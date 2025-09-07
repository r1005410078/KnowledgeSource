[Malware Blocked. “com.docker.socket” was not opened because it contains malware. this action did not harm your Mac.](https://github.com/docker/for-mac/issues/7520)

![[Pasted image 20250907102833.png|300x200]]

```bash
#!/bin/bash

# Stop the docker services
echo "Stopping Docker..."
sudo pkill '[dD]ocker'

# Stop the vmnetd service
echo "Stopping com.docker.vmnetd service..."
sudo launchctl bootout system /Library/LaunchDaemons/com.docker.vmnetd.plist

# Stop the socket service
echo "Stopping com.docker.socket service..."
sudo launchctl bootout system /Library/LaunchDaemons/com.docker.socket.plist

# Remove vmnetd binary
echo "Removing com.docker.vmnetd binary..."
sudo rm -f /Library/PrivilegedHelperTools/com.docker.vmnetd

# Remove socket binary
echo "Removing com.docker.socket binary..."
sudo rm -f /Library/PrivilegedHelperTools/com.docker.socket

# Install new binaries
echo "Install new binaries..."
sudo cp /Applications/Docker.app/Contents/Library/LaunchServices/com.docker.vmnetd /Library/PrivilegedHelperTools/
sudo cp /Applications/Docker.app/Contents/MacOS/com.docker.socket /Library/PrivilegedHelperTools/
```