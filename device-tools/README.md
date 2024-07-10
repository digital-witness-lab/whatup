## New device

1. Enable dev mode (about this phone -> tap on "build version" 5 times)
2. Enable USB debugging and optionally Wireless debugging (and turn off authentication timeout)
3. Connect to USB and ensure ADB connection using `adb devices`
4. If using wireless debugging, run command `adb tcpip 5555`
5. If using wireless debugging, ensure ability to connect with `adb connect <IP>:5555`. You can find the IP in the "About This Phone" settings page
6. Update config.yml:devices
