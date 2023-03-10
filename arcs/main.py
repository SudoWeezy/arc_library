from algosdk.v2client import algod
from pyteal import compileTeal, Mode
from beaker import sandbox
import arc3, arc19, arc16
import subprocess
import json
import pathlib
def ipfs_folder_cid(folder: str, upload = False) -> str:
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


def demo():
    accts = sandbox.get_accounts()
    acct_sender = accts.pop()
    print(f"Sender {acct_sender.address}")

    # ---------INPUT---------
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
    # ---------INPUT---------




    url_prefix_image = ipfs_folder_cid(folder_image, upload=True)
    print("Cid_Image_Folder: " + url_prefix_image)
    # Check everything is fine
    for nft_metadata in nfts_metadata: 
        current_file = folder_image + nft_metadata["image"]
        image_integrity = arc3.file_integrity(current_file)
        image_mimetype = arc3.file_mimetype(current_file)
        nft_metadata_string = arc3.create_metadata(
            name=nft_metadata["name"], 
            description=nft_metadata["name"], 
            image= "ipfs:/" + url_prefix_image + "/" + nft_metadata["image"], 
            image_integrity=image_integrity,
            image_mimetype=image_mimetype,
            properties=nft_metadata["properties"],
            # extra_metadata="iHcUslDaL/jEM/oTxqEX++4CS8o3+IZp7/V5Rgchqwc="
        )
        with open(folder_json + pathlib.Path(nft_metadata["image"]).stem + '.json', 'w') as json_file:
            json_file.write(nft_metadata_string)
            # json.dump(nft_metadata_string, json_file, indent=4)
    url_prefix_json = ipfs_folder_cid(folder_json, upload=True)
    print("Cid_Metadata_Folder: " + url_prefix_json)
    unsigned_txns = []
    idx=1
    for nft_metadata in nfts_metadata:
        json_file = pathlib.Path(nft_metadata["image"]).stem + '.json'
        f = open(folder_json + json_file)
        dict_metadata = json.load(f)
        with open(folder_json + json_file, "r+") as file1:
        # Reading from a file
            str_metadata = file1.read()
        sp = sandbox.get_algod_client().suggested_params()
        unsigned_txns.append(arc3.create_asset_txn(
            dict_metadata=dict_metadata,
            str_metadata=str_metadata,
            unit_name=unitname_prefix + str(idx).zfill(4), # zfill to get ALGO0001 ALGO0002 ... ALGO9999
            asset_name=nft_metadata["name"],
            url="ipfs://" + url_prefix_json + "/" + json_file + '#arc3',
            sender=sender,
            sp=sp,
            manager=manager,
            reserve=reserve
        ))
        idx + 1 
    print(unsigned_txns)


if __name__ == "__main__":
    demo()