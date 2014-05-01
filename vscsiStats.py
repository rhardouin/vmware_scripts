#!/usr/bin/env python
#
# The following is a BSD 2-Clause license.
#
# Copyright (c) 2014, Romain Hardouin
#  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Retrieve vscsiStats using the vSphere 5.5 API (not tested with another version).

Require VMWare Vmomi Python bindings (pyVmomi).

"""
from __future__ import print_function
import argparse
import sys


class BadUsageError(Exception):
    pass


def parse_command_line():
    parser = argparse.ArgumentParser(usage='%(prog)s',
                                     description="Retrieve vscsiStats using the vSphere 5.5 API")
    parser.add_argument('-s', '--host', required=True, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-P', '--port', type=int, default=443, action='store', help='Port to connect on')
    parser.add_argument('-u', '--user', required=False, default='root', action='store',
                        help='User name to use when connecting to host. Default: root')
    parser.add_argument('-p', '--password', required=True, action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('-o', '--output', required=False, default=None, action='store',
                        help='Output to a file')
    parser.add_argument('-d', '--display', required=False, default=False, action='store_true',
                        help='Print results on standard output even if an output file is specified. ')
    parser.add_argument('operation', action='store',
                        help='Operation to perform [start|stop|reset|getstats]')
    return parser.parse_args()


def get_vscsi_command_name(operation):
    commands_mapping = {
        'start': 'StartVscsiStats',
        'stop': 'StopVscsiStats',
        'reset': 'ResetVscsiStats',
        'getstats': 'FetchAllHistograms'
    }
    try:
        return commands_mapping[operation.lower()]
    except KeyError:
        raise BadUsageError("Unknown operation: '{}'".format(operation))


if __name__ == '__main__':
    try:
        import pyVim.connect
        from pyVmomi import vmodl
        from pyVmomi import vim
    except ImportError:
        sys.exit("You need to install pyVmomi to run this script.")

    service_instance = None
    try:
        args = parse_command_line()
        service_instance = pyVim.connect.Connect(host=args.host,
                                                 user=args.user,
                                                 pwd=args.password,
                                                 port=int(args.port))
        content = service_instance.RetrieveContent()

        if content.about.apiType != 'HostAgent':
            raise BadUsageError("Script requires connecting directly to an ESXi host (not vCenter)")

        service_mgr = vim.ServiceManager('ha-servicemanager')
        list_view = content.viewManager.CreateListView([service_mgr])
        service_manager = list_view.view[0]
        vscsi_service_info = service_manager.QueryServiceList('VscsiStats')
        vscsi_stats = vscsi_service_info[0].service
        operation = get_vscsi_command_name(args.operation)
        results = vscsi_stats.ExecuteSimpleCommand(arguments=[operation])

        if args.output:
            with open(args.output, 'w') as out:
                out.write(results)
                print("Results written to '{0}'".format(args.output))

            if args.display:
                print(results)
        else:
            print(results)
    except vmodl.MethodFault as e:
        # special case for getaddrinfo to provide a better message
        if 'Errno 11004' in e.msg:
            sys.exit("Cannot connect to host '%s'" % args.host)
        else:
            sys.exit("Caught vmodl fault : %s" % e.msg)
    except BadUsageError as e:
        sys.exit(e)
    finally:
        pyVim.connect.Disconnect(service_instance)
