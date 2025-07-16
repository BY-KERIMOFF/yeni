import json

json_file = "channels.json"
m3u_file = "playlist.m3u"

try:
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    with open(m3u_file, "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n\n")
        for channel in data["channels"]:
            m3u.write(f"#EXTINF:-1, {channel['name']}\n")
            m3u.write(f"{channel['url']}\n\n")

    print(f"✅ M3U faylı yaradıldı: {m3u_file}")

except Exception as e:
    print(f"❌ Xəta baş verdi: {e}")
