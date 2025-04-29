# Default values
$ROS_MASTER_URI="http://192.168.1.160:11311"
$ROS_IP = ""
$ROS_HOSTNAME = ""

# Parse command line arguments
for ($i = 0; $i -lt $args.Length; $i++) {
    switch ($args[$i]) {
        "-i" { $ROS_IP = $args[$i+1]; $i++ }
        "--host-ip" { $ROS_IP = $args[$i+1]; $i++ }
        "-m" { $ROS_MASTER_URI = $args[$i+1]; $i++ }
        "--master" { $ROS_MASTER_URI = $args[$i+1]; $i++ }
        "-h" { $ROS_HOSTNAME = $args[$i+1]; $i++ }
        "--hostname" { $ROS_HOSTNAME = $args[$i+1]; $i++ }
    }
}

if (!$ROS_HOSTNAME -and !$ROS_IP) {
    $ROS_HOSTNAME = [System.Net.Dns]::GetHostName()
}

# Set the environment variables
if ($ROS_IP) {
    [Environment]::SetEnvironmentVariable("ROS_IP", $ROS_IP, "Process")
}

if ($ROS_HOSTNAME) {
    [Environment]::SetEnvironmentVariable("ROS_HOSTNAME", $ROS_HOSTNAME, "Process")
}

[Environment]::SetEnvironmentVariable("ROS_MASTER_URI", $ROS_MASTER_URI, "Process")

# Echo out the values for verification
Write-Output "Remote Controller will start with the following values:"
Write-Output "ROS_IP: $ROS_IP"
Write-Output "ROS_HOSTNAME: $ROS_HOSTNAME"
Write-Output "ROS_MASTER_URI: $ROS_MASTER_URI"

# Ask enter to continue, or any other key to exit
$answer = Read-Host 'Press enter to continue, or any other key to exit'
if ($answer -ne '') { exit }

Write-Output "Starting Remote Controller..."

# Start docker compose
docker-compose -f .\docker-compose-windows.yml up
