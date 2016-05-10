import sys
import mock


sys.path.append('./lib')
# mock out some charmhelpers libraries as they have apt install side effects
sys.modules['charmhelpers.contrib.openstack.utils'] = mock.MagicMock()
sys.modules['charmhelpers.contrib.network.ip'] = mock.MagicMock()
