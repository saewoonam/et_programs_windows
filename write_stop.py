import asyncio
import info
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Not enough arguments")
        sys.exit(1)
    elif len(sys.argv) >= 3:
        device_number = int(sys.argv[1])
        number_to_find = int(sys.argv[2])
    elif len(sys.argv) == 2:
        device_number = int(sys.argv[1])
        number_to_find = 4
    global loop
    loop = asyncio.get_event_loop()
    print("looking for NIST ET bluetooth devices")
    devices = loop.run_until_complete(info.run(device_number, number_to_find, b's'))
    # devices =  asyncio.run(run())
    # print(devices)
