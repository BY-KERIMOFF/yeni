import json
import os
import requests
import time
from pathlib import Path
from datetime import datetime

def load_config(config_file="catcast-config.json"):
    """Load configuration from JSON file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_current_program(channel_id):
    """Send POST request to get current program information."""
    url = f"https://api.catcast.tv/api/channels/{channel_id}/getcurrentprogram"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
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

def extract_token_from_url(stream_url):
    """Extract token from full_mobile_url."""
    if not stream_url:
        return None
    if "token=" in stream_url:
        token_part = stream_url.split("token=")[1]
        token = token_part.split("&")[0]
        return token
    return None

def create_m3u8_file(slug, channel_id, token, output_dir="catcast"):
    """Create M3U8 playlist file - Catcast-in istədiyi formatda."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # ⭐ Catcast-in işlədiyi FORMAT (Sizin tapdığınız kimi) ⭐
    v2_url = f"https://v2.catcast.tv/content/{channel_id}/index.m3u8?token={token}"
    
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2000000
{v2_url}
"""
    
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    
    print(f"✓ Created: {output_file}")
    print(f"  └─ Token: {token[:20]}...")
    return output_file

def update_channel(channel):
    """Update single channel M3U8 file."""
    channel_id = channel.get("id")
    slug = channel.get("slug")
    
    if not channel_id or not slug:
        print(f"⚠️ Skipping: {channel}")
        return False
    
    print(f"\n📺 {slug} (ID: {channel_id}) - {datetime.now().strftime('%H:%M:%S')}")
    
    response_data = get_current_program(channel_id)
    
    if not response_data:
        print(f"❌ Failed: {slug}")
        return False
    
    if response_data.get("status") == 1 and "data" in response_data:
        data = response_data["data"]
        full_mobile_url = data.get("full_mobile_url") or data.get("full_hls_url")
        
        if full_mobile_url:
            token = extract_token_from_url(full_mobile_url)
            if token:
                create_m3u8_file(slug, channel_id, token)
                print(f"✅ Updated: {slug}")
                return True
            else:
                print(f"⚠️ No token found")
        else:
            print(f"⚠️ No stream URL")
    else:
        print(f"⚠️ Invalid response")
    
    return False

def main():
    """Auto-update mode - every 5 minutes."""
    
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        print("❌ catcast-config.json not found!")
        print("📝 Creating example...")
        example = [{"id": 50544, "slug": "mrbean"}]
        with open("catcast-config.json", 'w', encoding='utf-8') as f:
            json.dump(example, f, indent=2)
        print("✓ Created! Edit and run again.")
        return
    except json.JSONDecodeError:
        print("❌ Invalid JSON in catcast-config.json")
        return
    
    # Handle config format
    if isinstance(config, dict):
        channels = config.get("channels", [])
    else:
        channels = config
    
    UPDATE_INTERVAL = 300  # 5 dəqiqə
    
    print("="*50)
    print("🚀 Catcast Auto-Updater")
    print("="*50)
    print(f"📡 Channels: {len(channels)}")
    print(f"⏱️  Update interval: {UPDATE_INTERVAL} seconds (5 minutes)")
    print(f"📁 Output: catcast/*.m3u8")
    print("Press Ctrl+C to stop\n")
    
    def update_loop():
        while True:
            print("\n" + "="*50)
            print(f"🕐 Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
            
            success = 0
            for channel in channels:
                if update_channel(channel):
                    success += 1
                time.sleep(1)
            
            print(f"\n📊 Result: {success}/{len(channels)} updated")
            print(f"⏰ Next update in {UPDATE_INTERVAL//60} minutes\n")
            time.sleep(UPDATE_INTERVAL)
    
    try:
        update_loop()
    except KeyboardInterrupt:
        print("\n👋 Stopped!")

if __name__ == "__main__":
    main()
