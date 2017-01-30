#!/usr/bin/env python

import websocket
import thread
import time
import logging
import sys, getopt
import psutil

import json
from subprocess import Popen, PIPE

def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return output.replace("temp=", "")[0:4]

def get_cpu_usage():
    return psutil.cpu_percent()

def get_memory_usage():
    return psutil.virtual_memory().percent

def get_disk_usage():
    return psutil.disk_usage('/').percent

def get_network_speed(last_tot, interval, t0):
    counter = psutil.net_io_counters(pernic=True)['wlan0']
    t1 = time.time()
    tot = (counter.bytes_sent, counter.bytes_recv)
    ul, dl = [(now - last) / (t1 - t0) for now, last in zip(tot, last_tot)]
    t0 = time.time()
    return ul, dl, tot, t0

def msg_body_add_field(msg_body, field, value):
    if msg_body != "":
        msg_body += ","
    msg_body += "\"" + field + "\":" + value
    return msg_body

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
    logging.info(message)
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
        t0 = time.time()
        counter = psutil.net_io_counters(pernic=True)['wlan0']
        tot = (counter.bytes_sent, counter.bytes_recv)

        while True:
            time.sleep(interval)
            # Get temperature on Raspberry Pi
            upload, download, tot, t0 = get_network_speed(tot, interval, t0)
            cpu_temp = get_cpu_temperature()
            cpu_usage = get_cpu_usage()
            memory_usage = get_memory_usage()
            disk_usage = get_disk_usage()

            # Construct message type
            msg_type = "1"
            # Construct message ID
            msg_id = str(round(time.time())).rstrip('0').rstrip('.')

            # Construct message body
            msg_body = ""
            msg_body = msg_body_add_field(msg_body, "cpu_temperature", cpu_temp)
            msg_body = msg_body_add_field(msg_body, "cpu_usage", "%0.2f" % cpu_usage)
            msg_body = msg_body_add_field(msg_body, "memory_usage", "%0.2f" % memory_usage)
            msg_body = msg_body_add_field(msg_body, "disk_usage", "%0.2f" % disk_usage)
            msg_body = msg_body_add_field(msg_body, "upload_speed", "%d" % upload)
            msg_body = msg_body_add_field(msg_body, "download_speed", "%d" % download)
            msg_body = "{" + msg_body + "}"

            # Construct message
            msg = msg_type + "|" + msg_id + "|" + msg_body

            logging.info("sent: " + msg)
            ws.send(msg)
        ws.close()
        logging.info("Thread terminating...")

    thread.start_new_thread(run, ())

if __name__ == "__main__":
    global interval
    # For debug purpose
    # websocket.enableTrace(True)
    pf = ''
    cf = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:c:", ["profile=", "conf="])
    except getopt.GetoptError:
        print 'ws_client.py -p <profile.json> -c <config.json>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'ws_client.py -p <profile.json> -c <config.json>'
        elif opt in ("-p", "--profile"):
            pf = arg
        elif opt in ("-c", "--conf"):
            cf = arg

    with open(pf) as profile_file:
        profile = json.load(profile_file)
    with open(cf) as conf_file:
        conf = json.load(conf_file)

    logging.basicConfig(filename=conf["log_file"], format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    interval = conf["interval"];

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
