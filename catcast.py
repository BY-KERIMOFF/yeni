import json
import os
import requests
from pathlib import Path

def load_config(config_file="catcast-config.json"):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_current_program(channel_id, token=None):
    url = f"https://api.catcast.tv/api/channels/{channel_id}/getcurrentprogram"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr,en-US;q=0.9,en;q=0.8",
        "Referer": "https://catcast.tv/",
        "Origin": "https://catcast.tv",
        "Content-Type": "application/json"
    }
    
    # Token varsa əlavə et
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.post(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Xəta {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Bağlantı xətası: {e}")
        return None

def create_m3u8_file(slug, stream_url, output_dir="catcast"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    
    # Düzgün M3U8 formatı (canlı yayım üçün)
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
{stream_url}
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    
    print(f"✓ Yaradıldı: {output_file}")
    return output_file

def delete_m3u8_file(slug, output_dir="catcast"):
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"✗ Silindi: {output_file}")

def main():
    config = load_config()
    
    # Token əgər config-də varsa
    token = config.get("token") if isinstance(config, dict) else None
    
    # Əgər config array-dırsa
    if isinstance(config, list):
        channels = config
    else:
        channels = config.get("channels", [])
        token = config.get("token", None)
    
    for channel in channels:
        channel_id = channel.get("id")
        slug = channel.get("slug")
        
        print(f"\n📺 {slug} (ID: {channel_id})")
        
        data = get_current_program(channel_id, token)
        
        if data and data.get("status") == 1:
            stream_url = data.get("data", {}).get("full_mobile_url")
            if stream_url:
                create_m3u8_file(slug, stream_url)
            else:
                print("❌ Stream URL tapılmadı")
                delete_m3u8_file(slug)
        else:
            print("❌ API-dən düzgün cavab gəlmədi")
            delete_m3u8_file(slug)

if __name__ == "__main__":
    main()
