import asyncio
from bleak import discover

from bleak import BleakClient
from bleak import _logger as logger
from bleak.uuids import uuid16_dict
import list_et

service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'
data_uuid = 'fec26ec4-6d71-4442-9f81-55bc21d658d6'

async def get_et_list(num=4):
    found = False
    while not found:
        devices = await discover()
        et_devices = []
        for d in devices:
            # print(d.__dict__.keys())
            # print(d.address)
            # print(d.details)
            if 'uuids' in d.metadata:
                # print(d.metadata['uuids'])
                if service_uuid in d.metadata['uuids']:
                    print(d.name)
                    et_devices.append(d)
        if len(et_devices)>= num:
            found = True
        else:
            print(f"Found {len(et_devices)}/{num}")
    return et_devices

async def run():
    global g_client, g_total_expected, g_get_idx, g_ready, g_fp_out
    found = False
    num = 6
    while not found:
        devices = await discover()
        et_devices = []
        for d in devices:
            # print(d.__dict__.keys())
            # print(d.address)
            # print(d.details)
            if 'uuids' in d.metadata:
                # print(d.metadata['uuids'])
                if service_uuid in d.metadata['uuids']:
                    print(d.name)
                    et_devices.append(d)
        if len(et_devices)>= num:
            found = True
        else:
            print(f"Found {len(et_devices)}/{num}")
    for device in et_devices:
        client = BleakClient(device.address)
        connected = False
        while not connected:
            try:
                connected = await client.connect()
            except Exception as e:
                print(e)
                print("Trying again")

        g_client = client
        print(device.name, end=" ")
        x = await client.is_connected()
        print("Connected: {0}".format(x))
        c = await client.read_gatt_char(rw_uuid)
        print('last rw command: ',c)
        count = await client.read_gatt_char(count_uuid)
        count = int.from_bytes(bytes(count), byteorder='little')
        print('count:', count)
        await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())

