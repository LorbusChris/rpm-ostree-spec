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

# Test this module like this
#
# echo '{ "ANSIBLE_MODULE_ARGS": { "subjects": "cloud.qcow2" } }' \
#        | python tests/library/qemu-playbook.py
#

WANT_JSON = True

IDENTITY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEA1DrTSXQRF8isQQfPfK3U+eFC4zBrjur+Iy15kbHUYUeSHf5S
jXPYbHYqD1lHj4GJajC9okle9rykKFYZMmJKXLI6987wZ8vfucXo9/kwS6BDAJto
ZpZSj5sWCQ1PI0Ce8CbkazlTp5NIkjRfhXGP8mkNKMEhdNjaYceO49ilnNCIxhpb
eH5dH5hybmQQNmnzf+CGCCLBFmc4g3sFbWhI1ldyJzES5ZX3ahjJZYRUfnndoUM/
TzdkHGqZhL1EeFAsv5iV65HuYbchch4vBAn8jDMmHh8G1ixUCL3uAlosfarZLLyo
3HrZ8U/llq7rXa93PXHyI/3NL/2YP3OMxE8baQIDAQABAoIBAQCxuOUwkKqzsQ9W
kdTWArfj3RhnKigYEX9qM+2m7TT9lbKtvUiiPc2R3k4QdmIvsXlCXLigyzJkCsqp
IJiPEbJV98bbuAan1Rlv92TFK36fBgC15G5D4kQXD/ce828/BSFT2C3WALamEPdn
v8Xx+Ixjokcrxrdeoy4VTcjB0q21J4C2wKP1wEPeMJnuTcySiWQBdAECCbeZ4Vsj
cmRdcvL6z8fedRPtDW7oec+IPkYoyXPktVt8WsQPYkwEVN4hZVBneJPCcuhikYkp
T3WGmPV0MxhUvCZ6hSG8D2mscZXRq3itXVlKJsUWfIHaAIgGomWrPuqC23rOYCdT
5oSZmTvFAoGBAPs1FbbxDDd1fx1hisfXHFasV/sycT6ggP/eUXpBYCqVdxPQvqcA
ktplm5j04dnaQJdHZ8TPlwtL+xlWhmhFhlCFPtVpU1HzIBkp6DkSmmu0gvA/i07Z
pzo5Z+HRZFzruTQx6NjDtvWwiXVLwmZn2oiLeM9xSqPu55OpITifEWNjAoGBANhH
XwV6IvnbUWojs7uiSGsXuJOdB1YCJ+UF6xu8CqdbimaVakemVO02+cgbE6jzpUpo
krbDKOle4fIbUYHPeyB0NMidpDxTAPCGmiJz7BCS1fCxkzRgC+TICjmk5zpaD2md
HCrtzIeHNVpTE26BAjOIbo4QqOHBXk/WPen1iC3DAoGBALsD3DSj46puCMJA2ebI
2EoWaDGUbgZny2GxiwrvHL7XIx1XbHg7zxhUSLBorrNW7nsxJ6m3ugUo/bjxV4LN
L59Gc27ByMvbqmvRbRcAKIJCkrB1Pirnkr2f+xx8nLEotGqNNYIawlzKnqr6SbGf
Y2wAGWKmPyEoPLMLWLYkhfdtAoGANsFa/Tf+wuMTqZuAVXCwhOxsfnKy+MNy9jiZ
XVwuFlDGqVIKpjkmJyhT9KVmRM/qePwgqMSgBvVOnszrxcGRmpXRBzlh6yPYiQyK
2U4f5dJG97j9W7U1TaaXcCCfqdZDMKnmB7hMn8NLbqK5uLBQrltMIgt1tjIOfofv
BNx0raECgYEApAvjwDJ75otKz/mvL3rUf/SNpieODBOLHFQqJmF+4hrSOniHC5jf
f5GS5IuYtBQ1gudBYlSs9fX6T39d2avPsZjfvvSbULXi3OlzWD8sbTtvQPuCaZGI
Df9PUWMYZ3HRwwdsYovSOkT53fG6guy+vElUEDkrpZYczROZ6GUcx70=
-----END RSA PRIVATE KEY-----
"""

USER_DATA = """#cloud-config
users:
  - default
  - name: root
    ssh_authorized_keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDUOtNJdBEXyKxBB898rdT54ULjMGuO6v4jLXmRsdRhR5Id/lKNc9hsdioPWUePgYlqML2iSV72vKQoVhkyYkpcsjr3zvBny9+5xej3+TBLoEMAm2hmllKPmxYJDU8jQJ7wJuRrOVOnk0iSNF+FcY/yaQ0owSF02Nphx47j2KWc0IjGGlt4fl0fmHJuZBA2afN/4IYIIsEWZziDewVtaEjWV3InMRLllfdqGMllhFR+ed2hQz9PN2QcapmEvUR4UCy/mJXrke5htyFyHi8ECfyMMyYeHwbWLFQIve4CWix9qtksvKjcetnxT+WWrutdr3c9cfIj/c0v/Zg/c4zETxtp standard-test-qcow2
