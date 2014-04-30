vmware_scripts
==============

vscsiStats.py
-------------

Retrieves vscsiStats using the vSphere 5.5 API.
VMWare vscsiStats is intended for storage performance analysis on ESXi host.


#### Usage


    positional arguments:
      operation             Operation to perform [start|stop|reset|getstats]

    optional arguments:
      -h, --help            show this help message and exit
      -s HOST, --host HOST  Remote host to connect to
      -P PORT, --port PORT  Port to connect on
      -u USER, --user USER  User name to use when connecting to host. Default:
                            root
      -p PASSWORD, --password PASSWORD
                            Password to use when connecting to host
      -o OUTPUT, --output OUTPUT
                            Output to a file
      -d, --display         Print results on standard output even if an output
                            file is specified.


License
-------

BSD 2-Clause license



