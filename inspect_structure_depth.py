import json

def print_structure(d, indent=0, max_depth=3):
    if indent > max_depth:
        return
    
    if isinstance(d, dict):
        for k, v in d.items():
            print("  " * indent + str(k))
            if isinstance(v, dict):
                # Check if it looks like year/month structure
                # Don't recurse too deep if many keys
                if len(v) > 12 and indent < max_depth: # heuristic
                     print("  " * (indent+1) + f"... {len(v)} keys ...")
                else:
                    print_structure(v, indent + 1, max_depth)
            elif isinstance(v, list):
                print("  " * (indent+1) + f"[List length: {len(v)}]")

try:
    with open('donne.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        print("--- Metadata keys ---")
        if 'metadata' in data:
            print(f"Metadata top keys: {list(data['metadata'].keys())}")
            if 'year' in data['metadata']:
                print(f"Years in metadata: {list(data['metadata']['year'].keys())}")
                # Check inside a year
                y = list(data['metadata']['year'].keys())[0]
                print(f"Keys inside metadata['year']['{y}']: {list(data['metadata']['year'][y].keys())}")
                if 'loc' in data['metadata']['year'][y]:
                     print(f"Found locations in year {y} metadata! Count: {len(data['metadata']['year'][y]['loc'])}")
            
        print("\n--- Data keys ---")
        if 'data' in data:
            print(list(data['data'].keys()))
            # Check if Data has years
            years = [k for k in data['data'].keys() if k.isdigit()]
            if years:
                y = years[0]
                print(f"Inside Year {y}: {list(data['data'][y].keys())}")
                # And inside month
                m = list(data['data'][y].keys())[0]
                print(f"Inside Month {m}: Type is {type(data['data'][y][m])}")
                if isinstance(data['data'][y][m], dict):
                     print(f"Keys: {list(data['data'][y][m].keys())}")
                elif isinstance(data['data'][y][m], list):
                     print(f"List length: {len(data['data'][y][m])}")
                     if len(data['data'][y][m]) > 0:
                         print(f"First item keys: {data['data'][y][m][0].keys()}")

except Exception as e:
    print(f"Error: {e}")
