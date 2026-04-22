import json
import os
import requests
import time
import subprocess
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
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data for channel {channel_id}: {e}")
        return None

def extract_token_from_url(stream_url):
    """Extract token from full_mobile_url or return None."""
    if not stream_url:
        return None
    
    if "token=" in stream_url:
        token_part = stream_url.split("token=")[1]
        token = token_part.split("&")[0]
        return token
    return None

def create_m3u8_file(slug, channel_id, token, output_dir="catcast"):
    """Create M3U8 playlist file with V2 URL."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    v2_url = f"https://v2.catcast.tv/content/{channel_id}/index.m3u8?token={token}"
    
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
{v2_url}
"""
    
    output_file = os.path.join(output_dir, f"{slug}.m3u8")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    
    print(f"✓ Created/Updated: {output_file}")
    return output_file

def git_commit_and_push(repo_path, file_path, commit_message):
    """Git commit and push changes."""
    try:
        # Change to repo directory
        os.chdir(repo_path)
        
        # Add file
        subprocess.run(["git", "add", file_path], check=True, capture_output=True, text=True)
        
        # Check if there are changes
        status = subprocess.run(["git", "status", "--porcelain", file_path], capture_output=True, text=True)
        
        if status.stdout.strip():
            # Commit
            subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True)
            
            # Push
            subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
            
            print(f"  └─ ✅ Pushed to GitHub: {commit_message}")
            return True
        else:
            print(f"  └─ ⏭️ No changes to commit")
            return False
    except subprocess.CalledProcessError as e:
        print(f"  └─ ❌ Git error: {e}")
        return False

def update_channel(channel, repo_path=None):
    """Update single channel M3U8 file and push to GitHub."""
    channel_id = channel.get("id")
    slug = channel.get("slug")
    
    if not channel_id or not slug:
        print(f"⚠️ Skipping invalid channel: {channel}")
        return False
    
    print(f"\n📺 Processing: {slug} (ID: {channel_id}) - {datetime.now().strftime('%H:%M:%S')}")
    
    response_data = get_current_program(channel_id)
    
    if not response_data:
        print(f"❌ Failed to get data for {slug}")
        return False
    
    if response_data.get("status") == 1 and "data" in response_data:
        data = response_data["data"]
        full_mobile_url = data.get("full_mobile_url") or data.get("full_hls_url")
        
        if full_mobile_url:
            token = extract_token_from_url(full_mobile_url)
            if token:
                # Create M3U8 file
                m3u8_file = create_m3u8_file(slug, channel_id, token)
                print(f"✅ Successfully updated {slug}")
                
                # Push to GitHub if repo path provided
                if repo_path:
                    commit_msg = f"Auto-update {slug} M3U8 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    git_commit_and_push(repo_path, m3u8_file, commit_msg)
                
                return True
            else:
                print(f"⚠️ No token found in URL for {slug}")
        else:
            print(f"⚠️ No stream URL found for {slug}")
    else:
        print(f"⚠️ Invalid response status for {slug}")
    
    return False

def main():
    """Main function with auto-update every 5 minutes."""
    
    # ==================== KONFİQURASİYA ====================
    # GitHub repo lokal yolunu BURAYA YAZIN!
    GITHUB_REPO_PATH = "/home/sizin_istifadeci/by_kerimoff_065"  # 🔴 BUNU DƏYİŞİN!
    UPDATE_INTERVAL = 300  # 5 dəqiqə
    
    # ======================================================
    
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
    
    print(f"🔄 Auto-update mode enabled - updating every {UPDATE_INTERVAL} seconds")
    print(f"📁 GitHub repo path: {GITHUB_REPO_PATH}")
    print("Press Ctrl+C to stop\n")
    
    def update_loop():
        while True:
            print("\n" + "="*60)
            print(f"🕐 Update cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            successful = 0
            for channel in channels:
                if update_channel(channel, GITHUB_REPO_PATH):
                    successful += 1
                time.sleep(2)  # Delay between channels
            
            print(f"\n📊 Cycle complete: {successful}/{len(channels)} channels updated")
            print(f"⏰ Next update in {UPDATE_INTERVAL} seconds\n")
            time.sleep(UPDATE_INTERVAL)
    
    try:
        update_loop()
    except KeyboardInterrupt:
        print("\n\n👋 Auto-update stopped by user")

if __name__ == "__main__":
    main()
