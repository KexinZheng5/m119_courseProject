
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
    num1 = input("Temperatur sensor: ")
    num2 = input("Motion sensor: ")
    return devices[int(num1)-1], devices[int(num2)-1]

# get data from temperature sensor
async def getTemperature(device, g):
    # connect to selected device
    async with BleakClient(device) as client:
        print(f"Connected to: {device.name}")
    
        try:
            # fetch data
            while(g.exit == False):
                g.updateTemperature(byteToFloat(await client.read_gatt_char(temperature_uuid)), 
                    byteToFloat(await client.read_gatt_char(humidity_uuid)))
                await asyncio.sleep(0)
        except Exception as e:
            print("ERROR:", e)
        finally:
            await client.disconnect()

# get data from distance sensor
async def getDistance(device, g):
    # connect to selected device
    async with BleakClient(device) as client:
        print(f"Connected to: {device.name}")
    
        try:
            # fetch data
            while(g.exit == False):
                g.updateDistance(byteToFloat(await client.read_gatt_char(distance_uuid)))
                await asyncio.sleep(0)
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
        device1, device2 = await discover()
    except e:
        print("ERROR: invalid input")

    # initialized GUI
    g = gui.GUI()
    await asyncio.gather(getTemperature(device1, g), getDistance(device2, g))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = main()
    loop.run_until_complete(task)