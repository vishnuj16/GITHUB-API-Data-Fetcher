import hashlib
import json

def normalize_and_deduplicate(data):
    # create a set to store the normalized JSON strings
    normalized = set()

    # create a list to store the deduplicated data
    deduplicated = []

    # loop through the data
    for item in data:
        # sort the keys of the item
        item = json.loads(item)
        sorted_keys = sorted(item.keys())
        # create a new dictionary with the sorted keys
        normalized_item = {k: item[k] for k in sorted_keys}

        # convert the normalized item to a JSON string
        normalized_json = json.dumps(normalized_item, sort_keys=True)

        # calculate the SHA-256 hash of the normalized JSON string
        hash = hashlib.sha256(normalized_json.encode()).hexdigest()

        # if the hash is not in the normalized set, add it to the set
        # and add the item to the deduplicated list
        if hash not in normalized:
            normalized.add(hash)
            deduplicated.append(item)
    print("NORMALIZED AND DUPLICATED!\n")

    return deduplicated