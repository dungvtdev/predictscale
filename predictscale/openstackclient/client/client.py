from novaclient.client import Client
from novaclient import exceptions

from keystoneauth1.identity import v3
from keystoneauth1 import session

try:
    from . import config as cf
except:
    import config as cf
import time


class OSClient(object):
    _instance = None

    def __init__(self):
        super(OSClient, self).__init__()
        self._setup()

    @classmethod
    def default(cls):
        if OSClient._instance is None:
            OSClient._instance = OSClient()
        return OSClient._instance

    def _setup(self):
        auth = v3.Password(auth_url=cf.auth_url,
                           user_domain_name=cf.user_domain_name,
                           username=cf.username,
                           password=cf.password,
                           project_domain_name=cf.project_domain_name,
                           project_name=cf.project_name)
        sess = session.Session(auth=auth)
        self.client = Client(cf.nova_version, session=sess)

    def _show_server(self, instance_id):
        server = self.client.servers.get(instance_id)
        return server

    def _list_servers(self):
        servers = self.client.servers.list()
        return servers

    def _list_ip(self, instance_id):
        return dict(self.client.servers.ips(instance_id))

    def _list_nic(self, instance_id):
        interfaces = self.client.servers.interface_list(instance_id)
        return interfaces

    def _show(self, instance_id):
        server = self.client.servers.get(
            instance_id
        )
        return server

    def create(self, image_id, flavor_id,
               network_id, name=None, user_data=None, **kargs):
        server = self.client.servers.create(
            name=name,
            image=image_id,
            flavor=flavor_id,
            nics=[{'net-id': network_id},],
            user_data=user_data
        )
        return server

    def _get_new_floating_ip(self, pool_name):
        ips = self.client.floating_ips.list()
        ip = next((ip for ip in ips
                   if ip.pool == pool_name and ip._loaded and ip.instance_id is None), None)
        if ip is None:
            ip = self.client.floating_ips.create(pool_name)
        return ip

    def _associate_public_ip(self, instance_id, public_ip_id, private_ip=None):
        """Associate a external IP"""
        floating_ip = self.client.floating_ips.get(public_ip_id)
        floating_ip = floating_ip.to_dict()
        address = floating_ip.get('ip')

        self.client.servers.add_floating_ip(instance_id, address, private_ip)

        return True

    def create_new_instance(self, name, image_id, flavor_id, net_selfservice_id,
                            provider_name, user_data=None, time_out=None):
        try:
            # create new instance
            server = self.create(image_id=image_id,
                                 flavor_id=flavor_id,
                                 network_id=net_selfservice_id,
                                 name=name,
                                 user_data=user_data)
            timeout = time_out or 20
            while(timeout >= 0):
                time.sleep(1)
                timeout = timeout - 1
                s_status = self._show(server.id)
                if s_status.status == 'ACTIVE':
                    break

            # check floating ip available
            ip = self._get_new_floating_ip(provider_name)
            self._associate_public_ip(server.id, ip.id)
            return {
                'instance_id': server.id,
                'floating_ip': ip.ip,
            }
        except Exception as e:
            print(e)
            return

    def delete(self, instance_id):
        self.client.servers.delete(instance_id)
        return True

    def get_instance_info(self, instance_id):
        status = ['BUILD', 'SHUTOFF', 'ACTIVE', ]
        try:
            s_status = self._show(instance_id)
            ip = None
            for k, v in s_status.addresses.items():
                ip = next(
                    (it['addr'] for it in v if it['OS-EXT-IPS:type'] == 'floating'), None)
                if ip is not None:
                    break
            return {
                'status': s_status.status,
                'ip': ip
            }
        except Exception as e:
            print(e)
