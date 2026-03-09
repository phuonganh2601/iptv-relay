import json
import subprocess
import os
import time

CONFIG = "/config/channels.json"
HLS = "/hls"

processes = {}
config_mtime = 0
channels_cache = []


def start_channel(ch):

    name = ch["name"]
    mpd = ch["mpd"]
    key = ch["key"]

    outdir = f"{HLS}/{name}"
    os.makedirs(outdir, exist_ok=True)

    playlist = f"{outdir}/index.m3u8"

    cmd = [
        "ffmpeg",
        "-loglevel", "error",

        "-fflags", "nobuffer",
        "-flags", "low_delay",

        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",

        "-cenc_decryption_key", key,

        "-i", mpd,

        "-map", "0:v",
        "-map", "0:a",

        "-c", "copy",

        "-f", "hls",
        "-hls_time", "2",
        "-hls_list_size", "6",
        "-hls_flags", "delete_segments+append_list+omit_endlist",

        playlist
    ]

    print("Start:", name)

    p = subprocess.Popen(cmd)

    processes[name] = p


def stop_channel(name):

    p = processes.get(name)

    if p:
        print("Stop:", name)
        p.kill()
        processes.pop(name, None)


def load_config():

    global config_mtime
    global channels_cache

    try:
        mtime = os.path.getmtime(CONFIG)
    except:
        return

    if mtime == config_mtime:
        return

    config_mtime = mtime

    with open(CONFIG) as f:
        channels = json.load(f)

    print("Reload config")

    names = {c["name"] for c in channels}

    for name in list(processes.keys()):
        if name not in names:
            stop_channel(name)

    channels_cache = channels


def monitor():

    while True:

        load_config()

        for ch in channels_cache:

            name = ch["name"]
            p = processes.get(name)

            if p is None or p.poll() is not None:
                start_channel(ch)

        time.sleep(5)


if __name__ == "__main__":

    os.makedirs(HLS, exist_ok=True)

    monitor()