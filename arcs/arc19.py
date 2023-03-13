import re
from multiformats_cid import make_cid
import multihash
from algosdk import encoding

def reserve_address_from_cid(cid:str):
    decoded_cid = multihash.decode(make_cid(cid).multihash)
    reserve_address = encoding.encode_address(decoded_cid.digest)
    assert(encoding.is_valid_address(reserve_address))
    return reserve_address

def version_from_cid(cid:str):
    return make_cid(cid).version

def codec_from_cid(cid:str):
    return make_cid(cid).codec

def hash_from_cid(cid:str):
    return multihash.decode(make_cid(cid).multihash).name

def create_url_from_cid(cid:str):
    version = version_from_cid(cid)
    codec = codec_from_cid(cid)
    hash = hash_from_cid(cid)
    url = "template-ipfs://{ipfscid:" + f"{version}:{codec}:reserve:{hash}" + "}";
    valid = re.compile(r"template-ipfs://{ipfscid:(?P<version>[01]):(?P<codec>[a-z0-9\-]+):(?P<field>[a-z0-9\-]+):(?P<hash>[a-z0-9\-]+)}")
    assert bool(valid.match(url))
    return url