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
- `screenfx_monitor` pre-define used monitor. Available options are shown at startup for selection if not or wrongly set. The expected value is 0 or bigger.

Additionally per device object, the following key must be set:

- `cutout` the area of the screen mapped to the device, can be one of the following: `left`, `right`, `bottom`, `top`, which represent the according screen border.
