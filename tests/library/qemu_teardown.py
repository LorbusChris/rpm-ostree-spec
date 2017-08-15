#!/usr/bin/env python

# XXX: we should move as much of these mods to standard-test-roles

import os
import shutil
import signal
import subprocess
import sys
import tempfile

# HACK: Ansible requires this exact string to be here
from ansible.module_utils.basic import *

WANT_JSON = True

def main(argv):
    module = AnsibleModule(argument_spec = {
        "statedir": { "required": True, "type": "str" },
    })

    directory = module.params["statedir"]

    pid = os.path.join(directory, "pid")

    with open(pid, 'r') as f:
        try:
            os.kill(int(f.read().strip()), signal.SIGTERM)
        except OSError:
            pass

    shutil.rmtree(directory)
    module.exit_json(changed=True)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
