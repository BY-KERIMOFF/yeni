import json
import os

# JSON faylını oxumaq
json_path = os.path.join(os.path.dirname(__file__), "channels.json")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# M3U faylını yaratmaq
m3u_content = "#EXTM3U\n\n"

for channel in data["channels"]:
    m3u_content += f'#EXTINF:-1, {channel["name"]}\n{channel["url"]}\n\n'

# M3U faylını yazmaq
m3u_path = os.path.join(os.path.dirname(__file__), "playlist.m3u")
with open(m3u_path, "w", encoding="utf-8") as f:
    f.write(m3u_content)

print("✅ M3U faylı yaradıldı: playlist.m3u")
