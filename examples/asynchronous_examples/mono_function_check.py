##automated script to run through all mono functions

import asyncio

import time

import re

from loguru import logger

from horiba_sdk.devices.device_manager import DeviceManager


async def main():
    start_command = input('EzSpec SDK: Press ENTER to search for HORIBA monochromator')
    logfile = open ('mono_log.txt', 'w')
    if start_command == "":
        device_manager = DeviceManager(start_icl=True)
        await device_manager.start()

        if not device_manager.monochromators:
            logger.error('No monochromators found, exiting...')
            await device_manager.stop()
            return
    
        mono = device_manager.monochromators[0]
        await mono.open()

        await mono.home()
        await wait_for_mono(mono)
        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Init successful\n')
        logfile.write('[' + timestr + '] Current wavelength position: ' + str(await mono.get_current_wavelength()) + ' nm\n')

        
        
        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Grating information: \n')
        grating_information = await find_gratings(mono)
        for x in grating_information:
            wlblazepairList = grating_information[x]
            logfile.write('\t' + 'Position : ' + str(x) + '; Grooves/mm: ' + str(wlblazepairList[0]) + '; Blaze: ' + str(wlblazepairList[1]) + '\n')


        logfile.write('[' + timestr + '] Changing grating to first turret position...\n')
        await mono.set_turret_grating(mono.Grating.FIRST)
        await wait_for_mono(mono)
        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Grating set to first position successfully. Performing single grating change to second position...\n')
        await mono.set_turret_grating(mono.Grating.SECOND)
        await wait_for_mono(mono)
        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Single grating change performed successfully. Performing double grating change back to first position...\n')
        await mono.set_turret_grating(mono.Grating.FIRST)
        await wait_for_mono(mono)
        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Double grating change performed successfully.\n')

        async def grating_limits_check():
            current_groove_density = float(0)
            if str(await mono.get_turret_grating() == 'Grating.FIRST'):
                current_groove_density = grating_information[0][0]
            elif str(await mono.get_turret_grating() == 'Grating.SECOND'):
                current_groove_density = grating_information[1][0]
            elif str(await mono.get_turret_grating() == 'Grating.THIRD'):
                current_groove_density = grating_information[2][0]
            max_position = 1200/(current_groove_density) * 1500

            await mono.move_to_target_wavelength(float(max_position))
            await wait_for_mono(mono)
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            logfile.write('[' + timestr + '] ' + str(current_groove_density) + 'gr/mm grating mechanical limit of ' + str(max_position) + ' nm reached. Returning to zero...\n')
            await mono.move_to_target_wavelength(float(0))
            await wait_for_mono(mono)
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            logfile.write('[' + timestr + '] 0 nm position reached. Grating limits checked successfully.\n')
            return

        await grating_limits_check()

        ##accessories
        entrance_mirror_exists = False
        exit_mirror_exists = False
        f_entrance_slit_exists = False
        s_entrance_slit_exists = False
        f_exit_slit_exists = False
        s_exit_slit_exists = False


        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Checking for entrance mirror...\n')
        try:
            await mono.get_mirror_position(mono.Mirror.FIRST)
            entrance_mirror_exists = True
            logfile.write('[' + timestr + '] Entrance mirror found, setting to axial position...\n')
            await mono.set_mirror_position(mono.Mirror.FIRST, mono.MirrorPosition.A)
            await wait_for_mono(mono)
        except:
            logfile.write('[' + timestr + '] Entrance mirror not found\n')

        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Checking for exit mirror...\n')
        try:
            await mono.get_mirror_position(mono.Mirror.SECOND)
            exit_mirror_exists = True
            logfile.write('[' + timestr + '] Exit mirror found, setting to axial position...\n')
            await mono.set_mirror_position(mono.Mirror.SECOND, mono.MirrorPosition.A) 
            await wait_for_mono(mono)
        except:
            logfile.write('[' + timestr + '] Exit mirror not found\n')


        ##front entrance slit check
        logfile.write('[' + timestr + '] Checking for front entrance slit...\n')
        await mono.set_slit_position(mono.Slit.A, 2)
        await wait_for_mono(mono)
        if await mono.get_slit_position_in_mm(mono.Slit.A) == float(2.0):
            f_entrance_slit_exists = True
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            logfile.write('[' + timestr + '] Front entrance slit found, setting to 1mm and checking for side entrance slit...\n')
            await mono.set_slit_position(mono.Slit.A, 1)
        else:
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            logfile.write('[' + timestr + '] Front entrance slit not found, checking for side entrance slit...\n')

        ##side entrance slit check
        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Checking for side entrance slit...\n')
        await mono.set_slit_position(mono.Slit.B, 2)
        await wait_for_mono(mono)
        if await mono.get_slit_position_in_mm(mono.Slit.B) == float(2.0):
            s_entrance_slit_exists = True
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            logfile.write('[' + timestr + '] Side entrance slit found, setting to 1mm and checking for front exit slit...\n')
            await mono.set_slit_position(mono.Slit.B, 1)
        else:
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            logfile.write('[' + timestr + '] Side entrance slit not found, checking for front exit slit...\n')
        ##front exit slit check
        logfile.write('[' + timestr + '] Checking for front exit slit...\n')
        await mono.set_slit_position(mono.Slit.C, 2)
        await wait_for_mono(mono)
        if await mono.get_slit_position_in_mm(mono.Slit.C) == float(2.0):
            f_exit_slit_exists = True
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            logfile.write('[' + timestr + '] Front exit slit found, setting to 1mm and checking for side exit slit...\n')
            await mono.set_slit_position(mono.Slit.C, 1)
        else:
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            logfile.write('[' + timestr + '] Front exit slit not found, checking for side exit slit...\n')
        ##side exit slit check
        logfile.write('[' + timestr + '] Checking for side exit slit...\n')
        await mono.set_slit_position(mono.Slit.D, 2)
        await wait_for_mono(mono)
        if await mono.get_slit_position_in_mm(mono.Slit.D) == float(2.0):
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            s_exit_slit_exists = True
            logfile.write('[' + timestr + '] Side exit slit found, setting to 1mm...\n')
            await mono.set_slit_position(mono.Slit.D, 1)
        else:
            timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
            logfile.write('[' + timestr + '] Side exit slit not found\n')

        ##check front entrance shutter
        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Checking for front entrance shutter...\n')
        if entrance_mirror_exists:
            logfile.write('[' + timestr + '] Setting entrance mirror to axial...\n')    
            await mono.set_mirror_position(mono.Mirror.FIRST, mono.MirrorPosition.A)
            await wait_for_mono(mono)
            try:
                await mono.get_shutter_position()
                await mono.open_shutter()
                asyncio.sleep(1)
                await mono.close_shutter()
                timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
                logfile.write('[' + timestr + '] Front entrance shutter found, opened for 1 second\n')
            except:
                timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
                logfile.write('[' + timestr + '] Front entrance shutter not found\n')
        else:
            try:
                await mono.get_shutter_position()
                await mono.open_shutter()
                asyncio.sleep(1)
                await mono.close_shutter()
                timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
                logfile.write('[' + timestr + '] Front entrance shutter found, opened for 1 second\n')
            except:
                timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
                logfile.write('[' + timestr + '] Front entrance shutter not found\n')

        ##check side entrance shutter
        timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
        logfile.write('[' + timestr + '] Checking for side entrance shutter...\n')
        if entrance_mirror_exists:
            logfile.write('[' + timestr + '] Setting entrance mirror to lateral...\n')            
            await mono.set_mirror_position(mono.Mirror.FIRST, mono.MirrorPosition.B)
            await wait_for_mono(mono)
            try:
                await mono.get_shutter_position()
                await mono.open_shutter()
                asyncio.sleep(1)
                await mono.close_shutter()
                timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
                logfile.write('[' + timestr + '] Side entrance shutter found, opened for 1 second\n')
            except:
                timestr = time.strftime("%Y/%m/%d-%H:%M:%S")
                logfile.write('[' + timestr + '] Side entrance shutter not found\n')
       






async def find_gratings(mono):
    configinfo = (str(await mono.configuration()))
    start_index = configinfo.find('gratings')
    end_index = configinfo.find('mirrors')
    turretinfo = configinfo[start_index : end_index]
    grating_info = str(turretinfo).split("{")
    grating_dict = {}
    position = 0
    for x in grating_info:
        if 'positionIndex' in x:
            WLBlazePair = []
            searchResultWavelength = re.search("'grooveDensity': (.*?), 'positionIndex", x)
            WLBlazePair.append(float(searchResultWavelength.group(1)))
            searchResultBlaze = re.search("'blaze': (.*?), 'grooveDensity'", x)
            WLBlazePair.append(float(searchResultBlaze.group(1)))
            grating_dict[position] = WLBlazePair
            position += 1
    return grating_dict


async def wait_for_mono(mono):
    mono_busy = True
    while mono_busy:
        mono_busy = await mono.is_busy()
        await asyncio.sleep(1)
        logger.info('Mono busy...')
        

if __name__ == '__main__':
    asyncio.run(main())