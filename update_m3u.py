import requests
import re

# Kanalların URL-ləri
CHANNELS = [
    {"name": "Show TV", "url": "https://www.showtv.com.tr/canli-yayin"},
    {"name": "CNNTürk", "url": "https://www.youtube.com/@cnnturk/live"},
    # Burada əlavə etmək istədiyiniz kanalları daxil edin
]

# M3U faylının adı
M3U_FILE = "playlist.m3u"

# Yeni tokenli m3u8 linkini tapmaq üçün funksiya
def get_new_m3u8_link(channel_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    
    response = requests.get(channel_url, headers=headers)
    
    if response.status_code == 200:
        match = re.search(r'https://[^"]+\.m3u8\?[^"]+', response.text)
        if match:
            return match.group(0)
        else:
            print(f"❌ Yeni m3u8 link tapılmadı: {channel_url}")
            return None
    else:
        print(f"❌ Xəta kodu: {response.status_code} - {channel_url}")
        return None

# Yeni M3U faylını yaradacağıq
with open(M3U_FILE, "w", encoding="utf-8") as m3u:
    m3u.write("#EXTM3U\n")
    
    # Hər kanal üçün linki tapıb M3U faylını əlavə edirik
    for channel in CHANNELS:
        print(f"❗ Kanal: {channel['name']} - URL: {channel['url']}")
        new_m3u8_link = get_new_m3u8_link(channel["url"])

        if new_m3u8_link:
            m3u.write(f"#EXTINF:-1, {channel['name']}\n")
            m3u.write(f"{new_m3u8_link}\n")
            print(f"✅ Kanal {channel['name']} üçün M3U link əlavə olundu.")
        else:
            print(f"❌ Kanal {channel['name']} üçün M3U link əlavə olunmadı.")

print(f"✅ M3U playlist yeniləndi: {M3U_FILE}")
