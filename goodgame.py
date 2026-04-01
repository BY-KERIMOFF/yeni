import json
import os
import requests
from pathlib import Path
from datetime import datetime

def load_config(config_file="goodgame-config.json"):
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {config_file} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_file}")
        return None

def get_stream_info_by_id(channel_id):
    """Get stream information by channel ID."""
    url = f"https://api.goodgame.ru/v2/streams/{channel_id}"
    
    try:
        response = requests.get(url, timeout=60, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  ✗ API error for ID {channel_id}: {e}")
        return None

def create_m3u8_file(channel_id, channel_name, quality="720p", output_dir="goodgame"):
    """Create M3U8 playlist file."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Clean filename
    filename = "".join(c for c in channel_name if c.isalnum() or c in ('-', '_'))
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create M3U8 content with multiple quality options
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
# Channel: {channel_name}
# Channel ID: {channel_id}
# Quality: {quality}
# URL: https://goodgame.ru/{channel_name}
# Updated: {timestamp}

#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=480x270
https://hls.goodgame.ru/{channel_id}/{channel_id}_480p/index.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION=854x480
https://hls.goodgame.ru/{channel_id}/{channel_id}_480p/index.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
https://hls.goodgame.ru/{channel_id}/{channel_id}_720p/index.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=4000000,RESOLUTION=1920x1080
https://hls.goodgame.ru/{channel_id}/{channel_id}_1080p/index.m3u8

# Default stream (selected quality: {quality})
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
https://hls.goodgame.ru/{channel_id}/{channel_id}_{quality}/index.m3u8
"""
    
    # Write to file
    output_file = os.path.join(output_dir, f"{filename}.m3u8")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    
    print(f"  ✓ Created: {output_file}")
    return output_file

def delete_m3u8_file(channel_name, output_dir="goodgame"):
    """Delete M3U8 playlist file if it exists."""
    filename = "".join(c for c in channel_name if c.isalnum() or c in ('-', '_'))
    output_file = os.path.join(output_dir, f"{filename}.m3u8")
    
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"  ✗ Deleted: {output_file}")
            return True
        except Exception as e:
            print(f"  ✗ Error deleting: {e}")
            return False
    return False

def process_channel(channel):
    """Process a single channel."""
    channel_id = channel.get("id")
    channel_name = channel.get("channel_name")
    quality = channel.get("quality", "720p")
    enabled = channel.get("enabled", True)
    
    if not channel_id or not channel_name:
        print(f"  ⚠ Skipping invalid channel")
        return False
    
    if not enabled:
        print(f"  ⏭ Disabled: {channel_name}")
        return False
    
    print(f"\n📺 {channel_name} (ID: {channel_id})")
    
    # Get stream info
    stream_info = get_stream_info_by_id(channel_id)
    
    if stream_info and stream_info.get('status') == 'live':
        print(f"  ✅ LIVE")
        
        # Print stream details
        viewers = stream_info.get('viewers', 0)
        title = stream_info.get('title', 'No title')
        print(f"  👁️ Viewers: {viewers}")
        print(f"  📝 Title: {title[:60]}...")
        
        # Create M3U8 file
        create_m3u8_file(channel_id, channel_name, quality)
        return True
    else:
        print(f"  ❌ OFFLINE")
        delete_m3u8_file(channel_name)
        return False

def get_all_live_streams():
    """Get all live streams from GoodGame.ru."""
    url = "https://api.goodgame.ru/v2/streams"
    
    try:
        response = requests.get(url, timeout=60, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        streams = response.json()
        
        # Filter only live streams
        live_streams = [s for s in streams if s.get('status') == 'live']
        return live_streams
    except Exception as e:
        print(f"Error fetching streams: {e}")
        return []

def auto_mode():
    """Auto mode - detect all live streams."""
    print("="*50)
    print("AUTO MODE - Detecting all live streams")
    print("="*50)
    
    live_streams = get_all_live_streams()
    
    if not live_streams:
        print("No live streams found")
        return
    
    print(f"Found {len(live_streams)} live streams\n")
    
    successful = []
    
    for stream in live_streams:
        channel_name = stream.get('channel', {}).get('name')
        channel_id = stream.get('channel', {}).get('id')
        
        if channel_name and channel_id:
            print(f"📺 {channel_name} (ID: {channel_id})")
            
            # Get viewer count and title
            viewers = stream.get('viewers', 0)
            title = stream.get('title', 'No title')
            print(f"  👁️ Viewers: {viewers}")
            print(f"  📝 Title: {title[:60]}...")
            
            # Create M3U8 file
            create_m3u8_file(channel_id, channel_name, "720p")
            successful.append(channel_name)
            print()
    
    print("="*50)
    print(f"✅ Created playlists for {len(successful)} live streams")
    print("="*50)

def manual_mode():
    """Manual mode - use config file."""
    print("="*50)
    print("MANUAL MODE - Using config file")
    print("="*50)
    
    # Load configuration
    config = load_config()
    
    if config is None:
        print("\n⚠ No configuration found!")
        print("Creating default configuration...")
        
        # Create default config
        default_config = [
            {
                "id": 160450,
                "channel_name": "Dartval",
                "url": "https://goodgame.ru/Dartval#autoplay",
                "quality": "720p",
                "enabled": True,
                "description": "Dartval gaming stream"
            }
        ]
        
        with open("goodgame-config.json", 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        config = default_config
        print("✓ Default config created with Dartval channel\n")
    
    # Process all channels
    successful = []
    failed = []
    
    for channel in config:
        if process_channel(channel):
            successful.append(channel.get("channel_name"))
        else:
            failed.append(channel.get("channel_name"))
    
    # Summary
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"✅ LIVE: {len(successful)} channels")
    for name in successful:
        print(f"  - {name}")
    
    print(f"\n❌ OFFLINE: {len(failed)} channels")
    for name in failed:
        print(f"  - {name}")
    
    print(f"\n📁 Output directory: goodgame/")

def main():
    """Main function - automatically detects environment."""
    print("GOODGAME.RU STREAM UPDATER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if running in GitHub Actions
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    
    if is_github_actions:
        print("Running in GitHub Actions mode")
        print("Using manual mode with config file\n")
        manual_mode()
    else:
        # Local execution - ask user for mode
        print("\n1. Manual mode (use config file)")
        print("2. Auto mode (detect all live streams)")
        
        try:
            choice = input("\nSelect mode (1 or 2): ").strip()
            
            if choice == "2":
                auto_mode()
            else:
                manual_mode()
        except EOFError:
            # No input available, use manual mode
            print("\nNo input detected, using manual mode")
            manual_mode()

if __name__ == "__main__":
    main()
