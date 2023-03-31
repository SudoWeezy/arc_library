from algosdk.atomic_transaction_composer import *
from beaker import sandbox
from arcs import arc3
import json
import pathlib


if __name__ == "__main__":
    client = sandbox.get_algod_client()
    accts = sandbox.get_accounts()
    acct_sender = accts.pop() # Replace by your address

    # ---------INPUT--------- #
    
    metadata_file = "metadata.json"
    folder_image = "Collections/Images/"
    folder_json = "Collections/Metadata/"
    unitname_prefix = "ALGO" # UnitName (eg for 1 file : ALGO ->  ALGO0001)
    sender = acct_sender.address
    manager = acct_sender.address
    reserve = acct_sender.address
    upload_ipfs = True
    

    with open(metadata_file, "r") as f: nfts_metadata = json.load(f)
    arc3.upload_ipfs(folder_image, folder_json, nfts_metadata, upload_ipfs)
    txns = arc3.create_acgf_txn(client, nfts_metadata, folder_json,unitname_prefix, sender, manager, reserve)

    for txn in txns:
        txid = client.send_transaction(
            txn.sign(acct_sender.private_key)
        )
        res = transaction.wait_for_confirmation(client, txid, 4)
        print(f"Immutable ARC-3 NFT Created, Asset ID: {res['asset-index']}")