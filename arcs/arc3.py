import hashlib
import pathlib
import mimetypes
import json
import base64
from algosdk import transaction
import arc16
def file_integrity(filename: str) ->str:
    with open(filename,"rb") as f:
        bytes = f.read() # read entire file as bytes
        readable_hash = hashlib.sha256(bytes).hexdigest();
        return "sha-256" + readable_hash

def file_mimetype(filename: str) ->str:
    extension = pathlib.Path(filename).suffix
    return mimetypes.types_map[extension]

def create_metadata(name:str, 
                    description:str, 
                    image:str, 
                    image_integrity:str, 
                    image_mimetype:str, 
                    properties:dict,
                    decimals=0,
                    background_color="",
                    external_url="",
                    external_url_integrity="",
                    external_url_mimetype="",
                    animation_url="",
                    animation_url_integrity="",
                    animation_url_mimetype="",
                    localization={"uri":"", "default":"", "locales":[]},
                    extra_metadata=""
                    ):
    if "traits" in properties.keys():
        arc16.check_traits(properties["traits"])
    else:
        print("No traits provided")
    assert type(name)==str, '''
        "name": {
            "type": "string",
            "description": "Identifies the asset to which this token represents"
        }
    '''
    assert type(decimals)==int, '''
        "decimals": {
            "type": "integer",
            "description": "The number of decimal places that the token amount should display - e.g. 18, means to divide the token amount by 1000000000000000000 to get its user representation."
        }
    '''
    if decimals != 0: print("If provided, decimals must match the Number of Digits after the Decimal Point of the assets ")
    assert type(description)==str, '''
        "description": {
            "type": "string",
            "description": "Describes the asset to which this token represents"
        }
    '''
    assert type(image)==str, '''
        "image": {
            "type": "string",
            "description": "A URI pointing to a file with MIME type image/* representing the asset to which this token represents. Consider making any images at a width between 320 and 1080 pixels and aspect ratio between 1.91:1 and 4:5 inclusive."
        }
    '''
    assert type(image_integrity)==str, '''
        "image_integrity": {
            "type": "string",
            "description": "The SHA-256 digest of the file pointed by the URI image. The field value is a single SHA-256 integrity metadata as defined in the W3C subresource integrity specification (https://w3c.github.io/webappsec-subresource-integrity)."
        }
    '''
    assert type(image_mimetype)==str, '''
        "image_mimetype": {
            "type": "string",
            "description": "The MIME type of the file pointed by the URI image. MUST be of the form 'image/*'."
        }
    '''
    assert type(background_color)==str, '''
        "background_color": {
            "type": "string",
            "description": "Background color do display the asset. MUST be a six-character hexadecimal without a pre-pended #."
        }
    '''
    if (image!=""):
        assert (image_integrity!=""), '''
        image_integrity not provided, you can get it with "arc3.file_integrity(path_to_file)"
        '''
        assert (image_mimetype!=""), '''
        image_mimetype not provided, you can get it with "arc3.file_mimetype(path_to_file)"
    '''
    assert type(external_url)==str, '''
        "external_url": {
            "type": "string",
            "description": "A URI pointing to an external website presenting the asset."
        }
    '''
    assert type(external_url_integrity)==str, '''
        "external_url_integrity": {
            "type": "string",
            "description": "The SHA-256 digest of the file pointed by the URI external_url. The field value is a single SHA-256 integrity metadata as defined in the W3C subresource integrity specification (https://w3c.github.io/webappsec-subresource-integrity)."
        }
    '''
    assert type(external_url_mimetype)==str, '''
        "external_url_mimetype": {
            "type": "string",
            "description": "The MIME type of the file pointed by the URI external_url. It is expected to be 'text/html' in almost all cases."
        }
    '''
    assert type(animation_url)==str, '''
        "animation_url": {
            "type": "string",
            "description": "A URI pointing to a multi-media file representing the asset."
        }
    '''
    assert type(animation_url_integrity)==str, '''
        "animation_url_integrity": {
            "type": "string",
            "description": "The SHA-256 digest of the file pointed by the URI external_url. The field value is a single SHA-256 integrity metadata as defined in the W3C subresource integrity specification (https://w3c.github.io/webappsec-subresource-integrity)."
        }
    '''
    assert type(animation_url_mimetype)==str, '''
        "animation_url_mimetype": {
            "type": "string",
            "description": "The MIME type of the file pointed by the URI animation_url. If the MIME type is not specified, clients MAY guess the MIME type from the file extension or MAY decide not to display the asset at all. It is STRONGLY RECOMMENDED to include the MIME type."
        }
    '''
    if animation_url!="":
        assert (animation_url_integrity!=""), '''
        animation_url_integrity not provided, you can get it with "arc3.file_integrity(path_to_file)"
        '''
        assert (animation_url_mimetype!=""), '''
        animation_url_mimetype not provided, you can get it with "arc3.file_mimetype(path_to_file)"
        ''' 
    

    assert type(properties)==dict, '''
        "properties": {
            "type": "object",
            "description": "Arbitrary properties (also called attributes). Values may be strings, numbers, object or arrays."
        },
    '''
    assert type(extra_metadata)==str, '''
        "extra_metadata": {
            "type": "string",
            "description": "Extra metadata in base64. If the field is specified (even if it is an empty string) the asset metadata (am) of the ASA is computed differently than if it is not specified."
        }
    '''
    assert (type(localization)==dict) & \
    (type(localization["uri"])==str) & \
    (type(localization["default"])==str) & \
    (type(localization["locales"])==list) , '''
        "localization": {
            "type": "object",
            "required": ["uri", "default", "locales"],
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "The URI pattern to fetch localized data from. This URI should contain the substring `{locale}` which will be replaced with the appropriate locale value before sending the request."
                },
                "default": {
                    "type": "string",
                    "description": "The locale of the default data within the base JSON"
                },
                "locales": {
                    "type": "array",
                    "description": "The list of locales for which data is available. These locales should conform to those defined in the Unicode Common Locale Data Repository (http://cldr.unicode.org/)."
                },
                "integrity": {
                    "type": "object",
                    "patternProperties": {
                        ".*": { "type": "string" }
                    },
                    "description": "The SHA-256 digests of the localized JSON files (except the default one). The field name is the locale. The field value is a single SHA-256 integrity metadata as defined in the W3C subresource integrity specification (https://w3c.github.io/webappsec-subresource-integrity)."
                }
            }
        }
    '''
    if (localization!={"uri":"", "default":"", "locales":[]}): print('''
    If the JSON Metadata file contains a localization attribute, its content MAY be used to provide localized values for fields that need it. The localization attribute should be a sub-object with three REQUIRED attributes: uri, default, locales, and one RECOMMENDED attribute: integrity. If the string {locale} exists in any URI, it MUST be replaced with the chosen locale by all client software.
    It is RECOMMENDED that integrity contains the digests of all the locales but the default one.
    ''')
    args = locals()
    metadata_dict = {}
    for key in args.keys():
        if (type(args[key])==str) & (args[key]==""):
            pass
        elif ((key=="localization") & (args[key]=={"uri":"", "default":"", "locales":[]})):
            pass
        elif ((key=="decimals") & (args[key]==0)):
            pass
        elif ((key=="traits")):
            pass
        else:
            metadata_dict[key] = args[key]
    return json.dumps(metadata_dict, indent=4)

