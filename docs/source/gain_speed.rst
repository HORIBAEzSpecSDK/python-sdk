==============
Gain and Speed
==============

The gain and speed of the CCD depend which sensor model is installed in the camera. 
In essence, only the camera itself knows which speed and gain settings it supports.

In order to determine the available gains and speeds of the CCD, the config of the ccd has to be retrieved:

.. code:: python

   import asyncio

   from horiba_sdk.devices.device_manager import DeviceManager


   async def main():
       device_manager = DeviceManager(start_icl=True)
       await device_manager.start()

       if not device_manager.charge_coupled_devices:
           print('No CCDs found, exiting...')
           await device_manager.stop()
           return

       with device_manager.charge_coupled_devices[0] as ccd:
           configuration = ccd.get_configuration()

       await device_manager.stop()

       print('------ Configuration ------')
       print(f'Gains: {configuration["Gains"]}')
       print(f'Speeds: {configuration["Speeds"]}')


   if __name__ == '__main__':
       asyncio.run(main())

.. note:: You can also find this example in the file :code:`examples/asynchronous_examples/gain_speed_info.py`

Once you run the code above, you will get the following information:

.. code:: txt

   [...]

   ------ Configuration -----
   Gains: [{'Info': 'High Sensitivity', 'Token': 2}, {'Info': 'Best Dynamic Range', 'Token': 1}, {'Info': 'High Light', 'Token': 0}
   Speeds: [{'Info': '500 kHz Wrap', 'Token': 127}, {'Info': ' 1 MHz Ultra ', 'Token': 2}, {'Info': ' 1 MHz       ', 'Token': 1}, {'Info': '45 kHz       ', 'Token': 0}]

.. warning:: Remember those are example values!

Based on this information you can create your own gain and speed classes as follows:

.. code:: python

  from enum import Enum
  from typing import final


  @final
  class Gain:
      class SyncerityOE(Enum):
          HIGH_LIGHT = 0
          BEST_DYNAMIC_RANGE = 1
          HIGH_SENSITIVITY = 2

  @final
  class Speed:
      class SyncerityOE(Enum):
          _45_KHZ = 0
          _1_MHZ = 1
          _1_MHZ_ULTRA = 2
          _500_KHZ_WRAP = 127

.. important:: You need to give the correct values to the enums based on the information retrieved from the config of the CCD.

You can then call the speed and gain functions as follows:

.. code:: python

   from horiba_sdk.devices.device_manager import DeviceManager
   from horiba_sdk.devices.ccd import ChargeCoupledDevice
   # assuming you have the Gain and Speed classes defined as above in a file called gain_speed.py
   from gain_speed import Gain, Speed

   async def main():
       device_manager = DeviceManager(start_icl=True)
       await device_manager.start()

       if not device_manager.charge_coupled_devices:
           print('No CCDs found, exiting...')
           await device_manager.stop()
           return

       with device_manager.charge_coupled_devices[0] as ccd:
           await ccd.set_gain(Gain.SyncerityOE.HIGH_SENSITIVITY.value)
           await ccd.set_speed(Speed.SyncerityOE._1_MHZ.value)
           # ...

       await device_manager.stop()
