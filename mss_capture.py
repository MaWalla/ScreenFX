import numpy as np

from mss import mss
from screeninfo import get_monitors

from fxmodes.ScreenFX.main import ScreenFXBase
from immersivefx import ManagedLoopThread


__all__ = ['ScreenFXMSS']


class ManagedMSSLoopThread(ManagedLoopThread):

    def loop(self, *args, **kwargs):
        with mss() as sct:
            super().loop(*args, **kwargs, sct=sct)


class ScreenFXMSS(ScreenFXBase):
    name = 'ScreenFX (mss)'

    def __init__(self, *args, config, **kwargs):
        monitor = self.get_monitor(config)
        self.capture_range = {
            'left': monitor.x,
            'top': monitor.y,
            'width': monitor.width,
            'height': monitor.height,
        }

        super().__init__(*args, config=config, **kwargs)

        self.raw_data = np.zeros([monitor.height, monitor.width, 4])

        self.start_threads()

    def start_data_thread(self):
        self.data_thread = ManagedMSSLoopThread(
            target=self.data_loop,
            args=(),
            kwargs={},
        )

        self.data_thread.start()

    def get_monitor(self, config):
        """
        Choice menu for the used monitor,
        can also be set statically by setting a "monitor" key in the config.
        """
        monitors = get_monitors()
        try:
            chosen_monitor = monitors[config.get('screenfx_monitor')]
        except (TypeError, IndexError, KeyError):
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

    def data_processing(self, *args, sct=None, **kwargs):
        if self.launch_arguments.single_threaded:
            with mss() as sct:  # this is very inefficient but that doesn't matter for this mode
                self.raw_data = np.array(sct.grab(self.capture_range))

        else:
            self.raw_data = np.array(sct.grab(self.capture_range))

