import asyncio
import struct
from bleak import BleakScanner
from bleak import BleakClient

import gui

distance_uuid = "00002a57-0000-1000-8000-00805f9b34fb"
humidity_uuid = "00002a6f-0000-1000-8000-00805f9b34fb"
temperature_uuid = "00002a1f-0000-1000-8000-00805f9b34fb"
   
# discover devices
async def discover():
    # search for devices
    devices = await BleakScanner.discover()
    print("Devices detected: ")
    i = 1
    for d in devices:
        print("|", i, "|", d)
        i += 1
    
    # select device to connect to
    num = input("Connect to device: ")
    return devices[int(num)-1]

# connect to device
async def connect(device):
    # connect to selected device
    async with BleakClient(device) as client:
        print(f"Connected to: {device.name}")
    
        try:
            # initialized GUI
            g = gui.GUI()
            # fetch data
            while(g.exit == False):
                data = []
                data.append(byteToFloat(await client.read_gatt_char(temperature_uuid)))
                data.append(byteToFloat(await client.read_gatt_char(humidity_uuid)))
                data.append(byteToFloat(await client.read_gatt_char(distance_uuid)))
                g.updateData(data[0], data[1], data[2])
                
        except Exception as e:
            print("ERROR:", e)
        finally:
            await client.disconnect()


def byteToFloat(arr):
    return struct.unpack('f', arr[0:4])[0]

def printData(arr):
    types = ["temperature", "humidity", "distance"]
    for i in range(3):
        print(types[i], ":", arr[i], end="\t")
    print()

# main program
async def main():
    try:
        device = await discover()
    except e:
        print("ERROR: invalid input")

    await connect(device)

if __name__ == "__main__":
    asyncio.run(main())