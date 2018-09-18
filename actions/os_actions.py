#!/usr/bin/env python3

print("Please specialise this file in the top level charm: ")
print("""
import sys
import os_generic_actions

import charm.openstack.CHARM_NAME  # noqa

sys.exit(os_generic_actions.run_action(sys.argv))""")
