class OpenStackRelationAdapter(object):
    """
    Base adapter class for all OpenStack related adapters.
    """

    interface_type = None
    """
    The generic type of the interface the adapter is wrapping.
    """

    def __init__(self, relation):
        self.relation = relation
        self._setup_properties()

    @property
    def relation_name(self):
        """
        Name of the relation this adapter is handling.
        """
        return self._relation.relation_name

    def _setup_properties(self):
        """
        Setup property based accessors for an interfaces
        auto accessors
        """
        for field in self.relation.auto_accessors:
            meth_name = field.replace('-', '_')
            # TODO: see if we can make this dynamic, rather
            #       than making all calls on setup.
            self.__dict__[meth_name] = getattr(self.relation,
                                               meth_name)()


class RabbitMQRelationAdapter(OpenStackRelationAdapter):
    """
    Adapter for the RabbitMQRequires relation interface.
    """

    interface_type = "messaging"

    @property
    def host(self):
        """
        Hostname that should be used to access RabbitMQ.
        """
        if self.vip:
            return self.vip
        else:
            return self.private_address

    @property
    def hosts(self):
        """
        Comma separated list of hosts that should be used
        to access RabbitMQ.
        """
        hosts = self.relation.rabbitmq_hosts()
        if len(hosts) > 1:
            return ','.join(hosts)
        else:
            return None


class OpenStackInterfaceAdapters(object):
    """
    Base adapters class for OpenStack Charms, used to aggregate
    the relations associated with a particular charm so that their
    properties can be accessed using dot notation, e.g:

        adapters.amqp.private_address
    """

    interface_adapters = {}
    """
    Dictionary mapping relation names to adapter classes, e.g:

        interface_adapters = {
            'amqp': RabbitMQRelationAdapter,
        }

    By default, interfaces will be wrapped in an OpenStackRelationAdapter.
    """

    def __init__(self, interfaces):
        for interface in interfaces:
            relation_name = interface.relation_name
            if relation_name in self.interface_adapters:
                self.__dict__[relation_name] = (
                    self.interface_adapters[relation_name](interface)
                )
            else:
                self.__dict__[relation_name] = (
                    OpenStackRelationAdapter(interface)
                )


class TestCharmAdapters(OpenStackInterfaceAdapters):
    """
    Adapters class for the TestCharm charm.
    """

    interface_adapters = {
        'amqp': RabbitMQRelationAdapter,
 }
