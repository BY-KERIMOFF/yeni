import json

# JSON faylını oxuyuruq
with open("channels.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# M3U faylını açırıq
with open("playlist.m3u", "w", encoding="utf-8") as m3u:
    m3u.write("#EXTM3U\n\n")
    
    for channel in data["channels"]:
        name = channel["name"]
        url = channel["url"]
        
        # YouTube linkləri üçün xəbərdarlıq veririk
        if "youtube.com" in url:
            print(f"⚠️ Diqqət: {name} üçün YouTube linkini dəyişdirmək lazımdır!")

        m3u.write(f"#EXTINF:-1, {name}\n{url}\n\n")

print("✅ M3U faylı uğurla yaradıldı: playlist.m3u")
