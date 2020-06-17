"""
Scan/Discovery
--------------

Example showing how to scan for BLE devices.

Updated on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>

"""

import asyncio
from bleak import discover

from bleak import BleakClient
from bleak import _logger as logger
from bleak.uuids import uuid16_dict

import list

service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'

async def get_counts(device):
    async with BleakClient(device.address) as client:
        # print(device.name, end=" ")
        x = await client.is_connected()
        # print("Connected: {0}".format(x))
        c = await client.read_gatt_char(rw_uuid)
        # print('last rw command: ',c)
        count = await client.read_gatt_char(count_uuid)
        count = int.from_bytes(bytes(count), byteorder='little')
        # print('count', count, int.from_bytes(bytes(count), byteorder='little'))
        return c, count

async def connect(client):
    connected = False
    while not connected:
        try:
            print("Try to connect to ", client, flush=True)
            connected = await client.connect()
            print("result", client, connected)
        except Exception as e:
            print(e)

async def run():
    #devices = await discover()
    print("Trying to find NIST ET devices")
    et_devices = await list.get_et_list()
    conn = {}
    for device in et_devices:
        conn[device.name] = BleakClient(device.address)

    # for key in conn.keys():
    #     await connect(conn[key])

    # tasks = []
    # for key in conn.keys():
    #     task = loop.create_task(connect(conn[key]))
    #     tasks.append(task)
    # result = await asyncio.wait(tasks)
    # print("result", result)

    # for key in conn.keys():
    #     print(key, await conn[key].is_connected())
    # print(len(result))
    # excepted_list = []
    # for r in result[0]:
    #     if r.exception() is not None:
    #         excepted_list.append(r)
    # print(excepted_list)
    # for key in conn.keys():
    #     print(key, await conn[key].is_connected())
    # for key in conn.keys():
    for key in conn.keys():
        # key = 'NIST-GEN'
        await connect(conn[key])
        count = await conn[key].read_gatt_char(count_uuid)
        count = int.from_bytes(bytes(count), byteorder='little')
        print(key, conn[key].address, count)
        await conn[key].disconnect()
    # return conn
loop = asyncio.get_event_loop()
conn = loop.run_until_complete(run())
print("done")
# print(conn)

