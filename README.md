# HyperSim
LED-Simulator for hyperion and open pixel protocol.

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


usage:
```
usage: hypersim [-h] [--num] [--hyperion HYPERION] [--opc_xy OPC_XY] [--opc_yz OPC_YZ] [--opc_xz OPC_XZ]

Simulator for hyperion.

optional arguments:
  -h, --help           show this help message and exit
  --num                show led IDs
  --hyperion HYPERION  hyperion config
  --opc_xy OPC_XY      opc config xy components
  --opc_yz OPC_YZ      opc config yz components
  --opc_xz OPC_XZ      opc config xz components
```

screenshot:

![HyperSim matrix demo](doc/images/demo_matrix.png)
