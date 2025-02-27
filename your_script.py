import requests
import time

def get_m3u8_url():
    url = "https://manifest.googlevideo.com/api/manifest/hls_variant/expire/1740640205/ei/bbu_Z-rsDt2IzPsP0r2JsQE/ip/92.205.0.142/id/gMWls8NtaNo.1/source/yt_live_broadcast/requiressl/yes/xpc/EgVo2aDSNQ%3D%3D/tx/51399978/txs/51399971%2C51399972%2C51399973%2C51399974%2C51399975%2C51399976%2C51399977%2C51399978/hfr/1/playlist_duration/30/manifest_duration/30/maudio/1/gcr/fr/bui/AUWDL3wgfWT6bW0NtwK_-INPiYQpjcxlNAi72QX3ShOhx18lGnk0hE2RzA_wQDuS9Yvc0WKuckAkjA1y/spc/RjZbSWPzLCEpWv3CNh1iFORDAXq-dcw4hjRG-TyMcDj5TeMVUhLDv5wb2r4zbBjD6JQvwA4/vprv/1/go/1/rqh/5/pacing/0/nvgoi/1/ncsapi/1/keepalive/yes/fexp/51326932%2C51355912/dover/11/itag/0/playlist_type/DVR/sparams/expire%2Cei%2Cip%2Cid%2Csource%2Crequiressl%2Cxpc%2Ctx%2Ctxs%2Chfr%2Cplaylist_duration%2Cmanifest_duration%2Cmaudio%2Cgcr%2Cbui%2Cspc%2Cvprv%2Cgo%2Crqh%2Citag%2Cplaylist_type/sig/AJfQdSswRQIgTckPHin5lQwCBZnfnGA5Oc9muaD62dg7zA6iEZE33TgCIQCQ8xECz6jZsOtykMrDMpeOH-aJq3SHTY-JkeWu3KnGMg%3D%3D/file/index.m3u8"
    response = requests.get(url)
    return response.text

def save_m3u8(content):
    with open("stream.m3u8", "w") as f:
        f.write(content)

while True:
    m3u8_content = get_m3u8_url()
    save_m3u8(m3u8_content)
    print("M3U8 URL refreshed.")
    time.sleep(30)  # Yeniləmə intervalı (30 saniyə)
