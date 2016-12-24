#!/usr/bin/env python

import websocket
import thread
import time

import json
from subprocess import check_output

def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_pong(ws, pong_message):
    print "pong: " + pong_message

def on_open(ws):
    def run():
        while True:
            # Get temperature on Raspberry Pi
            temperature = check_output(["/opt/vc/bin/vcgencmd", "measure_temp"]).replace("temp=", "")[0:4]

            # Construct message type
            msg_type = "1"
            # Construct message ID
            msg_id = str(round(time.time())).rstrip('0').rstrip('.')
            # Construct message body
            msg_body = "{\"temperature\":" + temperature + "}"
            # Construct message
            msg = msg_type + "|" + msg_id + "|" + msg_body

            print "send: " + msg
            #ws.send(msg)
            time.sleep(300)
        ws.close()
        print("Thread terminating...")

    thread.start_new_thread(run, ())

if __name__ == "__main__":
    # For debug purpose
    #websocket.enableTrace(True)
    with open('profile.json') as profile_file:
        profile = json.load(profile_file)

    # Construct url without tags
    url = "ws://" + profile["host"] + ":" + profile["port"] + "/channels/" + profile["channel"] + \
          "/devices/" + profile["device"] + "/ws?"

    # Append tags to url
    if "tags" in profile:
        for key, value in profile["tags"].items():
            url += key + "=" + value + "&"
    url = url.rstrip('&')

    ws = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open,
                              on_pong = on_pong,
                              header = {'AccessToken:1234abcd'})
    ws.run_forever(ping_interval=60)
