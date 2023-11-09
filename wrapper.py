from outline_vpn.outline_vpn import OutlineVPN
import uuid

def init_client(api_url, cert_sha256):
    client = OutlineVPN(api_url=api_url,
                    cert_sha256=cert_sha256)
    return client

async def create_new_key(client, user_id, limit = 1):
    #key = client.create_key()
    #client.add_data_limit(key.key_id, 1000 * 1000 * limit * 1000)
    #client.rename_key(key.key_id, f"{user_id}_{str(uuid.uuid4())[:5]}")
    return f"я работаю c лимитом {limit}. {user_id}_{str(uuid.uuid4())[:5]}"

