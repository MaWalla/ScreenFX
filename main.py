import numpy as np

from immersivefx import Core


__all__ = ['ScreenFXBase']


class ScreenFXBase(Core):
    name = 'ScreenFX (Base)'

    target_versions = ['1.2']
    target_platforms = ['all']

    capture_range = {
        'left': 0,
        'top': 0,
        'width': 0,
        'height': 0,
    }
    
    def __init__(self, *args, config, **kwargs):
        # cutouts follow the scheme: lower limit, upper limit, axis
        cutout_presets = {
            'low': {
                'left': (0, int(self.capture_range.get('width') * 0.05), 1),
                'right': (int(self.capture_range.get('width') * 0.95), int(self.capture_range.get('width')), 1),
                'bottom': (int(self.capture_range.get('height') * 0.95), int(self.capture_range.get('height')), 0),
                'top': (0, int(self.capture_range.get('height') * 0.05), 0),
            },
            'medium': {
                'left': (0, int(self.capture_range.get('width') * 0.1), 1),
                'right': (int(self.capture_range.get('width') * 0.9), int(self.capture_range.get('width')), 1),
                'bottom': (int(self.capture_range.get('height') * 0.9), int(self.capture_range.get('height')), 0),
                'top': (0, int(self.capture_range.get('height') * 0.1), 0),
            },
            'high': {
                'left': (0, int(self.capture_range.get('width') * 0.15), 1),
                'right': (int(self.capture_range.get('width') * 0.85), int(self.capture_range.get('width')), 1),
                'bottom': (int(self.capture_range.get('height') * 0.85), int(self.capture_range.get('height')), 0),
                'top': (0, int(self.capture_range.get('height') * 0.15), 0),
            },
            'extreme': {
                'left': (0, int(self.capture_range.get('width') * 0.33), 1),
                'right': (int(self.capture_range.get('width') * 0.67), int(self.capture_range.get('width')), 1),
                'bottom': (int(self.capture_range.get('height') * 0.67), int(self.capture_range.get('height')), 0),
                'top': (0, int(self.capture_range.get('height') * 0.33), 0),
            },
        }

        self.cutouts = {
            **cutout_presets[config.get('screenfx_preset', 'extreme')],
        }
        
        super().__init__(*args, config=config, **kwargs)

        self.devices = self.add_device_cutouts()

    def add_device_cutouts(self):
        screenfx_devices = {}

        devices = self.config.get('devices')

        for name, device_config in self.devices.items():
            cutout = devices.get(name).get('screenfx_cutout')

            if cutout:
                if cutout in self.cutouts:
                    screenfx_devices[name] = {**device_config, 'screenfx_cutout': cutout}
                else:
                    print(f'Device {name} has an invalid cutout. Available cutouts are: {self.cutouts}')
                    exit(1)
            else:
                print(f'Device {name} is missing the cutout key, which is required for ScreenFX though, skipping it.')

        if not screenfx_devices:
            print('ScreenFX is missing valid devices, perhaps none of them have a cutout specified? Exiting...')
            exit(1)

        return screenfx_devices

    def splash(self):
        print('Welcome to ----------------------------------------')
        print('         ██  ██ ██  ███ ███ ██  █ ███ ██ ██        ')
        print('        █   █   █ █ █   █   █ █ █ █    █ █         ')
        print('         █  █   ██  ██  ██  █ █ █ ██    █          ')
        print('          █ █   █ █ █   █   █ █ █ █    █ █         ')
        print('        ██   ██ █ █ ███ ███ █  ██ █   ██ ██        ')
        print('---------------------------------------- by MaWalla')

    def device_processing(self, device, device_instance):
        lower_limit, upper_limit, axis = self.cutouts[device['screenfx_cutout']]

        cutout = np.array_split(
            self.raw_data.take(indices=range(lower_limit, upper_limit), axis=axis)[:, :, :3].mean(axis=axis),
            device_instance.leds,
            axis=0,
        )

        return np.flip(np.array([
            np.array(value.mean(axis=0))
            for value in cutout
        ]), axis=1)
