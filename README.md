# pepper2

[![CircleCI](https://circleci.com/gh/trickeydan/pepper2.svg?style=svg)](https://circleci.com/gh/trickeydan/pepper2)
[![Test Coverage](https://api.codeclimate.com/v1/badges/c99dfbefd260764d8875/test_coverage)](https://codeclimate.com/github/trickeydan/pepper2/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/c99dfbefd260764d8875/maintainability)](https://codeclimate.com/github/trickeydan/pepper2/maintainability)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](https://opensource.org/licenses/MIT)
![Bees](https://img.shields.io/badge/bees-110%25-yellow.svg)

Robot Management Daemon

## Dependencies

Some of the dependencies for pepper2 are not available on PyPI.

- D-Bus
  - Tested on 1.12.16+
- [GLib](https://developer.gnome.org/glib/) 2.46+
- [girepository](https://wiki.gnome.org/Projects/GObjectIntrospection) 1.46+
- Python 3.6+
- UDisks2
  - Tested on 2.8.1+
- udiskie or similar automounting daemon that uses udisks2.
  - Tested on 1.7.7

These packages can usually be found on systems with a desktop interface anyway.

[Instructions for setting up a Debian 10 system](docs/DEBIAN.md) are included in this repo.

## Running

There are two programs in this repo, with shared code between them.

- `pepperctl`
    - CLI tool that talks to pepperd over D-Bus.
- `pepperd`
    - Daemon that sits on the System Bus
    - Listens for mount and cleanup events from UDisks
    - Registers the USBs.
    - Triggers run and stop events for USBs, based on a set of conditions.
    
In order to run `pepperd`, we need to tell D-Bus that we have permission to create a service on the System Bus.
This can be done by placing a config file in `/etc/dbus-1/uk.org.j5.pepper2.conf`.
An example config file is included in this repository: [uk.org.j5.pepper2.conf](uk.org.j5.pepper2.conf).

## Usage

`pepperd` should be run in the background as a daemon using systemd.

USB drives should be automounted, and pepper2 will detect the new drive via Udisks.

Usercode `main.py` on the drive will begin execution, `stdout` and `stderr` will be logged to `log.txt`.

- View daemon status: `pepperctl status`
- View usercode status: `pepperctl usercode status`
- Kill usercode: `pepperctl usercode kill`
- Start usercode on already inserted drive: `pepperctl usercode start`
- View live log of usercode: `journalctl -ft pepper2-usercode`

## Future Development

![pepper2 Entity Diagram](docs/pepper2.svg)

The above diagram shows how a typical system using `pepper2` would work.

### Core Components

Core Components are essential to use `pepper2`. They are all included in this repo.

- `pepper2`
    - Python library to interact with `pepper2-daemon`
    - Abstracts D-Bus from the user.
- `pepper2-daemon`
    - Daemon that listens for events from UDisks2.
    - Performs actions based on conditions defined in a config.
        - Manages a usercode process
    - Provides "metadata" that can be accessed.
        - e.g `USERCODE_DIR`, `ARENA`, `START_TRIGGER_STATE`
- `pepper2-cli`
    - Simple wrapper around `pepper2`
    - Allows control of daemon from CLI for debugging and bash scripts.

## Additional Components

- `pepper2-usercode`
    - Common components that may be useful for usercode processes to interact with `pepper2`
    - For example, wait for start.
- `pepper2-leds`
    - Listens to signal events from `pepper2-daemon` and manipulates GPIO pins according to a config.
- `pepper2-servohack`
    - Listens to signal events from `pepper2-daemon` and resets the USB bus. Workaround for [bug in SR SBv4](https://github.com/srobo/servo-v4-fw/issues/7)

## Development Resources

This program makes heavy use of D-Bus, which is not the simplest thing in the world to understand.

- [DBus Overview](https://pythonhosted.org/txdbus/dbus_overview.html)
- [D-Feet](https://github.com/GNOME/d-feet)

## Contributions

This project is released under the MIT Licence. For more information, please see LICENSE.

The CONTRIBUTORS file can be generated by executing CONTRIBUTORS.gen. This generated file contains a list of people who have contributed to Pepper2.

## Etymology

No, it's not version 2.

Spelling is `pepper2`, much like `j5`. No capitals necessary.

![Wouldn't you like to be a pepper too?](https://i.imgur.com/B2BBwz1.gif)
