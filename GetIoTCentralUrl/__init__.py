import logging
import azure.functions as func
import sys
import sys, getopt
from azure.iot.device.aio import ProvisioningDeviceClient
import asyncio


class Device():
    def __init__(self, scope, device_id, key):
        self.scope = scope
        self.device_id = device_id
        self.key = key

    async def __register_device(self):
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host='global.azure-devices-provisioning.net',
            registration_id=self.device_id,
            id_scope=self.scope,
            symmetric_key=self.key,
        )

        return await provisioning_device_client.register()

    @property
    async def connection_string(self):
        results = await asyncio.gather(self.__register_device())
        registration_result = results[0]
        return (registration_result.registration_state.assigned_hub)


async def main(req: func.HttpRequest) -> func.HttpResponse:

    scope = req.params.get('scope')
    device = req.params.get('deviceid')    
    key = req.params.get('key')

    if scope is None or device is None or key is None:
        return func.HttpResponse(
             "Please pass a IoT Central device scope, deviceId and deviceKey (url encoded) on the query string or in the request body",
             status_code=400
        )

    device = Device(scope, device, key)
    (IoTCentral) = await device.connection_string
    logging.info(IoTCentral)

    if IoTCentral:
        return func.HttpResponse(f"{IoTCentral}")
    else:
        return func.HttpResponse(
             "Please check IoT Central scope, deviceId and deviceKey (url encoded) on the query string or in the request body",
             status_code=400
        )
