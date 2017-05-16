try:
    from .client import OSClient
except:
    from client import OSClient
from utils import dumps_object
import time

provider_id = '1e27ffe0-af0c-4275-8c9c-b7d7b102aa57'
selfservice_id = '4c358775-c884-4cba-9280-4525655ebc55'
image_id = '07b28db9-feae-4ea2-9ac2-024c4daae486'
flavor_id = '1'

floating_ip = '1164fad8-26e8-48de-bc4f-77f6ac19766a'

instance_id = 'a55acfb5-6544-481b-870c-a69b98bdbfb2'

if __name__ == '__main__':
    client = OSClient()

    servers = client._list_servers()
    for s in servers:
        info = client.get_instance_info(s.id)
        print(info)

    # server = client._show('2fb873c6-ea1c-43c8-aede-382e912550fa')
    # dumps_object(server)
    # server = client.create(image_id=image_id,
    #                     flavor_id=flavor_id,
    #                     network_id=selfservice_id,
    #                     name='testxxx')
    # dumps_object(server)

    # success = client.associate_public_ip(instance_id, floating_ip)
    # print(success)

    # ip = client.get_new_floating_ip('provider')
    # dumps_object(ip)

    # ips = client.client.floating_ips.list()
    # for ip in ips:
    #     dumps_object(ip)

    # server = client.create_new_instance(name='vm111', image_id=image_id,
    #                                     flavor_id=flavor_id,
    #                                     net_selfservice_id=selfservice_id,
    #                                     provider_name='provider')
    # print(server)

    # time.sleep(2)
    # client.delete(server['instance_id'])