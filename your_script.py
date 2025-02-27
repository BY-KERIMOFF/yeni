import requests
import time

def get_m3u8_url():
    url = "https://www.ecanlitvizle.app/"
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
