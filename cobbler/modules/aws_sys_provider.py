#!/usr/bin/python

import distutils.sysconfig
import os
import sys

# Needed for accessing other providers.
import cobbler.providers.AWS as aws

plib = distutils.sysconfig.get_python_lib()
mod_path="%s/cobbler" % plib
sys.path.insert(0, mod_path)
from utils import _
import cobbler.templar as templar
from cobbler.cexceptions import CX
import utils


def register():
    return "/var/lib/cobbler/triggers/add/system/post/*"
    #return "/var/lib/cobbler/triggers/install/post/*"


def run(api, args, logger):

    settings = api.settings()

    name = args[0]

    os.system("echo %s > /tmp/my_test" % (args))

    if len(args) > 1 and args[1] != "system":
        return 0

    system = api.find_system(name)
    system = utils.blender(api, False, system)
    os.system("echo 'hi, my name is %s' >> /tmp/blah" % (name))

    aws_conn = aws.SystemAWS()
    aws_conn._run_sys(name,'ami-aecd60c7','dbarcelo-omnia','t1.micro',
            ['quick-start-1'])
    if logger is not None:
        logger.info('spinning up in AWS!')



    return 0
