import json
import itertools
import sys

output_file = 'loc_structure_info.txt'

try:
    with open('donne.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(output_file, 'w', encoding='utf-8') as out:
        if 'metadata' in data and 'all' in data['metadata'] and 'loc' in data['metadata']['all']:
            locs = data['metadata']['all']['loc']
            out.write(f"Total locations in metadata['all']['loc']: {len(locs)}\n")
            out.write(f"First 50 locs: {dict(itertools.islice(locs.items(), 50))}\n")
        else:
            out.write("No metadata['all']['loc'] found.\n")

        # Check data['data']
        if 'data' in data:
             out.write(f"data['data'] keys: {list(data['data'].keys())[:20]}\n")
             # It seems data['data'] might be a dict of ids to docs?
             first_key = next(iter(data['data']))
             out.write(f"Sample item from data['data'] (key={first_key}): {str(data['data'][first_key])[:500]}\n")

except Exception as e:
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"Error: {e}\n")
