# HyperSim
LED-Simulator for hyperion and open pixel control.

This is a python/TK app that can load a [hyperion](https://github.com/tvdzwan/hyperion) config file
or [open-pixel-control/OPC](http://openpixelcontrol.org/) layout file and visualize the LED configuration.
In addition it opens a OPC server where you can feed the virtual LEDs with real color from hyperion/opc client.

Hyperion users have to use the fadecandy driver. (default port is 7890)

hyperion.config.json:
```
"device" :
{
  "name"       : "MyPi",
  "type"       : "fadecandy",
  "output"     : "127.0.0.1"
},
```


command line usage:
```
usage: hypersim [-h] [-n]
                [--hyperion <file> | --opc_xy <file> | --opc_yz <file> | --opc_xz <file>]

Simulator for hyperion.

optional arguments:
  -h, --help         show this help message and exit
  -n, --num          show led IDs
  --hyperion <file>  hyperion config
  --opc_xy <file>    opc config xy components
  --opc_yz <file>    opc config yz components
  --opc_xz <file>    opc config xz components
```

Configuration file can be opened via file menu. LED numbers can be enabled on command line only (ATM).

screenshot:

![HyperSim matrix demo](doc/images/demo_matrix.png)
