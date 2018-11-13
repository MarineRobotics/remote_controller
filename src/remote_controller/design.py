# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/remote_controller/design.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1143, 684)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.btnStartManual = QtGui.QPushButton(self.centralwidget)
        self.btnStartManual.setGeometry(QtCore.QRect(40, 80, 111, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnStartManual.setFont(font)
        self.btnStartManual.setObjectName(_fromUtf8("btnStartManual"))
        self.lblControl = QtGui.QLabel(self.centralwidget)
        self.lblControl.setGeometry(QtCore.QRect(40, 30, 111, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblControl.setFont(font)
        self.lblControl.setObjectName(_fromUtf8("lblControl"))
        self.btnStop = QtGui.QPushButton(self.centralwidget)
        self.btnStop.setEnabled(False)
        self.btnStop.setGeometry(QtCore.QRect(40, 620, 101, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.btnStop.setFont(font)
        self.btnStop.setStyleSheet(_fromUtf8("QPushButton {color: red;}\n"
""))
        self.btnStop.setObjectName(_fromUtf8("btnStop"))
        self.lblActuatorStatus_2 = QtGui.QLabel(self.centralwidget)
        self.lblActuatorStatus_2.setGeometry(QtCore.QRect(320, 30, 191, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblActuatorStatus_2.setFont(font)
        self.lblActuatorStatus_2.setObjectName(_fromUtf8("lblActuatorStatus_2"))
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(310, 90, 166, 100))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.txtHeading = QtGui.QLineEdit(self.frame)
        self.txtHeading.setEnabled(True)
        self.txtHeading.setGeometry(QtCore.QRect(90, 12, 61, 20))
        self.txtHeading.setReadOnly(True)
        self.txtHeading.setObjectName(_fromUtf8("txtHeading"))
        self.txtWaterSpeed = QtGui.QLineEdit(self.frame)
        self.txtWaterSpeed.setEnabled(True)
        self.txtWaterSpeed.setGeometry(QtCore.QRect(90, 40, 61, 20))
        self.txtWaterSpeed.setReadOnly(True)
        self.txtWaterSpeed.setObjectName(_fromUtf8("txtWaterSpeed"))
        self.txtSOG = QtGui.QLineEdit(self.frame)
        self.txtSOG.setEnabled(True)
        self.txtSOG.setGeometry(QtCore.QRect(90, 68, 61, 20))
        self.txtSOG.setReadOnly(True)
        self.txtSOG.setObjectName(_fromUtf8("txtSOG"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(12, 12, 71, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Monospace"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(2, 40, 81, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Monospace"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_6 = QtGui.QLabel(self.frame)
        self.label_6.setGeometry(QtCore.QRect(12, 68, 71, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Monospace"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.frame_2 = QtGui.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(310, 280, 166, 100))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.txtWindDir = QtGui.QLineEdit(self.frame_2)
        self.txtWindDir.setEnabled(False)
        self.txtWindDir.setGeometry(QtCore.QRect(90, 12, 61, 20))
        self.txtWindDir.setObjectName(_fromUtf8("txtWindDir"))
        self.txtWindSpeed = QtGui.QLineEdit(self.frame_2)
        self.txtWindSpeed.setEnabled(False)
        self.txtWindSpeed.setGeometry(QtCore.QRect(90, 40, 61, 20))
        self.txtWindSpeed.setObjectName(_fromUtf8("txtWindSpeed"))
        self.txtDepth = QtGui.QLineEdit(self.frame_2)
        self.txtDepth.setEnabled(False)
        self.txtDepth.setGeometry(QtCore.QRect(90, 68, 61, 20))
        self.txtDepth.setObjectName(_fromUtf8("txtDepth"))
        self.label_10 = QtGui.QLabel(self.frame_2)
        self.label_10.setGeometry(QtCore.QRect(12, 12, 71, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Monospace"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(self.frame_2)
        self.label_11.setGeometry(QtCore.QRect(2, 40, 81, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Monospace"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.label_12 = QtGui.QLabel(self.frame_2)
        self.label_12.setGeometry(QtCore.QRect(12, 68, 71, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Monospace"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.lblActuatorStatus_3 = QtGui.QLabel(self.centralwidget)
        self.lblActuatorStatus_3.setGeometry(QtCore.QRect(320, 230, 191, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblActuatorStatus_3.setFont(font)
        self.lblActuatorStatus_3.setObjectName(_fromUtf8("lblActuatorStatus_3"))
        self.lblActuatorStatus_4 = QtGui.QLabel(self.centralwidget)
        self.lblActuatorStatus_4.setGeometry(QtCore.QRect(570, 30, 191, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblActuatorStatus_4.setFont(font)
        self.lblActuatorStatus_4.setObjectName(_fromUtf8("lblActuatorStatus_4"))
        self.lblActuatorStatus_5 = QtGui.QLabel(self.centralwidget)
        self.lblActuatorStatus_5.setGeometry(QtCore.QRect(570, 230, 191, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblActuatorStatus_5.setFont(font)
        self.lblActuatorStatus_5.setObjectName(_fromUtf8("lblActuatorStatus_5"))
        self.frame_3 = QtGui.QFrame(self.centralwidget)
        self.frame_3.setGeometry(QtCore.QRect(570, 90, 166, 100))
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.txtBatVoltage = QtGui.QLineEdit(self.frame_3)
        self.txtBatVoltage.setEnabled(True)
        self.txtBatVoltage.setGeometry(QtCore.QRect(90, 12, 61, 20))
        self.txtBatVoltage.setReadOnly(True)
        self.txtBatVoltage.setObjectName(_fromUtf8("txtBatVoltage"))
        self.txtCurrentDraw = QtGui.QLineEdit(self.frame_3)
        self.txtCurrentDraw.setEnabled(True)
        self.txtCurrentDraw.setGeometry(QtCore.QRect(90, 40, 61, 20))
        self.txtCurrentDraw.setReadOnly(True)
        self.txtCurrentDraw.setObjectName(_fromUtf8("txtCurrentDraw"))
        self.label_13 = QtGui.QLabel(self.frame_3)
        self.label_13.setGeometry(QtCore.QRect(12, 12, 71, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Monospace"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_13.setFont(font)
        self.label_13.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.label_14 = QtGui.QLabel(self.frame_3)
        self.label_14.setGeometry(QtCore.QRect(2, 40, 81, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Monospace"))
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_14.setFont(font)
        self.label_14.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.btnDisableManual = QtGui.QPushButton(self.centralwidget)
        self.btnDisableManual.setGeometry(QtCore.QRect(40, 110, 111, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnDisableManual.setFont(font)
        self.btnDisableManual.setObjectName(_fromUtf8("btnDisableManual"))
        self.txtConnectionStatus = QtGui.QLineEdit(self.centralwidget)
        self.txtConnectionStatus.setGeometry(QtCore.QRect(570, 280, 201, 20))
        self.txtConnectionStatus.setAutoFillBackground(False)
        self.txtConnectionStatus.setStyleSheet(_fromUtf8("background-color: rgb(120, 0, 0);\n"
"align: center;"))
        self.txtConnectionStatus.setFrame(False)
        self.txtConnectionStatus.setReadOnly(True)
        self.txtConnectionStatus.setObjectName(_fromUtf8("txtConnectionStatus"))
        self.txtMode = QtGui.QLineEdit(self.centralwidget)
        self.txtMode.setGeometry(QtCore.QRect(570, 320, 201, 20))
        self.txtMode.setAutoFillBackground(False)
        self.txtMode.setStyleSheet(_fromUtf8("background-color: rgb(120, 0, 0);\n"
"align: center;"))
        self.txtMode.setFrame(False)
        self.txtMode.setReadOnly(True)
        self.txtMode.setObjectName(_fromUtf8("txtMode"))
        self.layoutWidget = QtGui.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(40, 240, 182, 201))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lblActuatorStatus = QtGui.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.lblActuatorStatus.setFont(font)
        self.lblActuatorStatus.setObjectName(_fromUtf8("lblActuatorStatus"))
        self.verticalLayout.addWidget(self.lblActuatorStatus)
        self.label_3 = QtGui.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.slidePropeller = QtGui.QSlider(self.layoutWidget)
        self.slidePropeller.setStyleSheet(_fromUtf8("QSlider::groove:horizontal {\n"
"border: 1px solid #bbb;\n"
"background: white;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #fff;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #eee, stop:1 #ccc);\n"
"border: 1px solid #777;\n"
"width: 13px;\n"
"margin-top: -2px;\n"
"margin-bottom: -2px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #fff, stop:1 #ddd);\n"
"border: 1px solid #444;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal:disabled {\n"
"background: #bbb;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal:disabled {\n"
"background: #eee;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:disabled {\n"
"background: #eee;\n"
"border: 1px solid #aaa;\n"
"border-radius: 4px;\n"
"}"))
        self.slidePropeller.setMinimum(-127)
        self.slidePropeller.setMaximum(127)
        self.slidePropeller.setProperty("value", 50)
        self.slidePropeller.setSliderPosition(50)
        self.slidePropeller.setOrientation(QtCore.Qt.Horizontal)
        self.slidePropeller.setInvertedAppearance(False)
        self.slidePropeller.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slidePropeller.setTickInterval(123)
        self.slidePropeller.setObjectName(_fromUtf8("slidePropeller"))
        self.verticalLayout.addWidget(self.slidePropeller)
        self.label_4 = QtGui.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.slideRudder = QtGui.QSlider(self.layoutWidget)
        self.slideRudder.setStyleSheet(_fromUtf8("QSlider::groove:horizontal {\n"
"border: 1px solid #bbb;\n"
"background: white;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #fff;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #eee, stop:1 #ccc);\n"
"border: 1px solid #777;\n"
"width: 13px;\n"
"margin-top: -2px;\n"
"margin-bottom: -2px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #fff, stop:1 #ddd);\n"
"border: 1px solid #444;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal:disabled {\n"
"background: #bbb;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal:disabled {\n"
"background: #eee;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:disabled {\n"
"background: #eee;\n"
"border: 1px solid #aaa;\n"
"border-radius: 4px;\n"
"}"))
        self.slideRudder.setMinimum(-127)
        self.slideRudder.setMaximum(127)
        self.slideRudder.setSliderPosition(0)
        self.slideRudder.setOrientation(QtCore.Qt.Horizontal)
        self.slideRudder.setInvertedAppearance(False)
        self.slideRudder.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slideRudder.setObjectName(_fromUtf8("slideRudder"))
        self.verticalLayout.addWidget(self.slideRudder)
        self.label_5 = QtGui.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Liberation Mono"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        self.slideSail = QtGui.QSlider(self.layoutWidget)
        self.slideSail.setStyleSheet(_fromUtf8("QSlider::groove:horizontal {\n"
"border: 1px solid #bbb;\n"
"background: white;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #fff;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #eee, stop:1 #ccc);\n"
"border: 1px solid #777;\n"
"width: 13px;\n"
"margin-top: -2px;\n"
"margin-bottom: -2px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #fff, stop:1 #ddd);\n"
"border: 1px solid #444;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal:disabled {\n"
"background: #bbb;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal:disabled {\n"
"background: #eee;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:disabled {\n"
"background: #eee;\n"
"border: 1px solid #aaa;\n"
"border-radius: 4px;\n"
"}"))
        self.slideSail.setMinimum(-127)
        self.slideSail.setMaximum(127)
        self.slideSail.setSliderPosition(0)
        self.slideSail.setOrientation(QtCore.Qt.Horizontal)
        self.slideSail.setInvertedAppearance(False)
        self.slideSail.setObjectName(_fromUtf8("slideSail"))
        self.verticalLayout.addWidget(self.slideSail)
        self.layoutWidget.raise_()
        self.btnStartManual.raise_()
        self.lblControl.raise_()
        self.btnStop.raise_()
        self.lblActuatorStatus_2.raise_()
        self.frame.raise_()
        self.frame_2.raise_()
        self.lblActuatorStatus_3.raise_()
        self.lblActuatorStatus_4.raise_()
        self.lblActuatorStatus_5.raise_()
        self.frame_3.raise_()
        self.btnDisableManual.raise_()
        self.txtConnectionStatus.raise_()
        self.txtMode.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.btnStartManual.setText(_translate("MainWindow", "Enable manual", None))
        self.lblControl.setText(_translate("MainWindow", "Control", None))
        self.btnStop.setText(_translate("MainWindow", "STOP", None))
        self.lblActuatorStatus_2.setText(_translate("MainWindow", "NAV Info", None))
        self.label.setText(_translate("MainWindow", "Heading:", None))
        self.label_2.setText(_translate("MainWindow", "Water speed:", None))
        self.label_6.setText(_translate("MainWindow", "SOG:", None))
        self.label_10.setText(_translate("MainWindow", "Wind dir:", None))
        self.label_11.setText(_translate("MainWindow", "Wind speed:", None))
        self.label_12.setText(_translate("MainWindow", "Depth:", None))
        self.lblActuatorStatus_3.setText(_translate("MainWindow", "Environment", None))
        self.lblActuatorStatus_4.setText(_translate("MainWindow", "Stats", None))
        self.lblActuatorStatus_5.setText(_translate("MainWindow", "Status", None))
        self.label_13.setText(_translate("MainWindow", "Bat Voltage", None))
        self.label_14.setText(_translate("MainWindow", "Current draw", None))
        self.btnDisableManual.setText(_translate("MainWindow", "Disable manual", None))
        self.txtConnectionStatus.setText(_translate("MainWindow", "DISCONNECTED", None))
        self.txtMode.setText(_translate("MainWindow", "MANUAL DISABLED", None))
        self.lblActuatorStatus.setText(_translate("MainWindow", "Actuator status", None))
        self.label_3.setText(_translate("MainWindow", "Propeller", None))
        self.label_4.setText(_translate("MainWindow", "Rudder", None))
        self.label_5.setText(_translate("MainWindow", "Sail", None))

