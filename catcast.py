import json
import os
import requests
from pathlib import Path

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://catcast.tv",
    "Referer": "https://catcast.tv/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def load_config(config_file="catcast-config.json"):
    """Load configuration from JSON file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_current_program(channel_id):
    """Send POST request to get current program information."""
    url = f"https://api.catcast.tv/api/channels/{channel_id}/getcurrentprogram"
    
    try:
        # Some environments inject HTTP(S)_PROXY and Catcast blocks these requests.
        # trust_env=False ignores proxy variables and fixes intermittent 403 tunnel errors.
        with requests.Session() as session:
            session.trust_env = False
            session.headers.update(DEFAULT_HEADERS)

            response = session.post(url, timeout=60)
            if response.status_code == 405:
                # Catcast can switch method requirements; fallback to GET for resilience.
                response = session.get(url, timeout=60)

            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for channel {channel_id}: {e}")
        return None


def extract_stream_url(response_data):
    """Extract stream URL from known Catcast response fields."""
    data = response_data.get("data") if isinstance(response_data, dict) else None
    if not isinstance(data, dict):
        return None

    for key in ("full_mobile_url", "mobile_url", "full_url", "stream_url", "url"):
        value = data.get(key)
        if value and isinstance(value, str):
            return value

    return None

def create_m3u8_file(slug, stream_url, output_dir="catcast"):
    """Create M3U8 playlist file."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Create M3U8 content
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2000000
{stream_url}
"""
    
    # Write to file
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    
    print(f"✓ Created M3U8 file: {output_file}")
    return output_file

def delete_m3u8_file(slug, output_dir="catcast"):
    """Delete M3U8 playlist file if it exists."""
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    
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

def main():
    """Main function to process all channels."""
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        print("Error: catcast-config.json not found")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in catcast-config.json")
        return
    
    successful_channels = []
    failed_channels = []
    
    # Process each channel
    for channel in config:
        channel_id = channel.get("id")
        slug = channel.get("slug")
        
        if not channel_id or not slug:
            print(f"Skipping invalid channel entry: {channel}")
            continue
        
        print(f"\nProcessing channel: {slug} (ID: {channel_id})")
        
        # Get current program data
        response_data = get_current_program(channel_id)
        
        if not response_data:
            print(f"Failed to get data for channel {channel_id}")
            delete_m3u8_file(slug)
            failed_channels.append(slug)
            continue
        
        # Extract stream URL (Catcast may change field names over time)
        if response_data.get("status") == 1 and "data" in response_data:
            stream_url = extract_stream_url(response_data)
            
            if stream_url:
                # Create M3U8 file
                create_m3u8_file(slug, stream_url)
                successful_channels.append(slug)
                print(f"Successfully processed {slug}")
            else:
                print(f"No stream URL field found for channel {channel_id}")
                delete_m3u8_file(slug)
                failed_channels.append(slug)
        else:
            print(f"Invalid response status for channel {channel_id}")
            delete_m3u8_file(slug)
            failed_channels.append(slug)
    
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
    
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()
