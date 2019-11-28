import charms.reactive as reactive

import charmhelpers.core.unitdata as unitdata

import charms_openstack.charm as charm
import charms_openstack.charm.defaults as defaults


@reactive.when_not('charm.installed')
@reactive.when('charms.openstack.do-default-charm.installed')
def default_install():
    """Provide a default install handler

    The instance automagically becomes the derived OpenStackCharm instance.
    The kv() key charmers.openstack-release-version' is used to cache the
    release being used for this charm.  It is determined by the
    default_select_release() function below, unless this is overridden by
    the charm author
    """
    unitdata.kv().unset(defaults.OPENSTACK_RELEASE_KEY)
    with charm.provide_charm_instance() as instance:
        instance.install()
    reactive.set_state('charm.installed')


@reactive.when('config.changed',
               'charms.openstack.do-default-config.changed')
def default_config_changed():
    """Default handler for config.changed state from reactive.  Just see if
    our status has changed.  This is just to clear any errors that may have
    got stuck due to missing async handlers, etc.
    """
    with charm.provide_charm_instance() as instance:
        instance.config_changed()
        instance.assess_status()


@reactive.hook('upgrade-charm')
def default_upgrade_charm():
    """Default handler for the 'upgrade-charm' hook.
    This calls the charm.singleton.upgrade_charm() function as a default.
    """
    reactive.set_state('run-default-upgrade-charm')


@reactive.when('charms.openstack.do-default-upgrade-charm',
               'run-default-upgrade-charm')
def run_default_upgrade_charm():
    with charm.provide_charm_instance() as instance:
        instance.upgrade_charm()
    reactive.remove_state('run-default-upgrade-charm')


@reactive.hook('update-status')
def default_update_status():
    """Default handler for update-status state.
    Just call update status.
    """
    reactive.set_state('run-default-update-status')


@reactive.when('charms.openstack.do-default-update-status',
               'run-default-update-status')
def run_default_update_status():
    with charm.provide_charm_instance() as instance:
        instance.assess_status()
    reactive.remove_state('run-default-update-status')


@reactive.when('storage-backend.connected',
               'charms.openstack.do-default-storage-backend.connected')
def run_storage_backend():
    with charm.provide_charm_instance() as instance:
        instance.send_storage_backend_data()


# Series upgrade hooks are a special case and reacting to the hook directly
# makes sense as we may not want other charm code to run
@reactive.hook('pre-series-upgrade')
def default_pre_series_upgrade():
    """Default handler for pre-series-upgrade.
    """
    with charm.provide_charm_instance() as instance:
        instance.series_upgrade_prepare()


@reactive.hook('post-series-upgrade')
def default_post_series_upgrade():
    """Default handler for post-series-upgrade.
    """
    with charm.provide_charm_instance() as instance:
        instance.series_upgrade_complete()


@reactive.when('certificates.available',
               'charms.openstack.do-default-certificates.available')
def default_request_certificates():
    """When the certificates interface is available, this default handler
    requests TLS certificates.
    """
    tls = reactive.endpoint_from_flag('certificates.available')
    with charm.provide_charm_instance() as instance:
        for cn, req in instance.get_certificate_requests().items():
            tls.add_request_server_cert(cn, req['sans'])
        tls.request_server_certs()
        instance.assess_status()


@reactive.when('charms.openstack.do-default-certificates.available')
@reactive.when_any(
    'certificates.ca.changed',
    'certificates.certs.changed')
def default_configure_certificates():
    """When the certificates interface is available, this default handler
    updates on-disk certificates and switches on the TLS support.
    """
    tls = reactive.endpoint_from_flag('certificates.available')
    with charm.provide_charm_instance() as instance:
        instance.configure_tls(tls)
        # make charms.openstack required relation check happy
        reactive.set_flag('certificates.connected')
        for flag in 'certificates.ca.changed', 'certificates.certs.changed':
            if reactive.is_flag_set(flag):
                reactive.clear_flag(flag)
        instance.assess_status()


@reactive.when('charms.openstack.do-default-config-rendered')
@reactive.when_not('config.rendered')
def default_config_not_rendered():
    """Disable services until charm code has set the config.rendered state."""
    with charm.provide_charm_instance() as instance:
        instance.disable_services()
        instance.assess_status()


@reactive.when('charms.openstack.do-default-config-rendered',
               'config.rendered')
def default_config_rendered():
    """Enable services when charm code has set the config.rendered state."""
    with charm.provide_charm_instance() as instance:
        instance.enable_services()
        instance.assess_status()
