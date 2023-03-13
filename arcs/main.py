from algosdk.v2client import algod
from pyteal import compileTeal, Mode
from beaker import sandbox
import arc3, arc19
import subprocess
import json
import pathlib
def ipfs_cid_from_folder(folder: str, upload = False) -> str:
    """
    Compute the (encoded) information byte string corresponding to all the files inside the folder `folder`
    """
    # Use Kubo IPFS command line
    # We don't use --wrap-directory as we are already in a folder
    if upload:
        output = subprocess.run(
            ["ipfs", "add", "--cid-version=1", "--hash=sha2-256", "--recursive", "--quiet", "--ignore=__pycache__", folder],
            capture_output=True
        )
    else:
        output = subprocess.run(
            ["ipfs", "add", "--cid-version=1", "--hash=sha2-256", "--recursive", "--only-hash", "--quiet", "--ignore=__pycache__", folder],
            capture_output=True
        )
    # The CID is the last non-empty line
    text_cid = output.stdout.decode().strip().split("\n")[-1]
    return text_cid


def upload_ipfs_arc3(folder_image: str, nfts_metadata: dict) -> str:
    cid_folder_images = ipfs_cid_from_folder(folder_image, upload=True)
    print("Cid_Image_Folder: " + cid_folder_images)

    url_prefix_images = "ipfs://" + cid_folder_images
    # Check everything is fine
    for nft_metadata in nfts_metadata: 
        current_file = folder_image + nft_metadata["image"]
        image_integrity = arc3.file_integrity(current_file)
        image_mimetype = arc3.file_mimetype(current_file)
        nft_metadata_string = arc3.create_metadata(
            name=nft_metadata["name"], 
            description=nft_metadata["name"], 
            image= url_prefix_images+ "/" + nft_metadata["image"], 
            image_integrity=image_integrity,
            image_mimetype=image_mimetype,
            properties=nft_metadata["properties"],
        )
        with open(folder_json + pathlib.Path(nft_metadata["image"]).stem + '.json', 'w') as json_file:
            json_file.write(nft_metadata_string)


    return ipfs_cid_from_folder(folder_json, upload=True)

def create_acgf_txn_arc_19_arc_3(
        nfts_metadata:dict,
        folder_json: str,
        unitname_prefix: str,
        sender: str,
        manager: str,
        ) -> list:
    cid_folder_metadata = ipfs_cid_from_folder(folder_json, upload=False)
    url_prefix_arc19 = arc19.create_url_from_cid(cid_folder_metadata)
    reserve_address_arc19 = arc19.reserve_address_from_cid(cid_folder_metadata)

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
            sp=sp,
            manager=manager,
            reserve=reserve_address_arc19
        ))
        idx + 1 
    return unsigned_txns_arc_19_arc_3

def create_acgf_txn_arc3(
        nfts_metadata:dict,
        folder_json: str,
        unitname_prefix: str,
        sender: str,
        manager: str,
        reserve: str,
        ) -> list:
    cid_folder_metadata = ipfs_cid_from_folder(folder_json, upload=False)
    url_prefix_arc3 = "ipfs://" + cid_folder_metadata

    print("Cid_Metadata_Folder: " + cid_folder_metadata)
    unsigned_txns_arc_3 = []
    idx=1
    for nft_metadata in nfts_metadata:
        json_file = pathlib.Path(nft_metadata["image"]).stem + '.json'
        with open(folder_json + json_file, "r+") as file1:
            json_metadata = file1.read()
        unsigned_txns_arc_3.append(arc3.create_asset_txn(
            json_metadata=json_metadata,
            unit_name=unitname_prefix + str(idx).zfill(4), # zfill to get ALGO0001 ALGO0002 ... ALGO9999
            asset_name=nft_metadata["name"],
            url= url_prefix_arc3 + "/" + json_file + '#arc3',
            sender=sender,
            sp=sp,
            manager=manager,
            reserve=reserve
        ))
        idx + 1 

    return unsigned_txns_arc_3


if __name__ == "__main__":
    accts = sandbox.get_accounts()
    acct_sender = accts.pop()
    print(f"Sender {acct_sender.address}")

    # ---------INPUT--------- #
    nfts_metadata = [
        {
            "name": "ALGO 1", 
            "description": "Stars", 
            "image": "ALGO_1.png", 
            "properties":{
                "author": "Stephane",
                "traits": {
                    "position": "center",
                    "colors": 4,
                }
            }
        },
        {
            "name": "ALGO 2", 
            "description": "Light", 
            "image": "ALGO_2.jpg", 
            "properties":{
                "author": "Stephane",
                "traits": {
                    "position": "left",
                    "colors": 3,
                }
            }
        },
        {
            "name": "ALGO 3", 
            "description": "Water", 
            "image": "ALGO_3.jpg", 
            "properties":{
                "author": "Stephane",
                "traits": {
                    "position": "center",
                    "colors": 8,
                }
            }
        }
    ]
    
    folder_image = "Collections/Images/"
    folder_json = "Collections/Metadata/"
    unitname_prefix = "ALGO"
    sender = acct_sender.address
    manager = acct_sender.address
    reserve = acct_sender.address
    sp = sandbox.get_algod_client().suggested_params()

    upload_ipfs_arc3(folder_image, nfts_metadata)
    create_acgf_txn_arc3(nfts_metadata, folder_json,unitname_prefix, sender, manager, reserve)

    create_acgf_txn_arc_19_arc_3(nfts_metadata, folder_json,unitname_prefix, sender, manager)