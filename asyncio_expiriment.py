import asyncio
import time

async def say_hello(n):
    print("Start")
    start = time.time()
    await asyncio.sleep(n)
    print("End")
    await asyncio.sleep(2)
    print("....")
    end = time.time()
    print(f"Actual time = {end - start}")

async def say_hello2(n):
    print("Start 2")
    time.sleep(n)
    print("End 2")
    time.sleep(2)
    print(".... 2")

# 1.
# start
# start 2
# end
# end 2
# ....
# .... 2
# time = 4

# 2.
# start
# start 2
# end 2
# .... 2
# end
# ....
# time = 7

async def main():
    await asyncio.gather(say_hello(2), say_hello2(3))
if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"dauerte insgesamt {end - start}")