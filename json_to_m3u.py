import json

# JSON faylının adı
json_file = "channels.json"

# M3U faylının adı
m3u_file = "playlist.m3u"

try:
    # JSON faylını aç və oxu
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Yeni M3U faylı yarat
    with open(m3u_file, "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n\n")

        # Kanalları əlavə et
        for channel in data["channels"]:
            m3u.write(f"#EXTINF:-1, {channel['name']}\n")
            m3u.write(f"{channel['url']}\n\n")

    print(f"✅ M3U faylı yaradıldı: {m3u_file}")

except Exception as e:
    print(f"❌ Xəta baş verdi: {e}")
