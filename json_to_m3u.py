# M3U playlistini yaratmaq üçün Python skripti

m3u_url = "https://manifest.googlevideo.com/api/manifest/hls_variant/expire/1740641817/ei/ucG_Z8S1LMPR6dsPgdrHgQU/ip/92.205.0.142/id/gMWls8NtaNo.1/source/yt_live_broadcast/requiressl/yes/xpc/EgVo2aDSNQ%3D%3D/tx/51399978/txs/51399971%2C51399972%2C51399973%2C51399974%2C51399975%2C51399976%2C51399977%2C51399978/hfr/1/playlist_duration/30/manifest_duration/30/maudio/1/gcr/fr/bui/AUWDL3wRKquwasE6sTw_MxmF2mem05LQ37187bwQINdMWPLHqwgDlU-htyEnSHlbBqMprevQwbt7GEtz/spc/RjZbSUM-14p5lMqRUNa46o9Os8qE0WjaY4_1W0wU3JYfZdoFkUwsHPbqhs-Jm8Wv8bFT87o/vprv/1/go/1/rqh/5/pacing/0/nvgoi/1/ncsapi/1/keepalive/yes/fexp/51326932%2C51355912%2C51387515/dover/11/itag/0/playlist_type/DVR/sparams/expire%2Cei%2Cip%2Cid%2Csource%2Crequiressl%2Cxpc%2Ctx%2Ctxs%2Chfr%2Cplaylist_duration%2Cmanifest_duration%2Cmaudio%2Cgcr%2Cbui%2Cspc%2Cvprv%2Cgo%2Crqh%2Citag%2Cplaylist_type/sig/AJfQdSswRAIgKAOfPHd_Ic0SeemaSEVhp6TJGfDhyAkwP_T7bssxd30CIBf-uqLzitZUvLXQpnN3LMWohW8m_yc9goieSz1kJ_AB/file/index.m3u8"

# M3U faylı yaratmaq
with open("playlist.m3u", "w", encoding="utf-8") as m3u:
    m3u.write("#EXTM3U\n")
    m3u.write(f"#EXTINF:-1, Live Stream\n")
    m3u.write(f"{m3u_url}\n")

print("✅ M3U faylı yaratıldı: playlist.m3u")
