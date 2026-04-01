import json
import os
import requests
from pathlib import Path

def load_config(config_file="goodgame-config.json"):
    """Load configuration from JSON file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_stream_info(channel_name):
    """Get stream information from GoodGame.ru API."""
    # GoodGame.ru API endpoint for stream info
    url = f"https://api.goodgame.ru/v2/streams/{channel_name}"
    
    try:
        response = requests.get(url, timeout=60, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for channel {channel_name}: {e}")
        return None

def get_stream_url(channel_name):
    """Get actual stream URL from GoodGame.ru."""
    # Alternative method: get HLS stream URL
    stream_url = f"https://hls.goodgame.ru/{channel_name}/{channel_name}_720p/index.m3u8"
    return stream_url

def check_stream_status(channel_name):
    """Check if stream is currently live."""
    stream_info = get_stream_info(channel_name)
    
    if stream_info and stream_info.get('status') == 'live':
        return True, stream_info
    return False, None

def create_m3u8_file(channel_name, stream_url, quality="720p", output_dir="goodgame"):
    """Create M3U8 playlist file."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Create M3U8 content with multiple quality options
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3

#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=480x270
https://hls.goodgame.ru/{channel_name}/{channel_name}_480p/index.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION=854x480
https://hls.goodgame.ru/{channel_name}/{channel_name}_480p/index.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
https://hls.goodgame.ru/{channel_name}/{channel_name}_720p/index.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=4000000,RESOLUTION=1920x1080
https://hls.goodgame.ru/{channel_name}/{channel_name}_1080p/index.m3u8

# Default stream (720p)
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
https://hls.goodgame.ru/{channel_name}/{channel_name}_720p/index.m3u8
"""
    
    # Write to file
    output_file = os.path.join(output_dir, f"{channel_name}.m3u8")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    
    print(f"✓ Created M3U8 file: {output_file}")
    return output_file

def delete_m3u8_file(channel_name, output_dir="goodgame"):
    """Delete M3U8 playlist file if it exists."""
    output_file = os.path.join(output_dir, f"{channel_name}.m3u8")
    
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"✗ Deleted M3U8 file: {output_file}")
            return True
        except Exception as e:
            print(f"Error deleting file {output_file}: {e}")
            return False
    else:
        print(f"✗ File not found (already deleted or never created): {output_file}")
        return False

def get_all_streams():
    """Get list of all active streams from GoodGame.ru."""
    url = "https://api.goodgame.ru/v2/streams"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching streams list: {e}")
        return None

def main():
    """Main function to process all channels."""
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        print("Error: goodgame-config.json not found")
        print("Creating example config file...")
        
        # Create example config
        example_config = [
            {
                "channel_name": "example_channel",
                "quality": "720p",
                "enabled": True
            }
        ]
        
        with open("goodgame-config.json", 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=4, ensure_ascii=False)
        
        print("Please edit goodgame-config.json with your channels and run again.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in goodgame-config.json")
        return
    
    successful_channels = []
    failed_channels = []
    
    # Process each channel
    for channel in config:
        channel_name = channel.get("channel_name")
        
        if not channel_name:
            print(f"Skipping invalid channel entry: {channel}")
            continue
        
        # Check if channel is enabled
        if not channel.get("enabled", True):
            print(f"\nSkipping disabled channel: {channel_name}")
            continue
        
        print(f"\nProcessing channel: {channel_name}")
        
        # Check if stream is live
        is_live, stream_info = check_stream_status(channel_name)
        
        if is_live:
            print(f"✓ Stream is LIVE for {channel_name}")
            
            # Get stream URL
            quality = channel.get("quality", "720p")
            stream_url = get_stream_url(channel_name)
            
            # Create M3U8 file
            create_m3u8_file(channel_name, stream_url, quality)
            successful_channels.append(channel_name)
            
            # Print additional stream info if available
            if stream_info:
                viewers = stream_info.get('viewers', 0)
                title = stream_info.get('title', 'No title')
                print(f"  - Viewers: {viewers}")
                print(f"  - Title: {title[:50]}...")
        else:
            print(f"✗ Stream is OFFLINE for {channel_name}")
            delete_m3u8_file(channel_name)
            failed_channels.append(channel_name)
    
    # Summary
    print("\n" + "="*50)
    print("Processing Summary:")
    print("="*50)
    print(f"✓ Live streams: {len(successful_channels)} channels")
    if successful_channels:
        for channel_name in successful_channels:
            print(f"  - {channel_name}")
    
    print(f"\n✗ Offline streams: {len(failed_channels)} channels")
    if failed_channels:
        for channel_name in failed_channels:
            print(f"  - {channel_name}")
    
    print("\nProcessing complete!")

def main_auto():
    """Auto-detect all live streams and create playlists."""
    print("Auto-detecting all live streams...")
    
    streams = get_all_streams()
    
    if streams:
        live_streams = [s for s in streams if s.get('status') == 'live']
        
        print(f"Found {len(live_streams)} live streams")
        
        for stream in live_streams:
            channel_name = stream.get('channel', {}).get('name')
            if channel_name:
                print(f"\nProcessing: {channel_name}")
                stream_url = get_stream_url(channel_name)
                create_m3u8_file(channel_name, stream_url)
        
        print(f"\n✓ Created playlists for {len(live_streams)} streams")
    else:
        print("Failed to fetch streams list")

if __name__ == "__main__":
    print("GoodGame.ru Stream M3U8 Creator")
    print("="*40)
    print("1. Manual mode (use config file)")
    print("2. Auto mode (detect all live streams)")
    
    choice = input("\nSelect mode (1 or 2): ").strip()
    
    if choice == "2":
        main_auto()
    else:
        main()
