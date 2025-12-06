import asyncio
import httpx
import time

URL = "http://127.0.0.1:8000/"
NUM_REQUESTS = 5
WAIT_TIME = 3  # geschätzte Zeit einer einzelnen Anfrage, z.B. für künstliche Delay

async def send_request(i):
    start = time.time()
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            response = await client.get(URL)
            response.raise_for_status()
        except httpx.RequestError as e:
            print(f"Request {i} fehlgeschlagen: {e}")
            return None
    end = time.time()
    return end - start

async def main():
    print(f"Sende {NUM_REQUESTS} parallele Requests an {URL}...")
    
    # Tasks parallel starten
    tasks = [send_request(i) for i in range(1, NUM_REQUESTS + 1)]
    results = await asyncio.gather(*tasks)

    # Prüfen, ob Requests fehlgeschlagen sind
    if any(r is None for r in results):
        print("Mindestens ein Request ist fehlgeschlagen. Server prüfen.")
        return

    # Zeiten ausgeben
    print("Einzelne Request-Zeiten (Sekunden):", ["{:.3f}".format(r) for r in results])
    avg_time = sum(results) / NUM_REQUESTS
    print(f"Durchschnittliche Request-Zeit: {avg_time:.3f} Sekunden")

    # Auswertung
    if avg_time < WAIT_TIME:
        print("Der Server scheint asynchron zu sein (Requests parallel).")
    else:
        print("Der Server scheint synchron zu sein (Requests nacheinander).")


asyncio.run(main())