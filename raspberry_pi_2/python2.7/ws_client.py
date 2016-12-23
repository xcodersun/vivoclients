#!/usr/bin/env python

import websocket
import thread
import time

def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_pong(ws, pong_message):
    print pong_message

def on_open(ws):
    print "### opened ###"

if __name__ == "__main__":
    # For debug purpose
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://192.168.31.132:8081/channels/dNPbBY7op5zxqLen/devices/raspberrypi/ws?root=guest",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open,
                              on_pong = on_pong,
                              header = {'AccessToken:1234abcd'})
    ws.run_forever(ping_interval=2)
