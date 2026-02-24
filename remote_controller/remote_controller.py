#!/usr/bin/env python3

import sys
import os
import numpy as np

# ROS2 imports
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor

# Python imports
from ament_index_python.packages import get_package_share_directory

# ROS2 messages
from std_msgs.msg import Float64, String, Bool, Int32
from sensor_msgs.msg import BatteryState
# Assuming these message definitions were migrated to ROS2
from mr_interfaces.msg import Wind, Heading, Depth, Speed, GNSSData, ADCReading, RoboclawStatus
from mr_interfaces.msg import Temp, Pressure, Humidity, Declination, PID

# PyQt5 imports
from PyQt5 import QtGui, QtCore, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QTransform

from remote_controller import design

# from remote_controller.heading_manipulations import HeadingManipulations as HM
# from remote_controller.heading_manipulations import HeadingObj as HO

from movement_controls.heading_manipulations import HeadingManipulations as HM
from movement_controls.heading_manipulations import HeadingObj as HO

from collections import namedtuple
from math import cos, sin, radians

# Replace bondpy with ROS2 lifecycle node functionality
# This will be handled differently in ROS2

PKG = 'remote_controller'
NODE = 'send_key_cmd'

# Original design dimensions (from design.ui / design.py)
DESIGN_W = 1186
DESIGN_H = 946

PROP_SPEED = 1000
RUDDER_SPEED = 10
SAIL_SPEED = 100
COLOR_WARN = "rgb(252, 186, 3)"
COLOR_ERR = "rgb(186, 7, 7)"
COLOR_OK = "rgb(0, 150, 0)"


class myIntValidator(QtGui.QIntValidator):
    validationChanged = QtCore.pyqtSignal(QtGui.QValidator.State)

    def validate(self, input, pos):
        state, input, pos = super().validate(input, pos)
        # forward non int keypresses
        if state == QtGui.QValidator.Invalid:
            # We assume user tried to manually control boat if input was not an int
            # We then remove focus so their next keypress will register as intended
            try:
                if QtWidgets.QApplication.focusWidget() is not None:
                    QtWidgets.QApplication.focusWidget().clearFocus()
            except AttributeError as e:
                # TODO: Can we make this a ROS logger?
                print(f"Could not clear focus: {e}")
                pass
        self.validationChanged.emit(state)
        return state, input, pos


