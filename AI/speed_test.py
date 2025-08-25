import speedtest
import time


while True:
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Mbps
    upload_speed = st.upload() / 1_000_000      # Mbps
    ping = st.results.ping

    result_md = (
        f"SpeedTest Results\n\n"
        f"Download Speed: {download_speed:.2f} Mbps\n"
        f"Upload Speed: {upload_speed:.2f} Mbps\n"
        f"Ping: {ping} ms\n"
        f"Measurement Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    with open("speedtest_results.md", "w", encoding="utf-8") as f:
        f.write(result_md)

    time.sleep(3600)  # Czekaj godzinę przed kolejnym pomiarem

