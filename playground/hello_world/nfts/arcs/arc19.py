import re
from multiformats_cid import make_cid
import multihash
from algosdk import encoding
import pathlib
from arcs import arc3

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

def create_acgf_txn(
        client: any, 
        nfts_metadata: dict,
        folder_json: str,
        unitname_prefix: str,
        sender: str,
        manager: str,
        ) -> list:
    cid_folder_metadata = arc3.ipfs_cid_from_folder(folder_json, upload=False)
    url_prefix_arc19 = create_url_from_cid(cid_folder_metadata)
    reserve_address_arc19 = reserve_address_from_cid(cid_folder_metadata)

    print("Cid_Metadata_Folder: " + cid_folder_metadata)
    unsigned_txns_arc_19_arc_3 = []
    idx=1
    for nft_metadata in nfts_metadata:
        json_file = pathlib.Path(nft_metadata["image"]).stem + '.json'
        with open(folder_json + json_file, "r+") as file1:
            json_metadata = file1.read()
        unsigned_txns_arc_19_arc_3.append(arc3.create_asset_txn(
            json_metadata=json_metadata,
            unit_name=unitname_prefix + str(idx).zfill(4), # zfill to get ALGO0001 ALGO0002 ... ALGO9999
            asset_name=nft_metadata["name"],
            url= url_prefix_arc19 + "/" + json_file + '#arc3',
            sender=sender,
            sp=client.suggested_params(),
            manager=manager,
            reserve=reserve_address_arc19,
            metadata_hash=False
        ))
        idx + 1 
    return unsigned_txns_arc_19_arc_3