import cv2
import numpy as np

from fxmodes.ScreenFX.main import ScreenFXBase


__all__ = ['ScreenFXVideoCapture']


class ScreenFXVideoCapture(ScreenFXBase):
    name = 'ScreenFX (Video Capture)'

    def __init__(self, *args, config, **kwargs):
        self.video_device = cv2.VideoCapture(self.get_video_device(config))

        width = int(self.video_device.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video_device.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.capture_range = {
            'left': 0,
            'top': 0,
            'width': width,
            'height': height,
        }

        super().__init__(*args, config=config, **kwargs)

        self.raw_data = np.zeros([height, width, 3])

        self.start_threads()

    def get_video_device(self, config):
        print('Probing video devices...')
        non_working_devices = []
        dev_port = 0
        working_devices = {}

        while len(non_working_devices) < 6:
            device = cv2.VideoCapture(dev_port)

            if device.isOpened():
                is_reading, img = device.read()
                width = int(device.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(device.get(cv2.CAP_PROP_FRAME_HEIGHT))

                working_devices = {**working_devices, dev_port: f'{width}x{height}'}
            else:
                non_working_devices = [*non_working_devices, dev_port]

            device.release()
            dev_port += 1

        choice = config.get('screenfx_video_device')

        while choice not in working_devices:
            print('ScreenFX requires a video device, but no such key was set in the config.')
            print('Pick a video device please:\n')
            print('---------------------------------------------------')
            for device_number, resolution in working_devices.items():
                print(f'Device {device_number}: {resolution}')

            choice = int(input())

            try:
                working_devices[choice]
            except (IndexError, ValueError):
                print(f'Invalid choice, try again!')

        return choice

    def data_processing(self, *args, **kwargs):
        ret, frame = self.video_device.read()

        self.raw_data = frame
