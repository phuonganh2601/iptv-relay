import json
import subprocess
import os
import time
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

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
        "-cenc_decryption_key", key,
        "-i", mpd,
        "-map", "0:v",
        "-map", "0:a",
        "-c", "copy",
        "-f", "hls",
        "-hls_time", "4",
        "-hls_list_size", "10",
        "-hls_flags", "delete_segments+append_list",
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


def http_server():

    os.chdir(HLS)

    server = ThreadingHTTPServer(("0.0.0.0", 8151), SimpleHTTPRequestHandler)

    print("HTTP server running on 8151")

    server.serve_forever()


def main():

    os.makedirs(HLS, exist_ok=True)

    threading.Thread(target=http_server, daemon=True).start()

    monitor()


if __name__ == "__main__":
    main()