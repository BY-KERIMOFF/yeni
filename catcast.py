import json
import os
import requests
import time
from pathlib import Path
from datetime import datetime

def load_config(config_file="catcast-config.json"):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_current_program(channel_id):
    url = f"https://api.catcast.tv/api/channels/{channel_id}/getcurrentprogram"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://catcast.tv/",
        "Origin": "https://catcast.tv"
    }
    try:
        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def extract_token(stream_url):
    if not stream_url:
        return None
    if "token=" in stream_url:
        token = stream_url.split("token=")[1].split("&")[0]
        return token
    return None

def create_m3u8_file(slug, channel_id, token, output_dir="catcast"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # ⭐ SİZİN TAPDIĞINIZ İŞLƏYƏN FORMAT ⭐
    v2_url = f"https://v2.catcast.tv/content/{channel_id}/index.m3u8?token={token}"
    
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2000000
{v2_url}
"""
    
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    
    print(f"✓ {output_file}")
    return output_file

def update_channel(channel):
    channel_id = channel.get("id")
    slug = channel.get("slug")
    
    if not channel_id or not slug:
        return False
    
    print(f"📺 {slug} - {datetime.now().strftime('%H:%M:%S')}")
    
    data = get_current_program(channel_id)
    if not data or data.get("status") != 1:
        print(f"  ❌ Failed")
        return False
    
    stream_url = data.get("data", {}).get("full_mobile_url") or data.get("data", {}).get("full_hls_url")
    if not stream_url:
        print(f"  ❌ No stream URL")
        return False
    
    token = extract_token(stream_url)
    if not token:
        print(f"  ❌ No token")
        return False
    
    create_m3u8_file(slug, channel_id, token)
    print(f"  ✅ Updated")
    return True

def main():
    try:
        config = load_config()
    except FileNotFoundError:
        print("❌ catcast-config.json tapılmadı!")
        example = [{"id": 50544, "slug": "mrbean"}]
        with open("catcast-config.json", "w") as f:
            json.dump(example, f, indent=2)
        print("✓ Nümunə fayl yaradıldı. Zəhmət olmasa redaktə edib təkrar işə salın.")
        return
    
    channels = config if isinstance(config, list) else config.get("channels", [])
    
    print("="*50)
    print("🚀 Catcast Auto-Updater")
    print(f"📡 {len(channels)} kanal")
    print("⏱️ Hər 5 dəqiqədə yenilənir")
    print("Press Ctrl+C to stop\n")
    
    while True:
        print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        success = 0
        for ch in channels:
            if update_channel(ch):
                success += 1
            time.sleep(1)
        print(f"📊 {success}/{len(channels)} yeniləndi")
        time.sleep(300)  # 5 dəqiqə

if __name__ == "__main__":
    main()
