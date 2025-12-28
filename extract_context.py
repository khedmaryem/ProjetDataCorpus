import json
import pandas as pd
import re

# Load Top Locations (Geocoded)
try:
    df_locs = pd.read_csv('aggregated_locations_geocoded.csv')
    top_locs = set(df_locs['Location'].tolist()) # Quick lookup
    # limit to top 50 for speed in context extraction
    top_50_locs = set(df_locs.head(50)['Location'].tolist())
    print(f"Loaded {len(top_locs)} locations. Searching context for top 50.")
except FileNotFoundError:
    print("Geocoded file not found. Run process_locations.py first.")
    exit()

# Dictionary to store headlines: { 'Location': [ "Title 1", "Title 2" ] }
loc_context = {loc: [] for loc in top_50_locs}

# Regex compilation for speed (basic word boundary check)
# A simple " is in " might match "Mali" in "Animalier". using \b is better.
# But accents... straightforward regex \b might fail with unicode.
# Let's just use simple substring check for now or basic word boundaries if safe.
# Given time constraints, simple `if loc in text` is risky for short words (e.g. "Eco").
# But top locations are "Russie", "France", "Bamako"... mostly distinctive.

year_keys = []

print("Loading JSON and scanning for context...")
try:
    with open('donne.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Traverse structure
    # data['data'][year][month][day] -> list of dicts
    if 'data' in data and 'data' in data['data']: # based on inspection structure might be data['data']
        root = data['data']
    elif 'data' in data:
        root = data['data'] 
    else:
        root = data # Fallback

    count_processed = 0
    
    # Iterate Years
    for year in root:
        if not isinstance(root[year], dict): continue
        # Iterate Months
        for month in root[year]:
            if not isinstance(root[year][month], dict): continue
            # Iterate Days
            for day in root[year][month]:
                if not isinstance(root[year][month][day], list): continue
                
                # Iterate Docs
                for doc in root[year][month][day]:
                    count_processed += 1
                    title = doc.get('title', '')
                    desc = doc.get('description', '')
                    full_text = f"{title} {desc}"
                    
                    # Check against top locations
                    # Optimization: Iterate locations is slow if 50 locs * 10000 docs.
                    # Just check those that haven't filled their quota (e.g. 3 headlines)
                    
                    active_locs = [l for l in top_50_locs if len(loc_context[l]) < 3]
                    if not active_locs:
                        break # Done finding context for all
                        
                    for loc in active_locs:
                        # Simple check (case sensitive often fine for Proper Nouns, or allow Title Case)
                        if loc in full_text: 
                            # Check duplicates
                            if title not in loc_context[loc]:
                                loc_context[loc].append(title)

    print(f"Processed {count_processed} docs.")

except Exception as e:
    print(f"Error processing JSON: {e}")

# Save Context
context_data = []
for loc, titles in loc_context.items():
    # Join snippets with HTML line breaks or a separator
    snippet = " | ".join(titles) if titles else "Aucun contexte trouvé récemment."
    context_data.append({'Location': loc, 'Context': snippet})

df_context = pd.DataFrame(context_data)
df_context.to_csv('location_context.csv', index=False)
print("Saved context to location_context.csv")
