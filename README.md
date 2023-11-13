# fisherman

Fisherman is meant to be a locally hosted Django app on a Raspberry Pi to control fish tank systems on large scales.

# Connecting to a Raspberry Pi via VNC

## Prerequisites
- Ensure VNC Server is installed and running on your Raspberry Pi.
  - `vncserver`
- Know the Raspberry Pi's IP address.
  - `hostname -I`
- Have VNC Viewer installed on your computer.
  - See https://www.realvnc.com for information on VNC.

## Steps to Connect

1. **Open VNC Viewer on your Computer**
   Launch the VNC Viewer application.

2. **Connect to your Raspberry Pi**
   - In the VNC Viewer address bar, enter the IP address of your Raspberry Pi.
   - Press `Enter` to initiate the connection.

3. **Authenticate**
   - When prompted, enter the username and password for your Raspberry Pi.
   - The default credentials are (unless you have changed them):
     - **Username:** pi
     - **Password:** raspberry

4. **Start Using the Raspberry Pi's Desktop**
   Once connected, you should see the Raspberry Pi's desktop environment. You can now use your Raspberry Pi as if you were directly using it with a keyboard and mouse connected.

## Tips for a Better Experience
- **Set a VNC Password:** For additional security, set a password for VNC connections if you haven't already done so via the `vncpasswd` command on your Raspberry Pi.
- **Adjust Quality Settings:** If the connection is slow, adjust the quality settings in VNC Viewer to favor speed over quality.
- **Troubleshooting:** If you cannot connect, make sure your Raspberry Pi and your computer are on the same network and that the correct IP address is used.

Remember to safely shutdown your Raspberry Pi before disconnecting to prevent data loss.

# Clone and Update the Project on the Pi

Clone the repository 
```python
git clone https://github.com/qwage/fisherman.git
```

Update the repository
```python
git pull origin main
```

# Activate venv on Pi

```
cd /home/fisherman/.virtualenvs
```

```
source fisherman/bin/activate 
```

```
pip3 install xyz
```
