"""
Services
----------------

An example showing how to fetch all services and print them.

Updated on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>

"""

import asyncio
import platform

from bleak import BleakClient

service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'
data_uuid = 'fec26ec4-6d71-4442-9f81-55bc21d658d6'

global g_data, g_xfer_done
g_xfer_done = False
def data_handler(sender, data):
    global g_data, g_xfer_done
    print("sender, data", sender, data)
    g_data = data
    g_xfer_done = True

async def run(mac_addr: str, loop: asyncio.AbstractEventLoop):
    global g_data, g_xfer_done
    async with BleakClient(mac_addr, loop=loop) as client:
        svcs = await client.get_services()
        # print("Services:", svcs.services)
        # print("C:", svcs.characteristics)
        c = await client.read_gatt_char(rw_uuid)
        count = await client.read_gatt_char(count_uuid)
        count = int.from_bytes(count, byteorder='little')
        print(c, count, flush=True)
        await client.start_notify(data_uuid, data_handler) # , kw)
        print("Started notify")
        await client.write_gatt_char(rw_uuid, bytearray(b'I'))
        print("sent I", flush=True)
        g_xfer_done = False
        while not g_xfer_done:
            await asyncio.sleep(0.01)

        print(c, count, g_data)

mac_addr = ('58:8E:81:A5:4D:9D')
loop = asyncio.get_event_loop()
loop.run_until_complete(run(mac_addr, loop))
