import asyncio
from bleak import discover

from bleak import BleakClient
from bleak import _logger as logger
from bleak.uuids import uuid16_dict

from consolemenu import *
from consolemenu.items import *

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

async def m(devices):
    # Create the root menu
    menu = ConsoleMenu("Bluetooth Devices Menu", "")
    async def item_func(peripheral):
        result = await get_counts(peripheral)
        print(result[1])
        await asyncio.sleep.sleep(5)
        # input("Press Enter to continue.")

    # Create a menu item that calls a function
    for peripheral in devices:
        item_name = peripheral.name
        function_item = FunctionItem(item_name, item_func, [peripheral])
        menu.append_item(function_item)

    menu.start()
    menu.join()

async def run():
    #devices = await discover()
    print("Trying to find NIST ET devices")
    et_devices = await list.get_et_list()


    await m(et_devices)

    # for device in et_devices:
    #     print('*'*80)
    #     result = await get_counts(device)
    #     print(device.name, result)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