def create_asset_txn(
        json_metadata:str,
        sender:str,
        sp:object,
        unit_name:str,
        asset_name:str,
        url:str,
        manager:str,
        reserve:str,
        freeze="",
        clawback="",
        note="",
        decimals=0,
        total=1,
        default_frozen=False,
        lease="",
        rekey_to=""
        ):

    metadata = json.loads(json_metadata)

    
    if ("extra_metadata" in metadata.keys()):
        h = hashlib.new("sha512_256")
        h.update(b"arc0003/amj")
        h.update(json_metadata.encode("utf-8"))
        json_metadata_hash = h.digest()

        h = hashlib.new("sha512_256")
        h.update(b"arc0003/am")
        
        h.update(json_metadata_hash)
        h.update(base64.b64decode(metadata["extra_metadata"]))
        am = h.digest()
    else:
        h = hashlib.new("sha256")
        h.update(json_metadata.encode("utf-8"))
        am = h.digest()
    
    assert(url[:4]=="#arc3", '''
    
    ''')
    assert(total%10 == 0, '''
    Total Number of Units (t) MUST be a power of 10 larger than 1: 10, 100, 1000, ...
    ''')

    assert(decimals * total == 1, '''
    Number of Digits after the Decimal Point (dc) MUST be equal to the logarithm in base 10 of total number of units.
    In other words, the total supply of the ASA is exactly 1.
    ''')


    transaction_dict = {
        "sender": sender,
        "sp": sp,
        "total": total,
        "decimals": decimals,
        "default_frozen": default_frozen,
        "manager": manager,
        "reserve": reserve,
        "freeze": freeze,
        "clawback": clawback,
        "unit_name": unit_name,
        "asset_name": asset_name,
        "url": url,
        "metadata_hash": am,
        "note": note,
        "lease": lease,
        "rekey_to": rekey_to
    }
    return(transaction.AssetCreateTxn(**transaction_dict))

