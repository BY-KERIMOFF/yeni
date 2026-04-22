import json
import os
import requests
import time
import threading
from pathlib import Path
from datetime import datetime

def load_config(config_file="catcast-config.json"):
    """Load configuration from JSON file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_current_program(channel_id):
    """Send POST request to get current program information."""
    url = f"https://api.catcast.tv/api/channels/{channel_id}/getcurrentprogram"
    
    # Əlavə başlıqlar (bəzi hallarda tələb olunur)
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
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data for channel {channel_id}: {e}")
        return None

def extract_token_from_url(stream_url):
    """Extract token from full_mobile_url or return None."""
    if not stream_url:
        return None
    
    # Token-i URL-dən çıxar
    if "token=" in stream_url:
        token_part = stream_url.split("token=")[1]
        token = token_part.split("&")[0]
        return token
    return None

def create_m3u8_file(slug, channel_id, token, output_dir="catcast"):
    """Create M3U8 playlist file with V2 URL."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # V2 URL formatında yarat (daha etibarlı)
    v2_url = f"https://v2.catcast.tv/content/{channel_id}/index.m3u8?token={token}"
    
    # M3U8 content
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
{v2_url}
"""
    
    # Write to file
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    
    print(f"✓ Created/Updated: {output_file}")
    print(f"  └─ Token: {token[:20]}...")
    return output_file

def delete_m3u8_file(slug, output_dir="catcast"):
    """Delete M3U8 playlist file if it exists."""
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"✗ Deleted: {output_file}")
            return True
        except Exception as e:
            print(f"Error deleting file {output_file}: {e}")
            return False
    return False

def update_channel(channel, auto_delete_on_failure=True):
    """Update single channel M3U8 file."""
    channel_id = channel.get("id")
    slug = channel.get("slug")
    
    if not channel_id or not slug:
        print(f"⚠️ Skipping invalid channel: {channel}")
        return False
    
    print(f"\n📺 Processing: {slug} (ID: {channel_id}) - {datetime.now().strftime('%H:%M:%S')}")
    
    # Get current program data
    response_data = get_current_program(channel_id)
    
    if not response_data:
        print(f"❌ Failed to get data for {slug}")
        if auto_delete_on_failure:
            delete_m3u8_file(slug)
        return False
    
    # Extract full_mobile_url and token
    if response_data.get("status") == 1 and "data" in response_data:
        data = response_data["data"]
        full_mobile_url = data.get("full_mobile_url") or data.get("full_hls_url")
        
        if full_mobile_url:
            token = extract_token_from_url(full_mobile_url)
            if token:
                create_m3u8_file(slug, channel_id, token)
                print(f"✅ Successfully updated {slug}")
                return True
            else:
                print(f"⚠️ No token found in URL for {slug}")
        else:
            print(f"⚠️ No stream URL found for {slug}")
    else:
        print(f"⚠️ Invalid response status for {slug}")
    
    # If we reach here, something failed
    if auto_delete_on_failure:
        delete_m3u8_file(slug)
    return False

def main(auto_update_interval=None):
    """Main function to process all channels.
    
    Args:
        auto_update_interval: If provided (seconds), will run in auto-update mode
    """
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        print("❌ Error: catcast-config.json not found")
        return
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in catcast-config.json")
        return
    
    # Handle both list and dict config formats
    if isinstance(config, dict):
        channels = config.get("channels", [])
    else:
        channels = config
    
    if auto_update_interval:
        # Auto-update mode
        print(f"🔄 Auto-update mode enabled - updating every {auto_update_interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        def update_loop():
            while True:
                print("\n" + "="*60)
                print(f"🕐 Update cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)
                
                successful = 0
                for channel in channels:
                    if update_channel(channel):
                        successful += 1
                    time.sleep(1)  # Small delay between channels
                
                print(f"\n📊 Cycle complete: {successful}/{len(channels)} channels updated")
                print(f"⏰ Next update in {auto_update_interval} seconds\n")
                time.sleep(auto_update_interval)
        
        try:
            update_loop()
        except KeyboardInterrupt:
            print("\n\n👋 Auto-update stopped by user")
    else:
        # Single run mode
        successful_channels = []
        failed_channels = []
        
        for channel in channels:
            if update_channel(channel):
                successful_channels.append(channel.get("slug"))
            else:
                failed_channels.append(channel.get("slug"))
            time.sleep(0.5)  # Small delay
        
        # Summary
        print("\n" + "="*50)
        print("Processing Summary:")
        print("="*50)
        print(f"✓ Successful: {len(successful_channels)} channels")
        if successful_channels:
            for slug in successful_channels:
                print(f"  - {slug}")
        
        print(f"\n✗ Failed: {len(failed_channels)} channels")
        if failed_channels:
            for slug in failed_channels:
                print(f"  - {slug}")
        
        print("\n✅ Processing complete!")

if __name__ == "__main__":
    # İstifadə qaydaları:
    
    # 1. Tək işləmə üçün (bir dəfə icra edir):
    main()
    
    # 2. Avtomatik yeniləmə üçün (hər 300 saniyədə = 5 dəqiqə):
    # main(auto_update_interval=300)
    
    # 3. Hər 10 dəqiqədən bir yeniləmək üçün:
    # main(auto_update_interval=600)
