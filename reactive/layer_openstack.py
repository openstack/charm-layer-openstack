import charmhelpers.core.hookenv as hookenv
import charmhelpers.core.unitdata as unitdata

import charms_openstack.charm as charm
import charms_openstack.charm.defaults as defaults
import charms.reactive as reactive


@reactive.when_not('charm.installed')
@reactive.when('charms.openstack.do-default-charm.installed')
def default_install():
    """Provide a default install handler

    The instance automagically becomes the derived OpenStackCharm instance.
    The kv() key charmers.openstack-release-version' is used to cache the
    release being used for this charm.  It is determined by the
    default_select_release() function below, unless this is overriden by
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
        hookenv.application_version_set(instance.application_version)
        instance.assess_status()
    reactive.remove_state('run-default-update-status')
