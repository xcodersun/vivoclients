#!/usr/bin/env python

import websocket
import thread
import time
import logging

import json
from subprocess import check_output

def proc_send_msg(ws, msg_id, msg_body):
    logging.debug("Nothing to do with \"" + msg_body + "\"")

def proc_request_msg(ws, msg_id, msg_body):
    def run():
        # Construct message type
        msg_type = "4"
        # Construct message
        msg = msg_type + "|" + msg_id + "|" + msg_body
        ws.send(msg)
        logging.info("responded: " + msg)

    thread.start_new_thread(run, ())

def on_message(ws, message):
    print message
    msg = message.split('|', 3)
    msg_type = msg[0]
    msg_id = msg[1]
    msg_body = msg[2]

    if msg_type == "3":
        proc_send_msg(ws, msg_id, msg_body)
    elif msg_type == "2":
        proc_request_msg(ws, msg_id, msg_body)
    else:
        logging.warning("Ivalid Message")

def on_error(ws, error):
    logging.error(error)

def on_close(ws):
    logging.info("### closed ###")

def on_pong(ws, pong_message):
    logging.debug("pong: " + pong_message)

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

            logging.info("sent: " + msg)
            ws.send(msg)
            time.sleep(10)
        ws.close()
        logging.info("Thread terminating...")

    thread.start_new_thread(run, ())

if __name__ == "__main__":
    # For debug purpose
    # websocket.enableTrace(True)
    with open('profile.json') as profile_file:
        profile = json.load(profile_file)
    with open('config.json') as conf_file:
        conf = json.load(conf_file)

    logging.basicConfig(filename=conf["log_file"], format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

    # Construct url without tags
    url = "ws://" + profile["host"] + ":" + profile["port"] + "/channels/" + profile["channel"] + \
          "/devices/" + profile["device"] + "/ws?"

    # Append tags to url
    if "tags" in profile:
        for key, value in profile["tags"].items():
            url += key + "=" + value + "&"
    url = url.rstrip('&')
    accessToken = "AccessToken:" + profile["access_token"]

    ws = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open,
                              on_pong = on_pong,
                              header = {accessToken})
    ws.run_forever(ping_interval=120)
