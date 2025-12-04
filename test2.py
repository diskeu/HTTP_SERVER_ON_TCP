import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://localhost:8000/test"
NUM_REQUESTS = 5
WAIT_TIME = 3  # geschätzte Zeit einer einzelnen Anfrage (für Auswertung)

def send_request(i):
    start = time.time()
    try:
        response = requests.get(URL, timeout=40)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request {i} konnte den Server nicht erreichen: {e}")
        return None
    end = time.time()
    duration = end - start
    return duration

def main():
    print(f"Sende {NUM_REQUESTS} parallele Requests an {URL}...")
    times = []

    with ThreadPoolExecutor(max_workers=NUM_REQUESTS) as executor:
        futures = {executor.submit(send_request, i): i for i in range(1, NUM_REQUESTS + 1)}
        for future in as_completed(futures):
            duration = future.result()
            if duration is None:
                print("Mindestens ein Request ist fehlgeschlagen. Server prüfen.")
                return
            times.append(duration)

    print("Einzelne Request-Zeiten (Sekunden):", ["{:.3f}".format(t) for t in times])
    avg_time = sum(times) / NUM_REQUESTS
    print(f"Durchschnittliche Request-Zeit: {avg_time:.3f} Sekunden")

    if avg_time < WAIT_TIME:
        print("Der Server scheint asynchron zu sein (Requests wurden parallel bearbeitet).")
    else:
        print("Der Server scheint synchron zu sein (Requests wurden nacheinander bearbeitet).")

main()