# vivoclients
Client code for connecting eywa

## Raspberry Pi 2
When you get a new Raspberry Pi 2 board, you need to do:
1. Update your apt-get utility: `sudo apt-get update`
2. Install your favorite editor: `sudo apt-get install vim`
3. Install websocket clinet: `sudo pip install websocket-client`
4. Edit raspberry_pi_2/python2.7/profile.json file to configure your connection to eywa
5. Run `python ws_client.py` under raspberry_pi_2/python2.7/ directory
