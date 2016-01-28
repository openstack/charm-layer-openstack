"""Classes to support writing re-usable charms in the reactive framework"""

import os
from charmhelpers.contrib.openstack.utils import (
    configure_installation_source,
)
from charmhelpers.core.host import path_hash, service_restart
from charmhelpers.core.hookenv import config, status_set
from charmhelpers.fetch import (
    apt_install,
    apt_update,
    filter_installed_packages,
)

from charm.openstack.ip import PUBLIC, INTERNAL, ADMIN, canonical_url
from contextlib import contextmanager
from collections import OrderedDict
from charmhelpers.contrib.openstack.templating import get_loader
from charmhelpers.core.templating import render


class OpenStackCharm(object):
    """
    Base class for all OpenStack Charm classes;
    encapulates general OpenStack charm payload operations
    """

    packages = []
    """Packages to install"""

    api_ports = {}
    """
    Dictionary mapping services to ports for public, admin and
    internal endpoints
    """

    service_type = None
    """Keystone endpoint type"""

    default_service = None
    """Default service for the charm"""

    restart_map = {}

    def __init__(self):
        self.config = config()
        # XXX It's not always liberty!
        self.release = 'liberty'

    def install(self):
        """
        Install packages related to this charm based on
        contents of packages attribute.
        """
        packages = filter_installed_packages(self.packages)
        if packages:
            status_set('maintenance', 'Installing packages')
            apt_install(packages, fatal=True)

    def api_port(self, service, endpoint_type=PUBLIC):
        """
        Determine the API port for a particular endpoint type
        """
        return self.api_ports[service][endpoint_type]

    def configure_source(self):
        """Configure installation source"""
        configure_installation_source(self.config['openstack-origin'])
        apt_update(fatal=True)

    @property
    def region(self):
        """OpenStack Region"""
        return self.config['region']

    @property
    def public_url(self):
        """Public Endpoint URL"""
        return "{}:{}".format(canonical_url(PUBLIC),
                              self.api_port(self.default_service,
                                            PUBLIC))

    @property
    def admin_url(self):
        """Admin Endpoint URL"""
        return "{}:{}".format(canonical_url(ADMIN),
                              self.api_port(self.default_service,
                                            ADMIN))

    @property
    def internal_url(self):
        """Internal Endpoint URL"""
        return "{}:{}".format(canonical_url(INTERNAL),
                              self.api_port(self.default_service,
                                            INTERNAL))

    @contextmanager
    def restart_on_change(self):
        checksums = {path: path_hash(path) for path in self.restart_map}
        yield
        restarts = []
        for path in self.restart_map:
            if path_hash(path) != checksums[path]:
                restarts += self.restart_map[path]
        services_list = list(OrderedDict.fromkeys(restarts))
        for service_name in services_list:
            service_restart(service_name)

    def render_all_configs(self, adapters):
        self.render_configs(adapters, self.restart_map.keys())

    def render_configs(self, adapters, configs):
        with self.restart_on_change():
            for conf in self.restart_map.keys():
                render(source=os.path.basename(conf),
                       template_loader=get_loader('templates/', self.release),
                       target=conf,
                       context=adapters)

    def restart_all(self):
        for svc in self.restart_map.keys():
            service_restart(svc)


class OpenStackCharmFactory(object):

    releases = {}
    """
    Dictionary mapping OpenStack releases to their associated
    Charm class for this charm
    """

    first_release = "icehouse"
    """
    First OpenStack release which this factory supports Charms for
    """

    @classmethod
    def charm(cls, release=None):
        """
        Get an instance of the right charm for the
        configured OpenStack series
        """
        if release and release in cls.releases:
            return cls.releases[release]()
        else:
            return cls.releases[cls.first_release]()