class Window(QtWidgets.QMainWindow, design.Ui_MainWindow):

    # Define signals, used to send data to ROS thread
    heading_signal        = pyqtSignal(int)
    sail_hdng_signal      = pyqtSignal(int)
    sail_angle_signal     = pyqtSignal(int)
    sail_pos_signal       = pyqtSignal(int)
    rudder_angle_signal   = pyqtSignal(int)
    rudder_signal         = pyqtSignal(int)
    sail_signal           = pyqtSignal(int)
    prop_signal           = pyqtSignal(int)
    gui_enable_signal     = pyqtSignal(bool)
    set_estop_signal      = pyqtSignal(bool)
    auto_sail_signal      = pyqtSignal(bool)
    keel_calibrate_signal = pyqtSignal(bool)
    keel_reset_signal     = pyqtSignal(bool)
    keel_setpoint_signal  = pyqtSignal(float)

    pid_gains_signal      = pyqtSignal(float, float, float)
    toggle_peripheral_signal = pyqtSignal(str)

    def __init__(self, parent=None, **kwargs):
        super(Window, self).__init__(parent, **kwargs)
        self.rosmaster_running = False
        self._thread = QThread()
        self._rosthread = RosThread()

        self._thread.started.connect(self._rosthread.start)
        self._rosthread.moveToThread(self._thread)
        qApp.aboutToQuit.connect(self._thread.quit)
        self.connect_slots()
        self.connect_thread_slots()
        self._thread.start()
        
        self.hm = HM()

        ####################
        # Status variables #
        ####################
        self.rudder_increment = 5
        self.desired_rudder = 0
        self.desired_sail = 0

        self.setupUi(self)
        # The design has no menu bar or status bar; hide them so that
        # centralwidget fills the full window and our scale calc is accurate.
        self.menuBar().hide()
        self.statusBar().hide()
        self._store_original_geometries()
        # Debounce timer for the expensive compass reconfigure on resize
        self._resize_timer = QtCore.QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(150)
        self._resize_timer.timeout.connect(self._reconfigure_compass_after_resize)
        self._scale_to_screen()
        self.home()

        self.ERRORS = {
            0x0000: ("ok", "Normal", COLOR_OK),
            0x0001: ("warn", "M1 over current", COLOR_WARN),
            0x0002: ("warn", "M2 over current", COLOR_WARN),
            0x0004: ("error", "Emergency Stop", COLOR_ERR),
            0x0008: ("error", "Temperature1", COLOR_ERR),
            0x0010: ("error", "Temperature2", COLOR_ERR),
            0x0020: ("error", "Main batt voltage high", COLOR_ERR),
            0x0040: ("error", "Logic batt voltage high", COLOR_ERR),
            0x0080: ("error", "Logic batt voltage low", COLOR_ERR),
            0x0100: ("warn", "M1 driver fault", COLOR_WARN),
            0x0200: ("warn", "M2 driver fault", COLOR_WARN),
            0x0400: ("warn", "Main batt voltage high", COLOR_WARN),
            0x0800: ("warn", "Main batt voltage low", COLOR_WARN),
            0x1000: ("warn", "Temperature1", COLOR_WARN),
            0x2000: ("warn", "Temperature2", COLOR_WARN),
            0x4000: ("ok", "M1 home", COLOR_OK),
            0x8000: ("ok", "M2 home", COLOR_OK)
        }

    def home(self):
        # Setup enable/disable buttons
        self.btnStartManual.clicked.connect(self.enable_manual)
        self.btnDisableManual.clicked.connect(self.disable_manual)
        self.btnDisableManual.hide()
        # Setup prop on/off buttons
        self.btnPropOn.hide()
        self.btnPropOff.hide()
        # Setup ESTOP buttons
        self.btnResetEStop.hide()
        self.btnResetEStop.clicked.connect(self.reset_estop)
        self.btnEStop.hide()
        self.btnEStop.clicked.connect(self.set_estop)
        # Setup auto sail buttons
        self.btnAutoSail.hide()
        self.btnAutoSailDisable.hide()
        self.btnPropOn.clicked.connect(self.start_prop)
        self.btnPropOff.clicked.connect(self.stop_prop)
        self.btnAutoSail.clicked.connect(self.start_auto_sail)
        self.btnAutoSailDisable.clicked.connect(self.stop_auto_sail)
        self.btnDesHeading.clicked.connect(self.set_heading)
        self.txtDesHeading.returnPressed.connect(self.set_heading)
        self.btnDesSail.clicked.connect(self.set_sail_heading)
        self.txtDesSail.returnPressed.connect(self.set_sail_heading)
        self.btnDesSailAngle.clicked.connect(self.set_sail_angle)
        self.txtDesSailAngle.returnPressed.connect(self.set_sail_angle)
        # Setup peripheral toggle buttons
        self.btnToggleMC.clicked.connect(self.toggle_mc)
        self.btnTogglePOE.clicked.connect(self.toggle_poe)
        self.btnToggleEthernet.clicked.connect(self.toggle_ethernet)
        self.btnToggleLTE.clicked.connect(self.toggle_lte)
        self.btnTogglePixhawk.clicked.connect(self.toggle_pixhawk)
        self.btnToggleRC.clicked.connect(self.toggle_rc)
        self.btnToggleN2K.clicked.connect(self.toggle_n2k)
        # Setup keel calibration button
        self.btnCalKeel.clicked.connect(self.calibrate_keel)
        # Setup keel reset button
        self.btnResetKeel.clicked.connect(self.reset_keel)
        # Setup keel setpoint slider
        self.sldrKeel.valueChanged.connect(self.set_keel_setpoint)

        #TEST
        self.btnDesSailPos.clicked.connect(self.set_sail_position)
        self.txtDesSailPos.returnPressed.connect(self.set_sail_position)

        #TODO
        self.btnSetIntegral.clicked.connect(self.set_pid_gains)
        self.btnDesRudderAngle.clicked.connect(self.set_rudder_angle)
        self.txtDesRudder.returnPressed.connect(self.set_rudder_angle)

        #############################
        # Setup text default values #
        #############################
        self.txtRudderIncrement.setValue(self.rudder_increment)

        ####################
        # Input Validation #
        ####################

        # Create int validator (will reject all non int input, and remove focus from field)
        self.onlyInt = myIntValidator()

        # Connect validator to input fields
        self.txtDesHeading.setValidator(self.onlyInt)
        self.txtDesSail.setValidator(self.onlyInt)
        self.txtDesSailAngle.setValidator(self.onlyInt)
        self.txtDesRudder.setValidator(self.onlyInt)
        self.txtDesSailPos.setValidator(self.onlyInt)

        ##################
        # Compass widget #
        ##################
        self.configure_compass()

        #####################
        # User clock widget #
        #####################
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayTime)
        self.timer.timeout.connect(self.check_connection_status)
        self.timer.start()

        #########
        # Start #
        #########
        self.show()

    def _store_original_geometries(self):
        """Snapshot every child widget's geometry (and font point size) right
        after setupUi(), before any scaling happens.  resizeEvent() always
        scales from these originals so floating-point error never accumulates
        across multiple resize operations."""
        self._orig_geoms = {}
        self._orig_font_sizes = {}
        self._collect_orig_geoms(self.centralwidget)

    def _collect_orig_geoms(self, widget):
        parent_name = widget.objectName()
        for child in widget.children():
            if not isinstance(child, QtWidgets.QWidget):
                continue
            name = child.objectName()
            # Snapshot only widgets that:
            #   1. Have an explicit objectName (set by setupUi)
            #   2. Are NOT Qt-internal widgets (names starting with "qt_")
            #   3. Have a parent that is also user-owned (not a Qt-internal
            #      layout container). Qt-internal containers such as the
            #      scroll-area viewport (empty name) and the tab-widget
            #      stacked widget ("qt_tabwidget_stackedwidget") own their
            #      direct children's geometry — calling setGeometry() on those
            #      children conflicts with Qt's layout and causes blank content.
            parent_is_user_owned = bool(parent_name) and not parent_name.startswith('qt_')
            # If a widget is managed by a Qt layout, let the layout control
            # child geometry on resize. Manual setGeometry() fights the layout
            # and can make controls collapse/disappear while shrinking.
            parent_widget = child.parentWidget()
            parent_has_layout = parent_widget is not None and parent_widget.layout() is not None
            if name and not name.startswith('qt_') and parent_is_user_owned and not parent_has_layout:
                self._orig_geoms[child] = QtCore.QRect(child.geometry())
                font = child.font()
                if font.pointSize() > 0:
                    self._orig_font_sizes[child] = font.pointSize()
            elif name and not name.startswith('qt_'):
                # Keep font scaling for layout-managed widgets even though
                # geometry is delegated to the layout.
                font = child.font()
                if font.pointSize() > 0:
                    self._orig_font_sizes[child] = font.pointSize()
            self._collect_orig_geoms(child)

    def resizeEvent(self, event):
        """Reflow the entire layout whenever the window is resized.

        Scale factor is always computed against the original design dimensions
        (DESIGN_W × DESIGN_H) so the result is correct regardless of how many
        times the window has been resized before.  The compass is re-configured
        on a short debounce timer because pixmap scaling is expensive.
        """
        super().resizeEvent(event)
        if not hasattr(self, '_orig_geoms'):
            return

        # Use centralwidget dimensions (window minus any chrome) so the design
        # dimensions map exactly to the available drawing area.
        scale = min(self.centralwidget.width() / DESIGN_W,
                    self.centralwidget.height() / DESIGN_H)

        # Skip when nothing meaningful changed (avoids redundant work on show)
        if abs(scale - getattr(self, '_last_scale', 0.0)) < 0.001:
            return
        self._last_scale = scale

        # configure_compass sets minimumSize on the compass labels; clear them
        # now or setGeometry() will be silently clamped to the old minimum.
        if hasattr(self, 'lblWind'):
            for lbl in [self.lblWind, self.lblBoat, self.lblSail,
                        self.lblSailDesired, self.lblRudder, self.lblRudderDesired]:
                lbl.setMinimumSize(0, 0)

        for widget, orig in self._orig_geoms.items():
            widget.setGeometry(
                int(orig.x() * scale),
                int(orig.y() * scale),
                int(orig.width() * scale),
                int(orig.height() * scale),
            )
        for widget, pt in self._orig_font_sizes.items():
            font = widget.font()
            font.setPointSize(max(6, int(pt * scale)))
            widget.setFont(font)

        # Debounce the compass reconfigure — pixmap scaling is expensive
        if hasattr(self, '_windPixOrig'):
            self._resize_timer.start()

        # Force a full repaint now that all widget geometries have been updated
        self.update()

    def _reconfigure_compass_after_resize(self):
        self.configure_compass()
        self.update()

    def _scale_to_screen(self):
        """Scale the window down at startup if the design size exceeds the
        available screen area.  resize() triggers resizeEvent() which handles
        the child-widget scaling; _collect_orig_geoms has already run so the
        original geometries are safe.  We also call the scaling directly in
        case resize() is async on this platform (common on X11)."""
        available = QtWidgets.QApplication.primaryScreen().availableGeometry()
        sx = available.width() / DESIGN_W
        sy = available.height() / DESIGN_H
        scale = min(sx, sy)

        if scale >= 1.0:
            return  # Window already fits — nothing to do

        self.resize(int(DESIGN_W * scale), int(DESIGN_H * scale))
        # Belt-and-suspenders: apply scaling directly in case the X11 resize
        # event hasn't fired yet when configure_compass() runs below.
        for widget, orig in self._orig_geoms.items():
            widget.setGeometry(
                int(orig.x() * scale),
                int(orig.y() * scale),
                int(orig.width() * scale),
                int(orig.height() * scale),
            )
        for widget, pt in self._orig_font_sizes.items():
            font = widget.font()
            font.setPointSize(max(6, int(pt * scale)))
            widget.setFont(font)

    def configure_compass(self):
        """
        This function takes the static wind, boat and sail labels from our design.py file, and prepares them to be
        rotated by incoming values. We:
        - Load the pixmap from the correct relative path
        - Resize the label so rotation happens correctly (cirlce image with square label can be weird otherwise)
        - Save important dimensions necessary for drawing moving labels
        """
        # Get the package share directory using ROS2's resource index
        package_share_dir = get_package_share_directory('remote_controller')  # Replace with your actual package name
        asset_path = os.path.join(package_share_dir, 'assets')
        
        # Print paths for debugging
        print(f"\033[95mPackage share directory: {package_share_dir}\033[0m")
        print(f"\033[95mAsset path: {asset_path}\033[0m")

        # Create text labels showing degrees (guard so re-calls don't duplicate them)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        if not hasattr(self, 'lblWindAngle'):
            self.lblWindAngle = QLabel(self.tabWidget.widget(0))
            self.lblWindAngle.setText("000")
            self.lblWindAngle.setFont(font)
        if not hasattr(self, 'lblSailAngle'):
            self.lblSailAngle = QLabel(self.tabWidget.widget(0))
            self.lblSailAngle.setText("000")
            self.lblSailAngle.setFont(font)

        # Load original (full-resolution) pixmaps from disk only once.
        # Subsequent calls (e.g. after a post-show rescale) reuse the originals
        # so the pixmaps are always scaled from lossless source data.
        if not hasattr(self, '_windPixOrig'):
            self._windPixOrig    = QPixmap(os.path.join(asset_path, 'compass.png'))
            self._boatPixOrig    = QPixmap(os.path.join(asset_path, 'boat.png'))
            self._sailPixOrig    = QPixmap(os.path.join(asset_path, 'sail.png'))
            self._desSailPixOrig = QPixmap(os.path.join(asset_path, 'sail_desired.png'))
            self._rudderPixOrig  = QPixmap(os.path.join(asset_path, 'rudder.png'))
            self._desRudderPixOrig = QPixmap(os.path.join(asset_path, 'rudder_desired.png'))

        # Scale pixmap to label size determined in design.py file
        self.windPix     = self._windPixOrig.scaled(self.lblWind.width(), self.lblWind.height())
        self.boatPix     = self._boatPixOrig.scaled(self.lblBoat.width(), self.lblBoat.height())
        self.sailPix     = self._sailPixOrig.scaled(self.lblSail.width(), self.lblSail.height())
        self.desSailPix  = self._desSailPixOrig.scaled(self.lblSailDesired.width(), self.lblSailDesired.height())
        self.rudderPix   = self._rudderPixOrig.scaled(self.lblRudder.width(), self.lblRudder.height())
        self.desRudderPix = self._desRudderPixOrig.scaled(self.lblRudderDesired.width(), self.lblRudderDesired.height())

        # Calculate pixmap diagonal for sizing (corner to corner of square label, even if pic is circle)
        self.windDiag = int((self.lblWind.width()**2 + self.lblWind.height()**2)**0.5)
        self.boatDiag = int((self.lblBoat.width()**2 + self.lblBoat.height()**2)**0.5)
        self.sailDiag = int((self.lblSail.width()**2 + self.lblSail.height()**2)**0.5)
        self.desSailDiag = int((self.lblSailDesired.width()**2 + self.lblSailDesired.height()**2)**0.5)
        self.rudderDiag = int((self.lblRudder.width()**2 + self.lblRudder.height()**2)**0.5)
        self.desRudderDiag = int((self.lblRudderDesired.width()**2 + self.lblRudderDesired.height()**2)**0.5)

        # Don't scale pixmap to label (we want label to be bigger to have enough room for rotation of square pixmap)
        self.lblWind.setScaledContents(False)
        self.lblBoat.setScaledContents(False)
        self.lblSail.setScaledContents(False)
        self.lblSailDesired.setScaledContents(False)
        self.lblRudder.setScaledContents(False)
        self.lblRudderDesired.setScaledContents(False)

        # Save label centers
        point: namedtuple = namedtuple('point', 'x y')  # namedtuple to save x, y coordinates
        self.lblWindCenter = point(int(self.lblWind.x() + self.lblWind.width()/2), int(self.lblWind.y() + self.lblWind.height()/2))
        self.lblBoatCenter = point(int(self.lblBoat.x() + self.lblBoat.width()/2), int(self.lblBoat.y() + self.lblBoat.height()/2))
        self.lblSailCenter = point(int(self.lblSail.x() + self.lblSail.width()/2), int(self.lblSail.y() + self.lblSail.height()/2))
        self.lblSailDesiredCenter = point(int(self.lblSailDesired.x() + self.lblSailDesired.width()/2), int(self.lblSailDesired.y() + self.lblSailDesired.height()/2))
        self.lblRudderCenter = point(int(self.lblRudder.x() + self.lblRudder.width()/2), int(self.lblRudder.y() + self.lblRudder.height()/2))
        self.lblRudderDesiredCenter = point(int(self.lblRudderDesired.x() + self.lblRudderDesired.width()/2), int(self.lblRudderDesired.y() + self.lblRudderDesired.height()/2))

        # Add pixmaps to labels
        self.lblWind.setPixmap(self.windPix)
        self.lblBoat.setPixmap(self.boatPix)
        self.lblSail.setPixmap(self.sailPix)
        self.lblSailDesired.setPixmap(self.desSailPix)
        self.lblRudder.setPixmap(self.rudderPix)
        self.lblRudderDesired.setPixmap(self.desRudderPix)

        # Align to center
        self.lblWind.setAlignment(QtCore.Qt.AlignCenter)
        self.lblBoat.setAlignment(QtCore.Qt.AlignCenter)
        self.lblSail.setAlignment(QtCore.Qt.AlignCenter)
        self.lblSailDesired.setAlignment(QtCore.Qt.AlignCenter)
        self.lblRudder.setAlignment(QtCore.Qt.AlignCenter)
        self.lblRudderDesired.setAlignment(QtCore.Qt.AlignCenter)

        # Set label size based off diagonal
        self.lblWind.setMinimumSize(self.windDiag, self.windDiag)
        self.lblBoat.setMinimumSize(self.boatDiag, self.boatDiag)
        self.lblSail.setMinimumSize(self.sailDiag, self.sailDiag)
        self.lblSailDesired.setMinimumSize(self.desSailDiag, self.desSailDiag)
        self.lblRudder.setMinimumSize(self.rudderDiag, self.rudderDiag)
        self.lblRudderDesired.setMinimumSize(self.desRudderDiag, self.desRudderDiag)

        # Reset label center, becuse resize will move them around
        self.lblWind.move(int(self.lblWindCenter.x - self.windDiag/2), int(self.lblWindCenter.y - self.windDiag/2))
        self.lblBoat.move(int(self.lblBoatCenter.x - self.boatDiag/2), int(self.lblBoatCenter.y - self.boatDiag/2))
        self.lblSail.move(int(self.lblSailCenter.x - self.sailDiag/2), int(self.lblSailCenter.y - self.sailDiag/2))
        self.lblSailDesired.move(int(self.lblSailDesiredCenter.x - self.desSailDiag/2), int(self.lblSailDesiredCenter.y - self.desSailDiag/2))
        self.lblRudder.move(int(self.lblRudderCenter.x - self.rudderDiag/2), int(self.lblRudderCenter.y - self.rudderDiag/2))
        self.lblRudderDesired.move(int(self.lblRudderDesiredCenter.x - self.desRudderDiag/2), int(self.lblRudderDesiredCenter.y - self.desRudderDiag/2))

        # Update center points after resizing
        self.lblWindCenter = point(self.lblWind.x() + self.lblWind.width()/2, self.lblWind.y() + self.lblWind.height()/2)
        self.lblBoatCenter = point(self.lblBoat.x() + self.lblBoat.width()/2, self.lblBoat.y() + self.lblBoat.height()/2)
        self.lblSailCenter = point(self.lblSail.x() + self.lblSail.width()/2, self.lblSail.y() + self.lblSail.height()/2)
        self.lblSailDesiredCenter = point(self.lblSailDesired.x() + self.lblSailDesired.width()/2, self.lblSailDesired.y() + self.lblSailDesired.height()/2)
        self.lblRudderCenter = point(self.lblRudder.x() + self.lblRudder.width()/2, self.lblRudder.y() + self.lblRudder.height()/2)
        self.lblRudderDesiredCenter = point(self.lblRudderDesired.x() + self.lblRudderDesired.width()/2, self.lblRudderDesired.y() + self.lblRudderDesired.height()/2)

        # Save label radius
        self.lblWindRadius = self.windDiag/2
        self.lblBoatRadius = self.boatDiag/2
        self.lblSailRadius = self.sailDiag/2
        self.lblSailDesiredRadius = self.desSailDiag/2
        self.lblRudderRadius = self.rudderDiag/2
        self.lblRudderDesiredRadius = self.desRudderDiag/2


        # Move text label to location
        # TODO: check if this actually does anything
        windGeo = self.lblWind.geometry()
        sailGeo = self.lblSail.geometry()

        # Create label moving functions, can be called when a value is received from a ROS subscriber
        self.moveWindLbl = self.getLableMover(self.windPix, self.lblWind, self.lblWindCenter, self.lblWindAngle, offset=10, scaler=0)
        self.moveSailLbl = self.getLableMover(self.sailPix, self.lblSail, self.lblSailCenter, self.lblSailAngle, offset=10, scaler=20)
        self.moveSailDesiredLbl = self.getLableMover(self.desSailPix, self.lblSailDesired, self.lblSailDesiredCenter, None, offset=10, scaler=20)
        self.moveRudderLbl = self.getLableMover(self.rudderPix, self.lblRudder, self.lblRudderCenter, None, offset=10, scaler=20, lateralMax=self.lblBoat.width()/8, angleMax=50)
        self.moveRudderDesiredLbl = self.getLableMover(self.desRudderPix, self.lblRudderDesired, self.lblRudderDesiredCenter, None, offset=10, scaler=20, lateralMax=self.lblBoat.width()/8, angleMax=50)

    def getLableMover(self, imgPixmap, imgLabel, imgLabelCenter, valueLabel=None, offset=10, scaler=10, lateralMax=0, angleMax=1):
        """
        Summary:
        Returns function to move a specific label around its axis together with its descriptive label

        In depth:
        We need multiple functions with identical calculations, but for different labels/pixmaps for our compass animation.
        To avoid rewriting these functions, this function is a template, and returns a function with the given
        labels and pixmaps "baked in"

        imgPixmap: pixmap loaded with png (generally smaller in dimensions than the label)
        imgLabel: QLabel with pixmap loaded into it, needed to apply rotated pixmap
        imgLabelCenter: named tuple (x,y) containing coordinates of label center
        valueLabel: text label containing the rotation value, floats next to rotating image
        Offset: y offset, useful because we rotate the top left corner of the lable, not the center
        Scaler: affects the radius of the circle made by the label.
        """
        def moveLabel(value):
            pixmap_rotated = imgPixmap.transformed(QTransform().rotate(value),QtCore.Qt.SmoothTransformation)  # Rotate pixmap same as value
            imgLabel.setPixmap(pixmap_rotated) # set rotated pixmap into QLabel

            # Move label on x axis based on angle/angleMax and lateralMax
            imgLateral = lateralMax * (value/angleMax)
            imgLabel.move(int(imgLabelCenter.x - imgLateral - imgLabel.width()/2), int(imgLabelCenter.y - imgLabel.height()/2))

            # Move label displaying text to follow along with rotating picture
            if valueLabel is not None:
                valueLabel.move(int((imgLabelCenter.x - valueLabel.width()/2) + ((imgPixmap.width()/2 + scaler) * sin(radians(value)))),
                                int(imgLabelCenter.y - ((imgPixmap.width()/2 + scaler) * cos(radians(value)) + offset)))
        return moveLabel

    def check_connection_status(self):
        """
        This method checks whether the ROS2 node is still running.
        In ROS2, we need a different approach to check connection.
        """
        # For ROS2, we might check if the node is still alive
        # This would be done in the RosThread class
        pass

    def displayTime(self):
        self.txtUTC.setText(
            QtCore.QDateTime.currentDateTime().toUTC().toString())

    def increment_rudder(self, position, increment):
        """
        Increment desired rudder position to the next increment value.
        Example: if current position is 12 and increment is 10, this function will output 10 instead of 12

        As a second feature this function caps the max value between -40 and 40
        """
        pos = position + (increment - (position % increment))
        return np.clip(pos, -40, 40)
    
    def increment_sail(self, position, increment):
        """
        Increment desired sail position to the next increment value.
        Example: if current position is 12 and increment is 10, this function will output 10 instead of 12

        As a second feature this function caps the max value between -160 and 160
        """
        pos = position + (increment - (position % increment))
        return np.clip(pos, -160, 160)

    @pyqtSlot(str)
    def myDebugFunc(self, cmd):
        pass

    def connect_slots(self):
        """Connect all signals needed to update the GUI from our ROS thread"""
        self._rosthread.sail_data_updated.connect(self.update_sail_data)
        self._rosthread.northref_data_updated.connect(self.update_northref_data)
        self._rosthread.vessel_heading_updated.connect(self.update_vessel_heading)
        self._rosthread.sail_heading_updated.connect(self.update_sail_heading)
        self._rosthread.water_depth_updated.connect(self.update_water_depth)
        self._rosthread.air_temp_updated.connect(self.update_air_temp)
        self._rosthread.water_temp_updated.connect(self.update_water_temp)
        self._rosthread.humidity_updated.connect(self.update_humidity)
        self._rosthread.air_pressure_updated.connect(self.update_air_pressure)
        self._rosthread.water_speed_updated.connect(self.update_water_speed)
        self._rosthread.gnss_data_updated.connect(self.update_gnss_data)
        self._rosthread.current_data_updated.connect(self.update_current_data)
        self._rosthread.volt_data_updated.connect(self.update_battery_voltage)
        self._rosthread.robo_status_updated.connect(self.update_roboclaw_status)
        self._rosthread.state_change_updated.connect(self.update_state_change)
        self._rosthread.substate_change_updated.connect(self.update_substate_change)
        self._rosthread.declination_updated.connect(self.update_declination)
        self._rosthread.sog_updated.connect(self.update_sog)
        self._rosthread.bat_level_updated.connect(self.update_bat_lvl)
        self._rosthread.power_consumption_updated.connect(self.update_power_consumption)
        # TEST
        self._rosthread.motor_current_updated.connect(self.update_motor_current)
        self._rosthread.rudder_angle_updated.connect(self.update_rudder_angle)
        #new
        self._rosthread.sail_angle_updated.connect(self.update_sail_angle)
        # peripheral signals
        self._rosthread.estop_state_updated.connect(self.update_estop_state)
        self._rosthread.mc_state_updated.connect(self.update_mc_state)
        self._rosthread.poe_state_updated.connect(self.update_poe_state)
        self._rosthread.ethernet_state_updated.connect(self.update_ethernet_state)
        self._rosthread.lte_state_updated.connect(self.update_lte_state)
        self._rosthread.pixhawk_state_updated.connect(self.update_pixhawk_state)
        self._rosthread.rc_state_updated.connect(self.update_rc_state)
        self._rosthread.n2k_state_updated.connect(self.update_n2k_state)

    def connect_thread_slots(self):
        """Connect slots in rosthread class to signals coming from this main class"""
        self.heading_signal.connect(self._rosthread.pub_boat_heading)
        self.sail_hdng_signal.connect(self._rosthread.pub_sail_heading)
        self.sail_angle_signal.connect(self._rosthread.pub_sail_angle)
        # connect rudder signal to 2 slots. One in rosthread, one in current thread just to update label
        self.rudder_angle_signal.connect(self._rosthread.pub_rudder_angle)
        self.rudder_angle_signal.connect(self.update_rudder_desired)
        self.prop_signal.connect(self._rosthread.pub_prop_effort)
        self.gui_enable_signal.connect(self._rosthread.pub_gui_enabled)
        #TODO: test new signals
        self.pid_gains_signal.connect(self._rosthread.pub_pid_gains)
        
        # estop signal
        self.set_estop_signal.connect(self._rosthread.pub_estop)
        
        # peripheral signal
        self.toggle_peripheral_signal.connect(self._rosthread.pub_peripheral_toggle)

        # keel calibration signal
        self.keel_calibrate_signal.connect(self._rosthread.pub_keel_calibrate)

        # keel reset signal
        self.keel_reset_signal.connect(self._rosthread.pub_keel_reset)

        # keel setpoint signal
        self.keel_setpoint_signal.connect(self._rosthread.pub_keel_setpoint)

        #TEST
        self.sail_pos_signal.connect(self._rosthread.pub_sail_position)
        self.sail_pos_signal.connect(self.update_sail_desired)
        self.auto_sail_signal.connect(self._rosthread.pub_auto_sail_enable)

    @pyqtSlot(float, float, str)
    def update_sail_data(self, speed, direction, reference):
        """Update GUI fields with provided data"""
        speed = speed*3.6  # convert to km/h
        if reference == "True (ground referenced to North)":
            self.txtWindTrue.setText("{0:.0f}".format(round(direction)))
            self.txtTrueWindSpeed.setText("{0:.2f}".format(round(speed, 2)))
        elif reference == "Apparent":
            self.txtWindApp.setText("{0:.0f}".format(round(direction)))
            self.txtApptWindSpeed.setText("{0:.2f}".format(round(speed, 2)))

    @pyqtSlot(float, float)
    def update_northref_data(self, apparent_wind_north, vessel_heading):
        apparent_wind_vessel = self.hm.diff(vessel_heading, apparent_wind_north)
        self.moveWindLbl(apparent_wind_vessel)
        self.lblWindAngle.setText(str(int(apparent_wind_north)))
        
    @pyqtSlot(int)
    def update_vessel_heading(self, heading):
        """Update GUI field with heading data"""
        self.txtHeading.setText(str(heading))

    @pyqtSlot(int)
    def update_sail_heading(self, heading):
        """Update GUI field with heading data"""
        self.lblSailAngle.setText(str(heading))

    @pyqtSlot(int)
    def update_sail_angle(self, angle):
        print(f"Updating sail angle labe and text to {angle}")
        self.moveSailLbl(angle)
        self.txtSailAngle.setText(str(angle))
        
    @pyqtSlot(bool)
    def update_estop_state(self, estop):
        # TODO: change this to rclpy logger
        if estop:
            self.update_ui_estop_enabled()
            self.txtEStopState.setText("E-Stop enabled")
            self.txtEStopState.setStyleSheet("background-color: rgb(150, 0, 0);color: rgb(255, 255, 255)")
        else:
            self.update_ui_estop_disabled()
            self.txtEStopState.setText("E-Stop disabled")
            self.txtEStopState.setStyleSheet("background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
            
    @pyqtSlot(bool)
    def update_mc_state(self, mc):
        if mc:
            self.txtMCState.setText("Motor Controller on")
            self.txtMCState.setStyleSheet("background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
        else:
            self.txtMCState.setText("Motor Controller off")
            self.txtMCState.setStyleSheet("background-color: rgb(150, 0, 0);color: rgb(255, 255, 255)")
    
    @pyqtSlot(bool)
    def update_poe_state(self, poe):
        if poe:
            self.txtPOEState.setText("POE on")
            self.txtPOEState.setStyleSheet("background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
        else:
            self.txtPOEState.setText("POE off")
            self.txtPOEState.setStyleSheet("background-color: rgb(150, 0, 0);color: rgb(255, 255, 255)")
            
    @pyqtSlot(bool)
    def update_ethernet_state(self, eth):
        if eth:
            self.txtEthernetState.setText("Ethernet on")
            self.txtEthernetState.setStyleSheet("background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
        else:
            self.txtEthernetState.setText("Ethernet off")
            self.txtEthernetState.setStyleSheet("background-color: rgb(150, 0, 0);color: rgb(255, 255, 255)")
    
    @pyqtSlot(bool)         
    def update_lte_state(self, lte):
        if lte:
            self.txtLTEState.setText("LTE on")
            self.txtLTEState.setStyleSheet("background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
        else:
            self.txtLTEState.setText("LTE off")
            self.txtLTEState.setStyleSheet("background-color: rgb(150, 0, 0);color: rgb(255, 255, 255)")
            
    @pyqtSlot(bool)
    def update_pixhawk_state(self, pixhawk):
        if pixhawk:
            self.txtPixhawkState.setText("Pixhawk on")
            self.txtPixhawkState.setStyleSheet("background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
        else:
            self.txtPixhawkState.setText("Pixhawk off")
            self.txtPixhawkState.setStyleSheet("background-color: rgb(150, 0, 0);color: rgb(255, 255, 255)")
            
    @pyqtSlot(bool)
    def update_rc_state(self, rc):
        if rc:
            self.txtRCState.setText("RC on")
            self.txtRCState.setStyleSheet("background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
        else:
            self.txtRCState.setText("RC off")
            self.txtRCState.setStyleSheet("background-color: rgb(150, 0, 0);color: rgb(255, 255, 255)")  
            
    @pyqtSlot(bool)
    def update_n2k_state(self, n2k):
        if n2k:
            self.txtN2KState.setText("N2K on")
            self.txtN2KState.setStyleSheet("background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
        else:
            self.txtN2KState.setText("N2K off")
            self.txtN2KState.setStyleSheet("background-color: rgb(150, 0, 0);color: rgb(255, 255, 255)")
 
    def update_ui_estop_enabled(self):
        # Disable all controls and make estop rest button visible
        self.btnEStop.hide()
        self.btnResetEStop.show()
    
    def update_ui_estop_disabled(self):
        self.btnEStop.show()
        self.btnResetEStop.hide()

    @pyqtSlot(float)
    def update_declination(self, declination):
        """Update GUI field with declination data"""
        self.txtDeclination.setText("{0:.2f}".format(round(declination, 1)))

    @pyqtSlot(float)
    def update_water_depth(self, depth):
        """Update GUI field with water depth and format float"""
        self.txtDepth.setText("{0:.2f}".format(round(depth, 2)))

    @pyqtSlot(float)
    def update_air_temp(self, temp):
        """Update GUI field with temperature and format float"""
        self.txtAirTemp.setText("{0:.2f}".format(round(temp, 2)))

    @pyqtSlot(float)
    def update_water_temp(self, temp):
        """Update GUI field with temperature and format float"""
        self.txtWaterTemp.setText("{0:.2f}".format(round(temp, 2)))

    @pyqtSlot(float)
    def update_humidity(self, humid):
        """Update GUI field with humidity and format float"""
        self.txtHumid.setText("{0:.2f}".format(round(humid, 2)))

    @pyqtSlot(float)
    def update_air_pressure(self, pressure):
        """Update GUI field with air pressure and format float"""
        self.txtPres.setText("{0:.2f}".format(round(pressure, 2)))

    @pyqtSlot(float)
    def update_water_speed(self, speed):
        """Update GUI field with water speed and format float"""
        speed_kph = speed * 3.6
        self.txtWaterSpeed.setText("{0:.2f}".format(round(speed_kph, 2)))

    @pyqtSlot(str)
    def update_state_change(self, state):
        """Update GUI field with boat state change"""
        self.txtState.setText(str(state))

    @pyqtSlot(str)
    def update_substate_change(self, substate):
        """Update GUI field with boat substate change"""
        self.txtSubstate.setText(str(substate))

    @pyqtSlot(int)
    def update_gnss_data(self, num_sats):
        """Update gui field with number of connected satellites"""
        self.txtNumSats.setText(str(num_sats))
        # make background green if 4 or more satellites are connected
        if num_sats >= 4:
            self.txtNumSats.setStyleSheet(
                "background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
        # make background red if less than 4 satellites are connected
        else:
            self.txtNumSats.setStyleSheet(
                "background-color: rgb(150, 0, 0);color: rgb(0, 0, 0)")

    @pyqtSlot(float)
    def update_sog(self, speed):
        speed_kph = speed * 3.6
        self.txtSOG.setText("{0:.2f}".format(round(speed_kph, 2)))

    @pyqtSlot(float)
    def update_current_data(self, current):
        self.txtCurrentDraw.setText("{0:.2f}".format(round(current, 2)))

    @pyqtSlot(float)
    def update_battery_voltage(self, voltage):
        self.txtBatVoltage.setText("{0:.2f}".format(round(voltage, 2)))

    @pyqtSlot(int, int, str)
    def update_roboclaw_status(self, address, status_id, status_msg):
        if address == 0x80:
            text_field = self.txt0x80Status
        elif address == 0x81:
            text_field = self.txt0x81Status
        text_field.setText("{}: {}".format(hex(address), status_msg))
        text_field.setStyleSheet("background-color: {}"
                                 .format(self.ERRORS[status_id][2]))

    @pyqtSlot(float)
    def update_bat_lvl(self, level):
        self.txtBatRemaining.setText("{0:.0f}".format(round(level)))

    @pyqtSlot(float)
    def update_power_consumption(self, power):
        self.txtPower.setText("{0:.2f}".format(round(power, 2)))

    @pyqtSlot(float)
    def update_motor_current(self, voltage):
        pass

    @pyqtSlot(float)
    def update_rudder_angle(self, angle):
        self.moveRudderLbl(-angle)
        self.txtRudderAngle.setText(str(angle))

    @pyqtSlot(int)
    def update_rudder_desired(self, angle):
        # Move desired rudder label when sent to ROS thread
        self.moveRudderDesiredLbl(-angle)
        
    @pyqtSlot(int)
    def update_sail_desired(self, angle):
        # Move desired sail label when sent to ROS thread
        self.moveSailDesiredLbl(angle)

    def set_heading(self):
        des_heading = int(self.txtDesHeading.text())
        self.heading_signal.emit(des_heading)

    def set_sail_heading(self):
        des_heading = int(self.txtDesSail.text())
        self.sail_hdng_signal.emit(des_heading)

    def set_sail_angle(self):
        des_angle = int(self.txtDesSailAngle.text())
        self.sail_angle_signal.emit(des_angle)

    def set_sail_position(self):        
        des_pos = int(self.txtDesSailPos.text())
        self.sail_pos_signal.emit(des_pos)

    def stop_all(self):
        self.rudder_signal.emit(0)
        self.sail_signal.emit(0)
        self.prop_signal.emit(0)

    def enable_manual(self):
        self.gui_enable_signal.emit(True)
        self.txtMode.setStyleSheet(
            "background-color: rgb(0, 150, 0);color: rgb(255, 255, 255)")
        self.txtMode.setText("MANUAL ENABLED")
        self.btnStartManual.hide()
        self.btnDisableManual.show()
        self.btnPropOn.show()
        self.btnAutoSail.show()
        self.controlFrame.setEnabled(True)

    def disable_manual(self):
        self.gui_enable_signal.emit(False)
        self.txtMode.setStyleSheet(
            "background-color: rgb(150, 0, 0);color: rgb(255, 255, 255)")
        self.txtMode.setText("MANUAL DISABLED")
        self.btnStartManual.show()
        self.btnDisableManual.hide()
        self.btnPropOn.hide()
        self.btnPropOff.hide()
        self.btnAutoSail.hide()
        self.btnAutoSailDisable.hide()
        self.controlFrame.setEnabled(False)
        self.auto_sail_signal.emit(False)
        
    def reset_estop(self):
        self.set_estop_signal.emit(False)
        
    def set_estop(self):
        self.set_estop_signal.emit(True)

    def start_prop(self):
        self.prop_signal.emit(-PROP_SPEED)
        self.btnPropOff.show()
        self.btnPropOn.hide()

    def stop_prop(self):
        self.prop_signal.emit(0)
        self.btnPropOn.show()
        self.btnPropOff.hide()

    def start_auto_sail(self):
        self.sail_angle_signal.emit(0)
        self.auto_sail_signal.emit(True)
        self.btnAutoSail.hide()
        sailGroup = self.sailCtrlGroup
        if sailGroup is not None:
            sailGroup.setEnabled(False)
        self.btnAutoSailDisable.show()

    def stop_auto_sail(self):
        self.auto_sail_signal.emit(False)
        self.sail_signal.emit(0)
        self.btnAutoSail.show()
        sailGroup = self.sailCtrlGroup
        if sailGroup is not None:
            sailGroup.setEnabled(True)
        self.btnAutoSailDisable.hide()
        
    def toggle_mc(self):
        self.toggle_peripheral_signal.emit("mc_relay_control")
        
    def toggle_poe(self):
        self.toggle_peripheral_signal.emit("poe_injector_relay_control")
        
    def toggle_ethernet(self):
        self.toggle_peripheral_signal.emit("ethernet_switch_relay_control")
    
    def toggle_lte(self):
        self.toggle_peripheral_signal.emit("lte_modem_relay_control")
        
    def toggle_pixhawk(self):
        self.toggle_peripheral_signal.emit("pixhawk_relay_control")
        
    def toggle_rc(self):
        pass
    
    def toggle_n2k(self):
        self.toggle_peripheral_signal.emit("n2k_network_relay_control")

    def calibrate_keel(self):
        """Trigger keel calibration by publishing True to /keel/calibrate"""
        self.keel_calibrate_signal.emit(True)

    def reset_keel(self):
        """Trigger keel reset by publishing True to /keel/reset"""
        self.keel_reset_signal.emit(True)

    def set_keel_setpoint(self, value):
        """Publish keel setpoint value from slider (-1000 to 1000) to /keel/setpoint"""
        self.keel_setpoint_signal.emit(float(value))

    def set_rudder_angle(self):
        des_rudder = int(self.txtDesRudder.text())
        self.rudder_angle_signal.emit(des_rudder)

    def keyPressEvent(self, event):
        # SPEED EVENTS
        if event.key() == QtCore.Qt.Key_W and not event.isAutoRepeat():
            self.prop_signal.emit(-PROP_SPEED)
        elif event.key() == QtCore.Qt.Key_S and not event.isAutoRepeat():
            self.prop_signal.emit(PROP_SPEED)

        # RUDDER EVENTS
        # TEST
        elif event.key() == QtCore.Qt.Key_D and not event.isAutoRepeat():
            self.desired_rudder = self.increment_rudder(self.desired_rudder, self.txtRudderIncrement.value())
            self.rudder_angle_signal.emit(self.desired_rudder)
        elif event.key() == QtCore.Qt.Key_A and not event.isAutoRepeat():
            self.desired_rudder = self.increment_rudder(self.desired_rudder, (self.txtRudderIncrement.value()*-1))
            self.rudder_angle_signal.emit(self.desired_rudder)

        # SAIL EVENTS
        elif event.key() == QtCore.Qt.Key_E and not event.isAutoRepeat():
            self.desired_sail = self.increment_sail(self.desired_sail, self.txtSailIncrement.value())
            self.sail_pos_signal.emit(self.desired_sail)
        elif event.key() == QtCore.Qt.Key_Q and not event.isAutoRepeat():
            self.desired_sail = self.increment_sail(self.desired_sail, (self.txtSailIncrement.value()*-1))
            self.sail_pos_signal.emit(self.desired_sail)

        event.accept()

    def keyReleaseEvent(self, event):
        # SPEED EVENTS
        if event.key() == QtCore.Qt.Key_W and not event.isAutoRepeat():
            self.stop_prop()
        elif event.key() == QtCore.Qt.Key_S and not event.isAutoRepeat():
            self.stop_prop()

        # RUDDER EVENTS
        elif event.key() == QtCore.Qt.Key_A and not event.isAutoRepeat():
            pass
        elif event.key() == QtCore.Qt.Key_D and not event.isAutoRepeat():
            pass

        # SAIL EVENTS
        elif event.key() == QtCore.Qt.Key_E and not event.isAutoRepeat():
            pass
        elif event.key() == QtCore.Qt.Key_Q and not event.isAutoRepeat():
            pass
        event.accept()

    def closeEvent(self, event):
        """Stop all motors on close"""
        self.prop_signal.emit(0)
        self.rudder_signal.emit(0)
        self.sail_signal.emit(0)
        
        #Clean shutdown of the node
        self._rosthread.stop()
        
        # Allow the base class to handle the rest
        super().closeEvent(event)

    def set_pid_gains(self):
        pid_p = int(self.txtPInput.text())
        pid_i = int(self.txtIInput.text())
        pid_d = int(self.txtDInput.text())
        self.pid_gains_signal.emit(pid_p, pid_i, pid_d)

class RemoteControlNode(Node):
    """
    A dedicated ROS2 Node class that handles all ROS2 specific functionality.
    """
    
    def __init__(self, callback_manager=None, **kwargs):
        """
        Initialize the ROS2 Node.
        
        Args:
            callback_manager: Reference to the RosThread object to emit signals back to Qt
            **kwargs: Additional arguments to pass to Node constructor
        """
        Node.__init__(self, "manual_control_node", **kwargs)
        
        self.get_logger().info("Initializing ROS2 Node")
        
        # Store callback_manager to emit signals back to Qt
        self.callback_manager = callback_manager
        
        # Initialize data variables
        self.last_current_update = self.get_clock().now().to_msg().sec
        self.last_volt_update = self.get_clock().now().to_msg().sec
        self.current_readings = []
        self.volt_readings = []

        self.vessel_heading = 0
        self.sail_heading = 0

        self.sail_angle = HO(20)
        self.apparent_wind_vessel = HO(20)  # Heading object with 20 value mean
        self.apparent_wind_sail = HO(20)
        self.apparent_wind_north = HO(20)  # apparent wind north referenced

        self.hm = HM()
        
        # Create QoS profiles
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # Define callback groups for concurrency management
        self.callback_group_subscribers = MutuallyExclusiveCallbackGroup()
        self.callback_group_publishers = MutuallyExclusiveCallbackGroup()
        
        # Initialize publishers
        self._init_publishers()
            
        # Create timer for periodic tasks
        self.timer = self.create_timer(1.0, self.timer_callback)
    
    def _init_publishers(self):
        """Initialize all ROS2 publishers"""
        self.prop_effort_pub = self.create_publisher(
            Float64, '/cmd/gui/prop_effort', 10)
        self.boat_heading_pub = self.create_publisher(
            Heading, '/cmd/gui/heading', 10)
        self.sail_heading_pub = self.create_publisher(
            Heading, '/cmd/gui/sail_heading', 10)
        self.sail_angle_pub = self.create_publisher(
            Heading, '/cmd/gui/sail_aoa', 10)
        self.sail_pos_pub = self.create_publisher(
            Float64, '/cmd/gui/sail_pos', 10)
        self.rudder_angle_pub = self.create_publisher(
            Float64, '/cmd/gui/rudder_pos', 10)
        self.gui_enabled_pub = self.create_publisher(
            Bool, '/cmd/gui/enabled', 10)
        self.autosail_enable_pub = self.create_publisher(
            Bool, 'cmd/gui/sail_autonomy_enabled', 10)
        self.pid_gains_pub = self.create_publisher(
            PID, 'cmd/gui/rudder_pid_gains', 10)
        self.peripheral_pub = self.create_publisher(
            String, '/set_peripheral', 10)
        self.peripheral_toggle_pub = self.create_publisher(
            String, '/toggle_peripheral_cmd', 10)
        self.keel_calibrate_pub = self.create_publisher(
            Bool, 'cmd/gui/keel_calibrate', 10)
        self.keel_reset_pub = self.create_publisher(
            Bool, 'cmd/gui/keel_reset', 10)
        self.keel_setpoint_pub = self.create_publisher(
            Float64, 'cmd/gui/keel_setpoint', 10)

    def init_subscribers(self):
        """Initialize all ROS2 subscribers"""
        self.get_logger().info("Initializing ROS2 subscriptions")
        
        # Create all subscribers with callbacks
        self.wind_sub = self.create_subscription(
            Wind, 'wind_info', self.handle_wind_info, 10, 
            callback_group=self.callback_group_subscribers)
            
        self.northref_sub = self.create_subscription(
            Wind, 'app_wind_northref_avg', self.handle_northref_info, 10,
            callback_group=self.callback_group_subscribers)
            
        self.vessel_heading_sub = self.create_subscription(
            Heading, 'vessel_hdng_true_cal', self.handle_vessel_heading, 10,
            callback_group=self.callback_group_subscribers)
            
        self.sail_heading_sub = self.create_subscription(
            Heading, 'sail_hdng_true_cal', self.handle_sail_heading, 10,
            callback_group=self.callback_group_subscribers)
            
        self.water_depth_sub = self.create_subscription(
            Depth, 'water_depth', self.handle_water_depth, 10,
            callback_group=self.callback_group_subscribers)
            
        self.air_temp_sub = self.create_subscription(
            Temp, '/air_temperature', self.handle_air_temp, 10,
            callback_group=self.callback_group_subscribers)
            
        self.water_temp_sub = self.create_subscription(
            Temp, '/water_temperature', self.handle_water_temp, 10,
            callback_group=self.callback_group_subscribers)
            
        self.humidity_sub = self.create_subscription(
            Humidity, 'humidity', self.handle_humidity, 10,
            callback_group=self.callback_group_subscribers)
            
        self.pressure_sub = self.create_subscription(
            Pressure, 'pressure', self.handle_air_pressure, 10,
            callback_group=self.callback_group_subscribers)
            
        self.water_speed_sub = self.create_subscription(
            Speed, 'water_speed', self.handle_water_speed, 10,
            callback_group=self.callback_group_subscribers)
            
        self.gnss_sub = self.create_subscription(
            GNSSData, 'gnss_position', self.handle_gnss, 10,
            callback_group=self.callback_group_subscribers)
            
        self.roboclaw_status_sub = self.create_subscription(
            RoboclawStatus, 'roboclaw_status', self.handle_roboclaw_status, 10,
            callback_group=self.callback_group_subscribers)
            
        self.state_change_sub = self.create_subscription(
            String, 'state_change', self.handle_state_change, 10,
            callback_group=self.callback_group_subscribers)
            
        self.substate_change_sub = self.create_subscription(
            String, 'substate_change', self.handle_substate_change, 10,
            callback_group=self.callback_group_subscribers)
            
        self.declination_sub = self.create_subscription(
            Declination, 'declination', self.handle_declination, 10,
            callback_group=self.callback_group_subscribers)
            
        self.sog_sub = self.create_subscription(
            Speed, '/sog', self.handle_sog, 10,
            callback_group=self.callback_group_subscribers)
            
        self.battery_state_sub = self.create_subscription(
            BatteryState, '/battery_state', self.handle_bat_state, 10,
            callback_group=self.callback_group_subscribers)
            
        self.rudder_current_sub = self.create_subscription(
            ADCReading, '/rudder_current', self.handle_motor_current, 10,
            callback_group=self.callback_group_subscribers)
            
        self.rudder_angle_sub = self.create_subscription(
            ADCReading, '/rudder/position', self.handle_rudder_angle, 10,
            callback_group=self.callback_group_subscribers)
            
        self.sail_position_sub = self.create_subscription(
            ADCReading, '/sail/position', self.handle_sail_angle, 10,
            callback_group=self.callback_group_subscribers)
            
        self.wind_avg_interval_sub = self.create_subscription(
            Int32, 'wind_avg_interval', self.handle_wind_interval, 10,
            callback_group=self.callback_group_subscribers)
            
        # Peripheral subscriptions
        self.estop_state_sub = self.create_subscription(
            Bool, 'estop_state', self.handle_estop_state, 10,
            callback_group=self.callback_group_subscribers)
            
        self.mc_feedback_sub = self.create_subscription(
            Bool, 'mc_relay_feedback', self.handle_mc_feedback, 10,
            callback_group=self.callback_group_subscribers)
            
        self.poe_feedback_sub = self.create_subscription(
            Bool, 'poe_injector_relay_feedback', self.handle_poe_feedback, 10,
            callback_group=self.callback_group_subscribers)
            
        self.ethernet_feedback_sub = self.create_subscription(
            Bool, 'ethernet_switch_relay_feedback', self.handle_ethernet_feedback, 10,
            callback_group=self.callback_group_subscribers)
            
        self.lte_feedback_sub = self.create_subscription(
            Bool, 'lte_modem_relay_feedback', self.handle_lte_feedback, 10,
            callback_group=self.callback_group_subscribers)
            
        self.pixhawk_feedback_sub = self.create_subscription(
            Bool, 'pixhawk_relay_feedback', self.handle_pixhawk_feedback, 10,
            callback_group=self.callback_group_subscribers)
            
        self.rc_feedback_sub = self.create_subscription(
            Bool, 'rc_control_active', self.handle_rc_feedback, 10,
            callback_group=self.callback_group_subscribers)
        
        self.n2k_feedback_sub = self.create_subscription(
            Bool, 'n2k_network_relay_feedback', self.handle_n2k_feedback, 10,
            callback_group=self.callback_group_subscribers)
            
        self.get_logger().info('All subscriptions created')
    
    def timer_callback(self):
        """Periodic checks and updates"""
        # Replace with ROS2 equivalent of checking connection status
        # For now, just assume connected
        pass
    
    #############################
    # Post processing functions #
    #############################

    def update_apparent_wind_vessel(self, app_wind_sail):
        self.apparent_wind_vessel.degrees = self.hm.add(self.sail_angle.degrees, app_wind_sail)

    def update_apparent_wind_north(self, app_wind_sail):
        self.apparent_wind_north.degrees = self.hm.add(self.sail_heading, app_wind_sail)
    
    #############################
    # Publisher methods         #
    #############################
    
    def publish_prop_effort(self, speed):
        msg = Float64()
        msg.data = float(speed)
        self.prop_effort_pub.publish(msg)
        self.get_logger().info(f"Published prop effort: {speed}")

    def publish_boat_heading(self, heading):
        msg = Heading()
        msg.heading = heading
        self.boat_heading_pub.publish(msg)
        self.get_logger().info(f"Published boat heading: {heading}")

    def publish_sail_heading(self, heading):
        msg = Heading()
        msg.heading = heading
        self.sail_heading_pub.publish(msg)
        self.get_logger().info(f"Published sail heading: {heading}")

    def publish_sail_angle(self, angle):
        msg = Heading()
        msg.heading = angle
        self.sail_angle_pub.publish(msg)
        self.get_logger().info(f"Published sail angle: {angle}")

    def publish_sail_position(self, pos):
        msg = Float64()
        msg.data = float(pos)
        self.sail_pos_pub.publish(msg)
        self.get_logger().info(f"Published sail position: {pos}")

    def publish_rudder_angle(self, angle):
        msg = Float64()
        msg.data = float(angle)
        self.rudder_angle_pub.publish(msg)
        self.get_logger().info(f"Published rudder angle: {angle}")

    def publish_auto_sail_enable(self, enable):
        msg = Bool()
        msg.data = enable
        self.autosail_enable_pub.publish(msg)
        self.get_logger().info(f"Published auto sail enable: {enable}")

    def publish_pid_gains(self, p, i, d):
        msg = PID()
        msg.p = float(p)
        msg.i = float(i)
        msg.d = float(d)
        self.pid_gains_pub.publish(msg)
        self.get_logger().info(f"Published PID gains: P={p}, I={i}, D={d}")

    def publish_gui_enable(self, cmd: bool):
        msg = Bool()
        msg.data = cmd
        self.gui_enabled_pub.publish(msg)
        self.get_logger().info(f"Published manual command: {cmd}")
        
    def publish_estop(self, enable):
        msg = String()
        if enable:
            # We need to send false to estop because of how peripheral manager works
            msg.data = "estop_set,false"
            self.get_logger().warn("ESTOP ENABLED")
        else:
            msg.data = "estop_reset,true"
            self.get_logger().warn("ESTOP DISABLED")
        self.peripheral_pub.publish(msg)
            
    def publish_peripheral_toggle(self, peripheral):
        msg = String()
        msg.data = peripheral
        self.peripheral_toggle_pub.publish(msg)
        self.get_logger().info(f"Toggling {peripheral}")

    def publish_keel_calibrate(self, calibrate):
        msg = Bool()
        msg.data = calibrate
        self.keel_calibrate_pub.publish(msg)
        self.get_logger().info(f"Publishing keel calibration: {calibrate}")

    def publish_keel_reset(self, reset):
        msg = Bool()
        msg.data = reset
        self.keel_reset_pub.publish(msg)
        self.get_logger().info(f"Publishing keel reset: {reset}")

    def publish_keel_setpoint(self, setpoint):
        msg = Float64()
        msg.data = setpoint
        self.keel_setpoint_pub.publish(msg)
        self.get_logger().info(f"Publishing keel setpoint: {setpoint}")

    #############################
    #         Handlers          #
    #############################

    def handle_wind_info(self, wind_info):
        # update wind relative to vessel if incoming is apparent
        if wind_info.reference == "Apparent":
            self.update_apparent_wind_vessel(wind_info.direction)
            self.update_apparent_wind_north(wind_info.direction)
        
        # Emit signal via callback manager to update Qt UI
        if self.callback_manager:
            self.callback_manager.sail_data_updated.emit(
                wind_info.speed, wind_info.direction, wind_info.reference)
                                    
    def handle_northref_info(self, wind_info):
        if self.callback_manager:
            self.callback_manager.northref_data_updated.emit(
                wind_info.direction, self.vessel_heading)

    def handle_vessel_heading(self, heading):
        # Save heading and calculate sail angle
        self.vessel_heading = heading.heading
        # log heading to console
        # self.get_logger().info(f"Vessel heading: {heading.heading}")
        
        if self.callback_manager:
            self.callback_manager.vessel_heading_updated.emit(heading.heading)

    def handle_sail_heading(self, heading):
        self.sail_heading = heading.heading
        
        if self.callback_manager:
            self.callback_manager.sail_heading_updated.emit(heading.heading)

    def handle_declination(self, decl_msg):
        if self.callback_manager:
            self.callback_manager.declination_updated.emit(decl_msg.declination)

    def handle_water_depth(self, depth):
        if self.callback_manager:
            self.callback_manager.water_depth_updated.emit(depth.depth)

    def handle_air_temp(self, temp):
        if self.callback_manager:
            self.callback_manager.air_temp_updated.emit(temp.temp)

    def handle_water_temp(self, temp):
        if self.callback_manager:
            self.callback_manager.water_temp_updated.emit(temp.temp)

    def handle_humidity(self, humid):
        if self.callback_manager:
            self.callback_manager.humidity_updated.emit(humid.humid)

    def handle_air_pressure(self, pressure):
        if self.callback_manager:
            self.callback_manager.air_pressure_updated.emit(pressure.pressure)

    def handle_water_speed(self, speed):
        if self.callback_manager:
            self.callback_manager.water_speed_updated.emit(speed.speed)

    def handle_state_change(self, state):
        if self.callback_manager:
            self.callback_manager.state_change_updated.emit(state.data)

    def handle_substate_change(self, substate):
        if self.callback_manager:
            self.callback_manager.substate_change_updated.emit(substate.data)

    def handle_gnss(self, gnss):
        if self.callback_manager:
            self.callback_manager.gnss_data_updated.emit(gnss.num_sats)

    def handle_sog(self, sog_msg):
        if self.callback_manager:
            self.callback_manager.sog_updated.emit(sog_msg.speed)

    def handle_current_draw(self, msg):
        self.current_readings.append(msg.value)
        # only update gui once a second
        current_time = self.get_clock().now().to_msg().sec
        if (current_time - self.last_current_update) > 1:
            curr_average = sum(self.current_readings) / len(self.current_readings)
            if self.callback_manager:
                self.callback_manager.current_data_updated.emit(curr_average)
            # clear list
            self.current_readings.clear()
            self.last_current_update = current_time

    def handle_battery_voltage(self, msg):
        self.volt_readings.append(msg.value)
        # only update gui once a second
        current_time = self.get_clock().now().to_msg().sec
        if (current_time - self.last_volt_update) > 1:
            volt_average = sum(self.volt_readings)/len(self.volt_readings)
            if self.callback_manager:
                self.callback_manager.volt_data_updated.emit(volt_average)
            # clear list
            self.volt_readings.clear()
            self.last_volt_update = current_time

    def handle_roboclaw_status(self, msg):
        if self.callback_manager:
            self.callback_manager.robo_status_updated.emit(
                msg.address, msg.status_id, msg.status_message)

    def handle_bat_level(self, msg):
        if self.callback_manager:
            self.callback_manager.bat_level_updated.emit(msg.value)
        
    def handle_bat_state(self, msg):
        level = msg.percentage
        voltage = msg.voltage
        current = msg.current
        # calculate power
        power = voltage * current
        
        if self.callback_manager:
            self.callback_manager.bat_level_updated.emit(level)
            self.callback_manager.volt_data_updated.emit(voltage)
            self.callback_manager.current_data_updated.emit(current)
            self.callback_manager.power_consumption_updated.emit(power)

    def handle_power_consumption(self, msg):
        if self.callback_manager:
            self.callback_manager.power_consumption_updated.emit(msg.value)

    def handle_wind_interval(self, msg):
        # Wind is output at 5hz, so divide by 5 for seconds
        interval = msg.data * 5
        self.sail_angle = HO(interval)
        self.apparent_wind_vessel = HO(interval)  # Heading object with interval value mean
        self.apparent_wind_sail = HO(interval)
        self.apparent_wind_north = HO(interval)  # apparent wind north referenced

    def handle_motor_current(self, msg):
        if self.callback_manager:
            self.callback_manager.motor_current_updated.emit(msg.value)

    def handle_rudder_angle(self, msg):
        angle = msg.value
        # Round angle to nearest degree
        angle = round(angle)
        if self.callback_manager:
            self.callback_manager.rudder_angle_updated.emit(angle)

    def handle_sail_angle(self, msg):
        angle = int(msg.value)
        self.sail_angle.degrees = angle
        print(f"Received sail angle update: {angle}")
        if self.callback_manager:
            self.callback_manager.sail_angle_updated.emit(angle)
        
    def handle_estop_state(self, msg):
        if self.callback_manager:
            self.callback_manager.estop_state_updated.emit(msg.data)
        
    def handle_mc_feedback(self, msg):
        if self.callback_manager:
            self.callback_manager.mc_state_updated.emit(msg.data)
        
    def handle_poe_feedback(self, msg):
        if self.callback_manager:
            self.callback_manager.poe_state_updated.emit(msg.data)
        
    def handle_ethernet_feedback(self, msg):
        if self.callback_manager:
            self.callback_manager.ethernet_state_updated.emit(msg.data)
        
    def handle_lte_feedback(self, msg):
        if self.callback_manager:
            self.callback_manager.lte_state_updated.emit(msg.data)
        
    def handle_pixhawk_feedback(self, msg):
        if self.callback_manager:
            self.callback_manager.pixhawk_state_updated.emit(msg.data)
        
    def handle_rc_feedback(self, msg):
        if self.callback_manager:
            self.callback_manager.rc_state_updated.emit(msg.data)
    
    def handle_n2k_feedback(self, msg):
        if self.callback_manager:
            self.callback_manager.n2k_state_updated.emit(msg.data)


class RosThread(QObject):
    """
    A QThread wrapper for ROS2 functionality.
    This class handles the QT signals and communicates with the ROS2 node.
    """
    
    # QT Signals for UI updates
    sail_data_updated = pyqtSignal(float, float, str)
    northref_data_updated = pyqtSignal(float, float)
    vessel_heading_updated = pyqtSignal(int)
    sail_heading_updated = pyqtSignal(int)
    sail_angle_updated = pyqtSignal(int)
    declination_updated = pyqtSignal(float)
    water_depth_updated = pyqtSignal(float)
    air_temp_updated = pyqtSignal(float)
    water_temp_updated = pyqtSignal(float)
    humidity_updated = pyqtSignal(float)
    air_pressure_updated = pyqtSignal(float)
    water_speed_updated = pyqtSignal(float)
    state_change_updated = pyqtSignal(str)
    substate_change_updated = pyqtSignal(str)
    gnss_data_updated = pyqtSignal(int)
    sog_updated = pyqtSignal(float)
    current_data_updated = pyqtSignal(float)
    volt_data_updated = pyqtSignal(float)
    robo_status_updated = pyqtSignal(int, int, str)
    bat_level_updated = pyqtSignal(float)
    power_consumption_updated = pyqtSignal(float)
    motor_current_updated = pyqtSignal(float)
    rudder_angle_updated = pyqtSignal(float)
    estop_state_updated = pyqtSignal(bool)
    mc_state_updated = pyqtSignal(bool)
    poe_state_updated = pyqtSignal(bool)
    ethernet_state_updated = pyqtSignal(bool)
    lte_state_updated = pyqtSignal(bool)
    pixhawk_state_updated = pyqtSignal(bool)
    rc_state_updated = pyqtSignal(bool)
    n2k_state_updated = pyqtSignal(bool)

    def __init__(self, parent=None, **kwargs):
        """
        Initialize RosThread.
        
        Args:
            parent: Parent QObject
            **kwargs: Additional arguments to pass to ROS2 Node constructor
        """
        QObject.__init__(self, parent)
        
        print("\033[95mInitializing ROS2 Thread\033[0m")
        
        # Store kwargs to pass to Node later
        self.kwargs = kwargs
        
        # Initialize ROS node but don't start it yet
        self.node = None
        self.timer = None
        
        self.vessel_heading = 0
        self.sail_heading = 0

    @pyqtSlot()
    def start(self):
        """Initialize ROS2 Node and start timer for spinning"""
        try:
            # Initialize ROS2 if not already done
            if not rclpy.ok():
                rclpy.init(args=None)
            
            # Create the node with a reference to self for callbacks
            self.node = RemoteControlNode(callback_manager=self, **self.kwargs)
            self.node.init_subscribers()
            
            print("\033[95mROS2 Node initialized, starting spin timer\033[0m")
            
            # Create QTimer to periodically process ROS callbacks
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.spin_once)
            self.timer.start(10)  # 10ms interval, adjust as needed
            
        except Exception as e:
            print(f"\033[91mError in ROS thread initialization: {e}\033[0m")
    
    def spin_once(self):
        """Process pending ROS callbacks"""
        if self.node and rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.001)
    
    def stop(self):
        """Stop the ROS2 node spinning"""
        if self.timer:
            self.timer.stop()
        
        if self.node:
            self.node.destroy_node()
            self.node = None
            
        # Only call shutdown if we're the last node
        if rclpy.ok():
            try:
                rclpy.shutdown()
            except Exception as e:
                print(f"\033[91mError shutting down rclpy: {e}\033[0m")

    #############################
    # Publisher methods - These are slots connected to signals from the Window class
    #############################

    @pyqtSlot(int)
    def pub_prop_effort(self, speed):
        if self.node:
            self.node.publish_prop_effort(speed)

    @pyqtSlot(int)
    def pub_boat_heading(self, heading):
        if self.node:
            self.node.publish_boat_heading(heading)

    @pyqtSlot(int)
    def pub_sail_heading(self, heading):
        if self.node:
            self.node.publish_sail_heading(heading)

    @pyqtSlot(int)
    def pub_sail_angle(self, angle):
        if self.node:
            self.node.publish_sail_angle(angle)

    @pyqtSlot(int)
    def pub_sail_position(self, pos):
        if self.node:
            self.node.publish_sail_position(pos)

    @pyqtSlot(int)
    def pub_rudder_angle(self, angle):
        if self.node:
            self.node.publish_rudder_angle(angle)

    @pyqtSlot(bool)
    def pub_auto_sail_enable(self, enable):
        if self.node:
            self.node.publish_auto_sail_enable(enable)

    @pyqtSlot(float, float, float)
    def pub_pid_gains(self, p, i, d):
        if self.node:
            self.node.publish_pid_gains(p, i, d)

    @pyqtSlot(bool)
    def pub_gui_enabled(self, cmd: bool):
        if self.node:
            self.node.publish_gui_enable(cmd)
        
    @pyqtSlot(bool)
    def pub_estop(self, enable):
        if self.node:
            self.node.publish_estop(enable)
            
    @pyqtSlot(str)
    def pub_peripheral_toggle(self, peripheral):
        if self.node:
            self.node.publish_peripheral_toggle(peripheral)

    @pyqtSlot(bool)
    def pub_keel_calibrate(self, calibrate):
        if self.node:
            self.node.publish_keel_calibrate(calibrate)

    @pyqtSlot(bool)
    def pub_keel_reset(self, reset):
        if self.node:
            self.node.publish_keel_reset(reset)

    @pyqtSlot(float)
    def pub_keel_setpoint(self, setpoint):
        if self.node:
            self.node.publish_keel_setpoint(setpoint)

def main(args=None):
    rclpy.init(args=args)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    
    # Create executor for ROS2 node
    executor = MultiThreadedExecutor()
    
    # Initialize window
    GUI = Window()
    
    # # Spin ROS2 node in separate thread
    # ros_spin_thread = threading.Thread(target=executor.spin)
    # ros_spin_thread.daemon = True
    # ros_spin_thread.start()
    
    # Run Qt application
    sys.exit(app.exec_())
    
    # Cleanup ROS2
    rclpy.shutdown()


if __name__ == '__main__':
    main()