ssh_pwauth: True
chpasswd:
  list: |
    root:foobar
  expire: False
"""

INVENTORY = "localhost ansible_ssh_port=2222 ansible_ssh_host=127.0.0.3 ansible_ssh_user=root ansible_ssh_private_key_file=%s ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'\nexecutor ansible_ssh_host=127.0.0.1 ansible_connection=local"

SSH_CONFIG = """
Host vmcheck
    User root
    Port 2222
    HostName 127.0.0.3
    IdentityFile %s
    UserKnownHostsFile /dev/null
    StrictHostKeyChecking no
"""

def main(argv):

    module = AnsibleModule(argument_spec = {
        "subjects": { "required": True, "type": "str" },
        "log": { "required": False, "type": "str" },
    })

    null = open(os.devnull, 'w')

    directory = tempfile.mkdtemp(prefix="launch-cloud-")

    privkey = os.path.join(directory, "key")
    with open(privkey, 'w') as f:
        f.write(IDENTITY)
    os.chmod(privkey, 0600)

    metadata = os.path.join(directory, "meta-data")
    with open(metadata, 'w') as f:
        f.write("")

    userdata = os.path.join(directory, "user-data")
    with open(userdata, 'w') as f:
        f.write(USER_DATA)

    sshconfig = os.path.join(directory, "ssh-config")
    with open(sshconfig, 'w') as f:
        f.write(SSH_CONFIG % privkey)

    cloudinit = os.path.join(directory, "cloud-init.iso")
    subprocess.check_call(["/usr/bin/genisoimage", "-input-charset", "utf-8",
                           "-volid", "cidata", "-joliet", "-rock", "-quiet",
                           "-output", cloudinit, userdata, metadata], stdout=null)

    log = module.params.get("log") or os.devnull
    artifacts = os.path.dirname(log)

    # Make sure the log directory exists
    try:
        os.makedirs(artifacts)
    except OSError as exc:
        if exc.errno != errno.EEXIST or not os.path.isdir(artifacts):
            raise

    inventory = os.path.join(directory, "inventory")
    with open(inventory, 'w') as f:
        f.write(INVENTORY % privkey)

    pid = os.path.join(directory, "pid")
    subprocess.check_call(["/usr/bin/qemu-system-x86_64", "-m", "1024", module.params["subjects"],
        "-enable-kvm", "-snapshot", "-cdrom", cloudinit,
        "-net", "nic,model=virtio", "-net", "user,hostfwd=tcp:127.0.0.3:2222-:22",
        "-device", "isa-serial,chardev=pts2", "-chardev", "file,id=pts2,path=" + log,
        "-daemonize", "-display", "none", "-pidfile", pid], stdout=null)

    # wait for ssh to come up
    for tries in range(0, 30):
        try:
            subprocess.check_call(["/usr/bin/ansible", "-i", inventory, "localhost", "-m", "ping"],
                                  stdout=null, stderr=null)
            break
        except subprocess.CalledProcessError:
            time.sleep(3)
    else:
        with open(pid, 'r') as f:
            try:
                os.kill(int(f.read().strip()), signal.SIGTERM)
            except OSError:
                pass
        module.fail_json(msg="Couldn't connect to qemu host: {subjects}".format(**module.params))
        return 0

    module.exit_json(changed=True, statedir=directory)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
