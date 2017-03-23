# vivoclients
Client code for connecting eywa

## Raspberry Pi 2
When you get a new Raspberry Pi 2 board, you need to do:
1. Update your apt-get utility: `sudo apt-get update`
2. Install your favorite editor: `sudo apt-get install vim`
3. Install websocket clinet: `sudo pip install websocket-client`
4. Edit raspberry_pi_2/python2.7/profile.json file to configure your connection to eywa
5. Run `python ws_client.py` under raspberry_pi_2/python2.7/ directory

## Configure systemd to keep the service running
1. copy following script to /lib/systemd/system/ws_client.service

[Unit]
Description=websocket client for eywa
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python /home/pi/github.com/xcodersun/vivoclients/raspberry_pi_2/python2.7/ws_client.py -p /home/pi/github.com/xcodersun/vivoclients/raspberry_pi_2/python2.7/profile/example.json -c /home/pi/github.com/xcodersun/vivoclients/raspberry_pi_2/python2.7/config/example.json
Restart=on-success
RestartSec=300

[Install]
WantedBy=multi-user.target

2. run following commands
chmod +x /home/pi/github.com/xcodersun/vivoclients/raspberry_pi_2/python2.7/ws_client.py
sudo systemctl daemon-reload
sudo systemctl enable ws_client.service (Configure it to be automatically started at boot time)
sudo systemctl start ws_client.service (Start service)

3. check the status
sudo systemctl status ws_client.service
