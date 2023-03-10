
def check_traits(traits: dict):
    
    for trait in traits.values():
        assert ((type(trait)==int) | (type(trait)==str), '''
        ARC-16 check failed https://arc.algorand.foundation/ARCs/arc-0016
        "traits": {
            "type": "object",
            "description": "Traits (attributes) that can be used to calculate things like rarity. Values may be strings or numbers"
        }
        ''')