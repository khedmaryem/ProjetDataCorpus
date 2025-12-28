import json
import itertools
import sys

output_file = 'structure_info.txt'

try:
    with open('donne.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"Top level keys: {list(data.keys())}\n")
        
        if 'metadata' in data:
            out.write(f"metadata keys: {list(data['metadata'].keys())}\n")
            if 'all' in data['metadata']:
                out.write(f"metadata['all'] keys: {list(data['metadata']['all'].keys())}\n")
                if 'kws' in data['metadata']['all']:
                    kws = data['metadata']['all']['kws']
                    out.write(f"Total keywords: {len(kws)}\n")
                    out.write(f"First 20 kws: {dict(itertools.islice(kws.items(), 20))}\n")
        
        # Check if there is data outside metadata
        other_keys = [k for k in data.keys() if k != 'metadata']
        if other_keys:
             out.write(f"Other keys found: {other_keys}\n")
             for k in other_keys:
                 out.write(f"Type of data['{k}']: {type(data[k])}\n")
                 if isinstance(data[k], list):
                     out.write(f"Length of data['{k}']: {len(data[k])}\n")
                     if len(data[k]) > 0:
                        out.write(f"First item of data['{k}']: {str(data[k][0])[:200]}\n")

except Exception as e:
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"Error: {e}\n")
