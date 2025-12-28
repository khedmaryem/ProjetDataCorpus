import json
import sys

try:
    with open('donne.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("--- Metadata Check ---")
    if 'metadata' in data:
        md = data['metadata']
        if 'year' in md:
            years = list(md['year'].keys())
            print(f"Years found: {years}")
            for y in years:
                if 'loc' in md['year'][y]:
                     locs = md['year'][y]['loc']
                     print(f"Year {y}: {len(locs)} locations found.")
                     # Print top 3 locs for check
                     sorted_locs = sorted(locs.items(), key=lambda x: x[1], reverse=True)[:3]
                     print(f"  Top 3: {sorted_locs}")
        else:
            print("No 'year' key in metadata.")
            
except Exception as e:
    print(f"Error: {e}")
