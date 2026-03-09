import json
import subprocess
import os
import time
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

CONFIG = "/config/channels.json"
HLS_DIR = "/hls"

processes = {}


def start_channel(ch):

    name = ch["name"]
    mpd = ch["mpd"]
    key = ch["key"]
    keyId = ch["keyId"]

    outdir = f"{HLS_DIR}/{name}"
    os.makedirs(outdir, exist_ok=True)

    cmd = [
        "packager",
        f"in={mpd},stream=video,init_segment={outdir}/video_init.mp4,segment_template={outdir}/video_$Number$.m4s",
        f"in={mpd},stream=audio,init_segment={outdir}/audio_init.mp4,segment_template={outdir}/audio_$Number$.m4s",
        "--enable_raw_key_decryption",
        "--keys", f"key_id={keyId}:key={key}",
        "--hls_master_playlist_output", f"{outdir}/index.m3u8"
    ]

    print("Starting channel:", name)

    p = subprocess.Popen(cmd)

    processes[name] = p


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

        time.sleep(10)


def http_server():

    os.chdir(HLS_DIR)

    server = ThreadingHTTPServer(("0.0.0.0", 8151), SimpleHTTPRequestHandler)

    print("HTTP server started on 8151")

    server.serve_forever()


def main():

    threading.Thread(target=http_server, daemon=True).start()

    monitor()


if __name__ == "__main__":
    main()