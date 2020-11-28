from hashlib import sha1
from base64 import b64encode


def digest(lines):
    hash = sha1()
    for line in lines:
        hash.update(line.encode("utf8"))
    return b64encode(hash.digest()).decode("utf8")[:7]
