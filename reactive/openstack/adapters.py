class RabbitMQRelationAdapter(object):

    def __init__(self, rabbitmq):
        self.relation = rabbitmq

    @property
    def rabbitmq_host(self):
        if self.relation.vip():
            return self.relation.vip()
        else:
            return self.relation.private_address()

    @property
    def rabbitmq_hosts(self):
        hosts = self.relation.rabbitmq_hosts()
        if len(hosts) > 1:
            return ','.join(hosts)
        else:
            return None
