import json
import itertools
import sys

# Set up clean output
def print_clean(msg):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

try:
    with open('donne.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print_clean(f"Top level keys: {list(data.keys())}")
    
    if 'metadata' in data:
        print_clean(f"metadata keys: {list(data['metadata'].keys())}")
        if 'all' in data['metadata']:
            print_clean(f"metadata['all'] keys: {list(data['metadata']['all'].keys())}")
            if 'kws' in data['metadata']['all']:
                kws = data['metadata']['all']['kws']
                print_clean(f"Total keywords: {len(kws)}")
                print_clean(f"First 5 kws: {dict(itertools.islice(kws.items(), 5))}")
    
except Exception as e:
    print_clean(f"Error: {e}")
