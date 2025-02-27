# M3U playlistini yaratmaq üçün Python skripti

m3u_url = "https://manifest.googlevideo.com/api/manifest/hls_variant/expire/1740642231/ei/V8O_Z9KjJ7XKi9oP3sCn2Qc/ip/92.205.0.142/id/gMWls8NtaNo.1/source/yt_live_broadcast/requiressl/yes/xpc/EgVo2aDSNQ%3D%3D/hfr/1/playlist_duration/30/manifest_duration/30/maudio/1/gcr/fr/bui/AUWDL3zFt7UEAUBJBpjqn9N3vKHp7LO2_XydCEspyar7qIYIXdorpz-LNpr3vry4xBme8AuwCFQXPg6F/spc/RjZbSZ_xJJiJqzPAZnW8RWO3igrZQPoQLQTMvXs3ZaNETkSRclhoMO1pL1EixzCV5skdp4U/vprv/1/go/1/rqh/5/pacing/0/nvgoi/1/ncsapi/1/keepalive/yes/fexp/51326932%2C51355912/dover/11/itag/0/playlist_type/DVR/sparams/expire%2Cei%2Cip%2Cid%2Csource%2Crequiressl%2Cxpc%2Chfr%2Cplaylist_duration%2Cmanifest_duration%2Cmaudio%2Cgcr%2Cbui%2Cspc%2Cvprv%2Cgo%2Crqh%2Citag%2Cplaylist_type/sig/AJfQdSswRAIgWvniQsmpdwFUiOI492rxcUHG0uyMsjaOTkJSaJEBYboCIHD39tVbRHXfm7g0NAJ7OP06HdQ88BP7XqrwEDpvvQZ7/file/index.m3u8"

# M3U faylı yaratmaq
with open("playlist.m3u", "w", encoding="utf-8") as m3u:
    m3u.write("#EXTM3U\n")
    m3u.write(f"#EXTINF:-1, Live Stream\n")
    m3u.write(f"{m3u_url}\n")

print("✅ M3U faylı yaratıldı: playlist.m3u")
