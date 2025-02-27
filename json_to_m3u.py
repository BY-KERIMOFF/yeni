import json

# JSON faylını oxumaq
with open("channels.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# M3U faylını yaratmaq
m3u_content = "#EXTM3U\n\n"

for channel in data["channels"]:
    m3u_content += f'#EXTINF:-1, {channel["name"]}\n{channel["url"]}\n\n'

# M3U faylını yazmaq
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)

print("✅ M3U faylı yaradıldı: playlist.m3u")
