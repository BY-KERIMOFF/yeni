import requests
import re

# Saytın URL-si (linki bu saytdan tapırıq)
SOURCE_URL = "https://www.showtv.com.tr/canli-yayin"

# M3U faylının adı
M3U_FILE = "playlist.m3u"

# Yeni tokenli m3u8 linkini tapmaq üçün funksiya
def get_new_m3u8_link():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    
    response = requests.get(SOURCE_URL, headers=headers)
    
    if response.status_code == 200:
        match = re.search(r'https://[^"]+\.m3u8\?[^"]+', response.text)
        if match:
            return match.group(0)
        else:
            print("❌ Yeni m3u8 link tapılmadı!")
            return None
    else:
        print(f"❌ Xəta kodu: {response.status_code}")
        return None

# Yeni linki alıb M3U faylını yeniləyək
new_m3u8_link = get_new_m3u8_link()

if new_m3u8_link:
    with open(M3U_FILE, "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n")
        m3u.write(f"#EXTINF:-1, Show TV Live\n")
        m3u.write(f"{new_m3u8_link}\n")
    
    print(f"✅ M3U playlist yeniləndi: {M3U_FILE}")
else:
    print("❌ M3U faylı yenilənmədi!")
