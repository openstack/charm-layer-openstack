"""Adapter classes and utilities for use with Reactive interfaces"""


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

    @property
    def vhost(self):
        return self.relation.vhost()

    @property
    def username(self):
        return self.relation.username()


class OpenStackRelationAdapters(object):
    """
    Base adapters class for OpenStack Charms, used to aggregate
    the relations associated with a particular charm so that their
    properties can be accessed using dot notation, e.g:

        adapters.amqp.private_address
    """

    relation_adapters = {}
    """
    Dictionary mapping relation names to adapter classes, e.g:

        relation_adapters = {
            'amqp': RabbitMQRelationAdapter,
        }

    By default, relations will be wrapped in an OpenStackRelationAdapter.
    """

    _adapters = {
        'amqp': RabbitMQRelationAdapter,
    }
    """
    Default adapter mappings; may be overridden by relation adapters
    in subclasses.
    """

    def __init__(self, relations):
        self._adapters.update(self.relation_adapters)
        self._relations = []
        for relation in relations:
            relation_name = relation.relation_name
            if relation_name in self._adapters:
                self.__dict__[relation_name] = (
                    self._adapters[relation_name](relation)
                )
            else:
                self.__dict__[relation_name] = (
                    OpenStackRelationAdapter(relation)
                )
            self._relations.append(relation_name)

    def __iter__(self):
        """
        Iterate over the relations presented to the charm.
        """
        for relation in self._relations:
            yield relation, self.__dict__[relation]
