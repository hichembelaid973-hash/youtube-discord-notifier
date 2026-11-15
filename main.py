
import os
import json
import feedparser
import requests
from pathlib import Path

CONFIG_FILE = Path("channels.json")
STATE_FILE = Path("state.json")

def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

def save_json(path, data):
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def main():
    channels = load_json(CONFIG_FILE, [])
    state = load_json(STATE_FILE, {})

    for channel in channels:
        channel_id = channel["channel_id"]
        webhook_name = channel["webhook_env"]

        webhook_url = os.getenv(webhook_name)

        if not webhook_url:
            print(f"Missing webhook: {webhook_name}")
            continue

        feed_url = (
            "https://www.youtube.com/feeds/videos.xml"
            f"?channel_id={channel_id}"
        )

        feed = feedparser.parse(feed_url)

        for video in reversed(feed.entries):
            video_id = video.get("yt_videoid")

            if not video_id:
                continue

            key = f"{channel_id}:{video_id}"

            if key in state:
                continue

            payload = {
                "embeds": [{
                    "title": video.get("title", "New video"),
                    "url": video.get("link"),
                    "description": "A new video has been published!",
                    "color": 16711680
                }]
            }

            response = requests.post(
                webhook_url,
                json=payload,
                timeout=20
            )
            response.raise_for_status()

            state[key] = True
            print(f"Published: {video.get('title')}")

    save_json(STATE_FILE, state)

if __name__ == "__main__":
    main()
