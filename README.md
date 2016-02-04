# HyperSim
LED-Simulator for hyperion and open pixel control.

This is a python/TK app that can load a [hyperion](https://github.com/tvdzwan/hyperion) config file
or [open-pixel-control/OPC](http://openpixelcontrol.org/) layout file and visualize the LED configuration.
In addition it opens a OPC server where you can feed the virtual LEDs with real color from hyperion/opc client.

## Requirements
- python 3
- Tkinter support (windows: it comes with standard py3 install. Linux: there are packages)
- source of OPC messages like OLA, Hyperion, OPC-Clients
- a json config file with your led layout (e.g. hyperion config, OPC layouts)
- Hyperion: Ensure you have the latest hyperiond

## Usage

### client: Hyperion
use the fadecandy driver. (default port is 7890)

hyperion.config.json:
```
"device" :
{
  "name"       : "MyPi",
  "type"       : "fadecandy",
  "output"     : "127.0.0.1"
},
```
### client: generic OPC

configure your client to your HyperSim IP-address and port 7890
use the same LED-layout as the server.

### server: HyperSim
```
usage: hypersim [-h] [-n] [-c | -r] --hyperion <file> | --opc_xy <file> |
                --opc_yz <file> | --opc_xz <file>] [--led_size <pixel>]

Simulator for hyperion.

optional arguments:
  -h, --help          show this help message and exit
  -n, --num           show led IDs
  -c, --circle        draw led as circle/oval
  -r, --rect          draw led as rect (default)
  --hyperion <file>   hyperion config
  --opc_xy <file>     opc config xy components
  --opc_yz <file>     opc config yz components
  --opc_xz <file>     opc config xz components
  --led_size <pixel>  pixel size of a single led (default: 15)
```

Configuration file can be opened via file menu. LED numbers can be enabled on command line only (ATM).

If all works fine you should see something similar like that:

![HyperSim matrix demo](doc/images/demo_matrix.png)
