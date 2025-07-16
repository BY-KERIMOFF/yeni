import json
import subprocess

json_path = "channels.json"

try:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for channel in data["channels"]:
        page_url = channel["url"]
        print(f"[🔍] Kanal: {channel['name']} - Yoxlanır...")

        try:
            result = subprocess.run(
                ["yt-dlp", "-g", page_url],
                capture_output=True,
                text=True,
                timeout=15
            )
            stream_url = result.stdout.strip()
            if stream_url.startswith("http") and ".m3u8" in stream_url:
                channel["url"] = stream_url
                print(f"✅ Tapıldı: {stream_url}")
            else:
                print(f"⚠️ Tapılmadı və ya keçərsiz: {page_url}")

        except Exception as e:
            print(f"❌ Xəta: {e}")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n📁 JSON faylı yeniləndi: channels.json")

except Exception as e:
    print(f"❌ Baş xəta: {e}")
