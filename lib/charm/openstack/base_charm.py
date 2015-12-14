from charmhelpers.contrib.openstack.utils import (
    configure_installation_source,
)
from charm.openstack.ip import PUBLIC, INTERNAL, ADMIN, canonical_url
from charmhelpers.core.hookenv import config, status_set
from charmhelpers.fetch import (
    apt_install,
    apt_update,
    filter_installed_packages,
)

class OpenStackCharm(object):

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

    def __init__(self):
        self.config = config()

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
        """Get the right charm for the configured OpenStack series"""
        if release and release in cls.releases:
            return cls.releases[release]
        else:
            return cls.releases[cls.first_release]


