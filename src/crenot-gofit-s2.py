#!/bin/env python3
import asyncio
import logging
from bleak import BleakClient, BleakScanner



###
# class scaleComm:
#  - Implements the communication protocol for the "Crenot Gofit S2" scale
###
class CrenotGofitS2:

    address = None
    client = None

    async def run(self):
        name = "Crenot Gofit S2"
        if not await self.connect(name):
            logging.error(f"Could not connect to scale '{name}'")
            return False
            
        logging.info(f"Connection to scale '{name}' established")

    ###
    # connect()
    #  - discover ble devices
    #  - search for a device with the specified name
    #  - connect to it (if found)
    #    
    #
    # parameters:
    #  - name: name of the scale (e.g. "Crenot Gofit S2")
    #
    # return value:
    #  - True if a scale with the specified name was found and the connection could be established.
    #  - False if no matching device was found or if the connection could not be established.
    ###
    async def connect(self, name):

        logging.info("Discovering BLE devices")
        devices = await BleakScanner.discover()
        for d in devices:
            if d.name == name:
                self.address = d.address
                break
        if self.address == None:
            return False

        logging.info(f"Connecting to scale '{name}'")
        self.client = BleakClient(self.address)
        try:
            await self.client.connect()
            return True
        except Exception as e:
            logging.error("Connect failed with exception", e)
        return False



# Execute when the not initialized from an import statement.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=" - %(levelname)s \t%(message)s")
    asyncio.run(CrenotGofitS2().run())
