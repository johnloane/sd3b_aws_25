from Cryptodome.Cipher import AES
from pubnub.configuration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.crypto import PubNubCryptoModule, AesCbcCryptoModule, LegacyCryptoModule
from pubnub.models.consumer.v3.channel import Channel
from pubnub.models.consumer.v3.group import Group
from pubnub.models.consumer.v3.uuid import UUID
import os

cipher_key = os.getenv("PUBNUB_CIPHER_KEY")

pn_config = PNConfiguration()
pn_config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
pn_config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
pn_config.uuid = os.getenv("PUBNUB_UUID")
pn_config.secret_key = os.getenv("PUBNUB_SECRET_KEY")
pn_config.cipher_key = cipher_key
pn_config.cipher_mode = AES.MODE_GCM
pn_config.fallback_cipher_mode = AES.MODE_CBC
pn_config.crypto_module = AesCbcCryptoModule(pn_config)

pubnub = PubNub(pn_config)

pi_channel = "johns_pi_channel"

def grant_read_access(user_id):
    envelope = pubnub.grant_token()\
    .channels([Channel.id(channel).read() for channel in (pi_channel)])\
    .authorized_user(user_id)\
    .ttl(60)\
    .sync()
    return envelope.result.token
    
    
def grant_write_access(user_id):
    envelope = pubnub.grant_token()\
    .channels([Channel.id(channel).read() for channel in (pi_channel)])\
    .authorized_user(user_id)\
    .ttl(60)\
    .sync()
    return envelope.result.token


def grant_read_and_write_access(user_id):
    envelope = pubnub.grant_token()\
    .channels([Channel.id(channel).read().write() for channel in (pi_channel)])\
    .authorized_user(user_id)\
    .ttl(60)\
    .sync()
    return envelope.result.token

def revoke_token(token):
    envelope = pubnub.revoke_token(token)
    

def parse_token(token):
    token_details = pubnub.parse_token(token)
    print(token_details)
    read_access = token_details["resources"]["channels"]["johns_pi_channel"]["read"]
    write_access = token_details["resources"]["channels"]["johns_pi_channel"]["write"]
    uuid = token_details['authorized_uuid']
    return token_details['timestamp'], token_details["ttl"], uuid, read_access, write_access

