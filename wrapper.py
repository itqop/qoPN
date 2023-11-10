from outline_vpn.outline_vpn import OutlineVPN
import uuid

def init_client(api_url, cert_sha256):

    client_GE = OutlineVPN(api_url=api_url,
                        cert_sha256=cert_sha256)
    clients = {"DE": client_GE}
    return clients

def create_new_key(client, user_id, limit = 1):
    key = client.create_key()
    client.add_data_limit(key.key_id, 1000 * 1000 * int(limit) * 1000)
    name_id = str(uuid.uuid4())[:4]
    client.rename_key(key.key_id, f"{user_id}_{name_id}")
    return key, name_id

async def real_used(client):
    all_keys = {}
    for key in client.get_keys():
        all_keys[key.access_url] = round(key.used_bytes / 1000000000, 2) if key.used_bytes else 0
    return all_keys

async def delete_key(client, key_url):
    for key in client.get_keys():
        if key.access_url == key_url:
            client.delete_key(key.key_id)

