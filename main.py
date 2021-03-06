import numpy as np

from time import time, sleep

from mss import mss
from screeninfo import get_monitors

from immersivefx import Core


class ScreenFX(Core):
    name = 'ScreenFX'

    target_versions = ['1.1']
    target_platforms = ['all']

    def __init__(self, *args, config, **kwargs):
        super().__init__(*args, config=config, **kwargs)

        monitor = self.get_monitor()
        self.monitor_range = {
            'left': monitor.x,
            'top': monitor.y,
            'width': monitor.width,
            'height': monitor.height,
        }

        # raw_data is 3-dimensional here with the screen's pixel_amount of rgb arrays
        self.raw_data = np.zeros([monitor.height, monitor.width, 4])

        # cutouts follow the scheme: lower limit, upper limit, axis
        cutout_presets = {
            'low': {
                'left': (0, int(monitor.width * 0.05), 1),
                'right': (int(monitor.width * 0.95), int(monitor.width), 1),
                'bottom': (int(monitor.height * 0.95), int(monitor.height), 0),
                'top': (0, int(monitor.height * 0.05), 0),
            },
            'medium': {
                'left': (0, int(monitor.width * 0.1), 1),
                'right': (int(monitor.width * 0.9), int(monitor.width), 1),
                'bottom': (int(monitor.height * 0.9), int(monitor.height), 0),
                'top': (0, int(monitor.height * 0.1), 0),
            },
            'high': {
                'left': (0, int(monitor.width * 0.15), 1),
                'right': (int(monitor.width * 0.85), int(monitor.width), 1),
                'bottom': (int(monitor.height * 0.85), int(monitor.height), 0),
                'top': (0, int(monitor.height * 0.15), 0),
            },
        }

        self.cutouts = {
            **cutout_presets[config.get('preset', 'medium')],
        }
        self.devices = self.add_device_cutouts()

        self.start_threads()

    def add_device_cutouts(self):
        screenfx_devices = {}

        devices = self.config.get('devices')

        for name, device_config in self.devices.items():
            cutout = devices.get(name).get('cutout')

            if cutout:
                if cutout in self.cutouts:
                    screenfx_devices[name] = {**device_config, 'cutout': cutout}
                else:
                    print(f'Device {name} has an invalid cutout. If its a custom one, please make sure')
                    print('its specified in custom_cutouts.py')
                    exit(1)
            else:
                print(f'Device {name} is missing the cutout key, which is required for ScreenFX though, skipping it.')

        if not screenfx_devices:
            print('ScreenFX is missing valid devices, perhaps none of them have a cutout specified? Exiting...')
            exit(1)

        return screenfx_devices

    def splash(self):
        print('Welcome to ----------------------------------------')
        print('         ??????  ?????? ??????  ????????? ????????? ??????  ??? ????????? ?????? ??????        ')
        print('        ???   ???   ??? ??? ???   ???   ??? ??? ??? ???    ??? ???         ')
        print('         ???  ???   ??????  ??????  ??????  ??? ??? ??? ??????    ???          ')
        print('          ??? ???   ??? ??? ???   ???   ??? ??? ??? ???    ??? ???         ')
        print('        ??????   ?????? ??? ??? ????????? ????????? ???  ?????? ???   ?????? ??????        ')
        print('---------------------------------------- by MaWalla')

    def get_monitor(self):
        """
        Choice menu for the used monitor,
        can also be set statically by setting a "monitor" key in the config.
        """
        monitors = get_monitors()
        try:
            chosen_monitor = monitors[self.config.get('monitor')]
        except (TypeError, IndexError):
            chosen_monitor = None

        while chosen_monitor not in monitors:
            print('ScreenFX requires a monitor, but no such key was set in the config.')
            print('Pick a monitor please:\n')
            print('---------------------------------------------------')
            for index, monitor in enumerate(monitors):
                print(f'{index}: {monitor.name}')

            choice = input()

            try:
                chosen_monitor = monitors[int(choice)]
            except (IndexError, ValueError):
                print(f'Invalid choice! It must be a number bigger than 0 and smaller than {len(monitors)}, try again!')

        return chosen_monitor

    def data_loop(self, *args, **kwargs):
        if self.launch_arguments.single_threaded:
            with mss() as sct:
                self.raw_data = np.array(sct.grab(self.monitor_range))

        else:
            with mss() as sct:
                while True:
                    start = time()

                    self.raw_data = np.array(sct.grab(self.monitor_range))

                    duration = (time() - start) * 1000

                    if duration > self.frame_sleep:
                        if not self.launch_arguments.no_performance_warnings:
                            print('WARNING: data cycle took longer than frame time!')
                            print(f'frame time: {round(self.frame_sleep, 2)}ms, cycle time: {round(duration, 2)}ms')
                            print('If this happens repeatedly, consider lowering the fps.')
                    else:
                        sleep((self.frame_sleep - duration) / 1000)

    def device_processing(self, device, device_instance):
        lower_limit, upper_limit, axis = self.cutouts[device['cutout']]

        cutout = np.array_split(
            self.raw_data.take(indices=range(lower_limit, upper_limit), axis=axis)[:, :, :3].mean(axis=axis),
            device_instance.leds,
            axis=0,
        )

        return np.flip(np.array([
            np.array(value.mean(axis=0))
            for value in cutout
        ]), axis=1)
