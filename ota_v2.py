import asyncio
from bleak import discover

from bleak import BleakClient
from bleak import _logger as logger
from bleak.uuids import uuid16_dict

from consolemenu import *
from consolemenu.items import *

import list
import datetime
import time

service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'
data_uuid = 'fec26ec4-6d71-4442-9f81-55bc21d658d6'


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

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

global g_client, g_total_expected, g_get_idx, g_ready, g_fp_out

@static_vars(packet_index=0, total=0, not_done=True, packet_size=0)
def data_handler(sender, data, client=None, total_expected=0):
    global g_client, g_total_expected, g_get_idx, g_ready, g_fp_out
    if data_handler.total==0:
        # set packet_size with the first packet
        data_handler.packet_size = len(data)
    #  Check if data came over correctly
    #  check packet number, check size
    # print("data_handler client", g_client)
    packet_index_received = int.from_bytes(data[:4], byteorder='little')
    if (g_total_expected-data_handler.total)>= (data_handler.packet_size-4):
        expected_len = data_handler.packet_size
    else:
        expected_len = g_total_expected-data_handler.total + 4

    if (data_handler.packet_index == packet_index_received) and (len(data) == expected_len):
        data_handler.total += len(data) - 4
        print(f'\ridx: {packet_index_received} packet_len:{len(data)} received:{data_handler.total} / {g_total_expected}    ', end='')

        if len(data)>0:
            g_fp_out.write(data[4:])

        # check if done
        if data_handler.total == g_total_expected:
            print("\nDone with xfer")
            # fp_out.close()
            data_handler.not_done = False
        else:

            # not done, request next packet
            data_handler.packet_index += 1
            g_get_idx = data_handler.packet_index
            g_ready = True

            # print('send get_idx: ', get_idx, get_idx.to_bytes(4, byteorder='little'))
            # data_service.write_value(get_idx.to_bytes(4, byteorder='little'))
            # innerloop = asyncio.get_event_loop()
            # innerloop.run_until_complete(
            #     g_client.write_gatt_char(data_uuid, get_idx.to_bytes(4,
            #                                                      byteorder='little'))
            # await g_client.write_gatt_char(data_uuid, get_idx.to_bytes(4,
            #                                                      byteorder='little'))
    else:
        get_idx = data_handler.packet_index
        print("ask for packet {get_idx} again\r\n")
        g_ready = True
        # innerloop = asyncio.get_event_loop()
        # innerloop.run_until_complete(
        #     g_client.write_gatt_char(data_uuid, get_idx.to_bytes(4,
        #                                                      byteorder='little'))
        # )


async def run():
    global g_client, g_total_expected, g_get_idx, g_ready, g_fp_out
    #devices = await discover()
    not_found = True
    while not_found:
        print("Trying to find NIST ET devices")
        et_devices = await list.get_et_list()
        # print(et_devices)

        name = 'NIST-GEN'

        for device in et_devices:
            if device.name == name:
                not_found = False
                break

    print(device.name, device.address)
    # async with BleakClient(device.address) as client:
    if True:
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
        g_total_expected = count<<5;
        total_len = 0
        done_xfer = False
        if count==0:
            done_xfer = True
        else:
            date_suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            g_fp_out = open('raw_'+device.name+'_'+date_suffix+'.bin', 'wb')
        print('*'*40)
        start=time.time()
        # kw = {'client': client, 'total_expected': g_total_expected}
        await client.start_notify(data_uuid, data_handler) # , kw)
        print("Started notify")
        await client.write_gatt_char(rw_uuid, bytearray(b'f'))
        print("sent f")
        g_get_idx = 0
        await client.write_gatt_char(data_uuid, g_get_idx.to_bytes(4,
                                                                 byteorder='little'))
        print("sent 0, for first packet")
        g_ready = False
        while data_handler.not_done:
            if g_ready:
                await client.write_gatt_char(data_uuid, g_get_idx.to_bytes(4,
                                                                 byteorder='little'))
                g_ready = False
            else:
                await asyncio.sleep(0.01)
        await client.stop_notify(data_uuid)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
