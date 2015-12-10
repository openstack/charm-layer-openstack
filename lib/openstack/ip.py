PUBLIC = 'public'
INTERNAL = 'int'
ADMIN = 'admin'

_address_map = {
    PUBLIC: {
        'config': 'os-public-network',
        'fallback': 'public-address'
    },
    INTERNAL: {
        'config': 'os-internal-network',
        'fallback': 'private-address'
    },
    ADMIN: {
        'config': 'os-admin-network',
        'fallback': 'private-address'
    }

def canonical_url(configs, endpoint_type=PUBLIC):
    '''
    Returns the correct HTTP URL to this host given the state of HTTPS
    configuration, hacluster and charm configuration.

    :configs OSTemplateRenderer: A config tempating object to inspect for
        a complete https context.
    :endpoint_type str: The endpoint type to resolve.

    :returns str: Base URL for services on the current service unit.
    '''
    scheme = 'http'
    if 'https' in configs.complete_contexts():
        scheme = 'https'
    address = resolve_address(endpoint_type)
    if is_ipv6(address):
        address = "[{}]".format(address)
    return '%s://%s' % (scheme, address)
