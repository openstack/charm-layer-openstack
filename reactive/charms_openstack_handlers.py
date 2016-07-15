# handle the update-status hook for all openstack charms

from __future__ import absolute_import

import charms.reactive as reactive
import charmhelpers.core.hookenv as hookenv

import charms_openstack.charm as charm


@reactive.hook('update-status')
def update_status():
    """Use the update-status hook to run the assess_status() function for the
    unit.

    This runs, via the singleton, the assess_status() on the derived class,
    which is auto-instantiated according the the release.

    To deactivate this function override the assess_status in the derived class
    to a NOP.
    """
    charm.OpenStackCharm.singleton.assess_status()
