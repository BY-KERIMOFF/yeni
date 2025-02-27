import requests
import re

# Orijinal YouTube Live URL-i (Bunu dəyişə bilərsiniz)
youtube_url = "https://www.youtube.com/@cnnturk/live"

# Yeni m3u8 linkini tapmaq üçün funksiya
def get_m3u8_link(youtube_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    
    response = requests.get(youtube_url, headers=headers)
    
    if response.status_code == 200:
        match = re.search(r'https://manifest\.googlevideo\.com/api/manifest/hls_variant/[^"]+', response.text)
        if match:
            return match.group(0)
        else:
            print("❌ Yeni m3u8 link tapılmadı!")
            return None
    else:
        print(f"❌ Xəta kodu: {response.status_code}")
        return None

# Yenilənmiş M3U linkini götürək
m3u8_link = get_m3u8_link(youtube_url)

if m3u8_link:
    with open("playlist.m3u", "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n")
        m3u.write(f"#EXTINF:-1, CNN Türk Live\n")
        m3u.write(f"{m3u8_link}\n")
    
    print("✅ M3U playlist yeniləndi: playlist.m3u")
