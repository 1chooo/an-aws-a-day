import base64
import hashlib
import hmac
import os

from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())


def get_signature():
    channel_secret = os.environ["CHANNEL_SECRET"] # Channel secret string
    body = 'test' # Request body string
    hash = hmac.new(channel_secret.encode('utf-8'),
    body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash)
    return signature

signature = get_signature()
# Compare x-line-signature request header and the signature
print(signature)
