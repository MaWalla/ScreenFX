# ScreenFX

FXMode which captures the screen and maps zones in it to LED strips.

## Compatibility

In theory, everything supported by MSS should work. I only tested Linux wih X11 though.

## Requirements

[ImmersiveFX](https://github.com/MaWalla/ImmersiveFX)

## Installation

Since this comes as a submodule for ImmersiveFX already, follow the installation steps over there to get it working. ^^

## Configuration

additionally to the config done in the ImmersiveFX README, the following keys can be set in `config.json`:

- `screenfx_preset` can be either `low`, `medium` or `high`. Higher values capture more area but are more expensive to calculate. Defaults to `medium`. Only affects the provided cutouts below.
- `screenfx_monitor` pre-define used monitor for mss. Available options are shown at startup for selection if not or wrongly set. The expected value is 0 or bigger.
- `screenfx_video_device` pre-define video device. Available options are shown at startup for selection if not or wrongly set. The expected value is 0 or bigger.

Additionally per device object, the following key must be set:

- `cutout` the area of the screen mapped to the device, can be one of the following: `left`, `right`, `bottom`, `top`, which represent the according screen border.

## Using with Wayland

ScreenFX (Video Capture) can be used to process Wayland screens. This needs some preparation though:
1. install `v4l2loopback`. The package name for Arch Linux is `v4l2loopback-dkms`
2. run `sudo modprobe v4l2loopback`
    - hint: to persist it, create a file `/etc/modules-load.d/v4l2loopback.conf` with the content `v4l2loopback`
3. install `obs-studio` and run it
4. You should be able to add a capture source named something like `Screen Capture (PipeWire)`
5. (optional) In the bottom right corner under Settings > Video, you can scale down the output resolution which can greatly improve performance
6. In the bottom left corner you can start the virtual webcam which is then available to ScreenFX (Video Device)