# You feel like an artist? - Art-NFT Collection on Algorand

This repository allows you to easily create your own art-NFT collection on the Algorand blockchain. To get started, follow the steps below.

## Adding Images

To add images to your collection, simply place them in the `Collections/Images` folder.

## Updating Metadata
To update the metadata for your NFT collection, edit the `metadata.json` file. This file contains information such as the name, description, and image for each NFT.
>Eg for one NFT:
```
[
    {
        "name": "ALGO 1", 
        "description": "Stars", 
        "image": "ALGO_1.png", 
        "properties":{
            "author": "Stephane",
            "traits": {
                "position": "center",
                "colors": 4
            }
        }
    }
]
```

## Creating Immutable NFTs

To create an immutable NFT (ARC-3), run the following command:

```console
python immutable_nft.py
```

## Creating Mutable NFTs

To create an immutable NFT (ARC-3 + ARC-19), run the following command:

```console
python mutable_nft.py
```