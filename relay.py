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
    keyId = ch["keyId"]

    outdir = f"{HLS}/{name}"
    os.makedirs(outdir, exist_ok=True)

    cmd = [
        "packager",
        f"in={mpd},stream=video,init_segment={outdir}/video_init.mp4,segment_template={outdir}/video_$Number$.m4s",
        f"in={mpd},stream=audio,init_segment={outdir}/audio_init.mp4,segment_template={outdir}/audio_$Number$.m4s",
        "--enable_raw_key_decryption",
        "--keys", f"key_id={keyId}:key={key}",
        "--hls_master_playlist_output", f"{outdir}/index.m3u8"
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

    server.serve_forever()


def main():

    os.makedirs(HLS, exist_ok=True)

    threading.Thread(target=http_server, daemon=True).start()

    monitor()


if __name__ == "__main__":
    main()