import json
import subprocess
import time
import os

CONFIG = "/config/channels.json"

processes = {}

def start_channel(ch):

    name = ch["name"]
    mpd = ch["mpd"]
    key = ch["key"]

    rtmp = f"rtmp://127.0.0.1/live/{name}"

    cmd = [
        "ffmpeg",
        "-loglevel","error",

        "-reconnect","1",
        "-reconnect_streamed","1",
        "-reconnect_delay_max","5",

        "-cenc_decryption_key", key,

        "-i", mpd,

        "-map","0:v",
        "-map","0:a",

        "-c","copy",
        "-f","flv",

        rtmp
    ]

    print("Start:", name)

    processes[name] = subprocess.Popen(cmd)


def monitor():

    while True:

        try:
            with open(CONFIG) as f:
                channels = json.load(f)
        except:
            time.sleep(5)
            continue

        for ch in channels:

            name = ch["name"]

            p = processes.get(name)

            if p is None or p.poll() is not None:
                start_channel(ch)

        time.sleep(5)


if __name__ == "__main__":

    monitor()