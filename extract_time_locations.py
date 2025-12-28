import json
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# Load existing geocoded data to reuse coordinates
try:
    existing_df = pd.read_csv('aggregated_locations_geocoded.csv')
    # Create valid dictionary: name -> (lat, lon)
    # Ensure no NaNs
    existing_df = existing_df.dropna(subset=['Latitude', 'Longitude'])
    coord_dict = dict(zip(existing_df['Location'], zip(existing_df['Latitude'], existing_df['Longitude'])))
    print(f"Loaded {len(coord_dict)} existing coordinates.")
except FileNotFoundError:
    coord_dict = {}
    print("No existing coordinates file found.")

# Manually add some known ones if missing (from previous script)
defaults = {
    'Russie': (61.523112, 105.1), 'Ukraine': (48.379889, 31.168139), 'France': (46.232193, 2.209667),
    'Moscou': (55.7558, 37.6173), 'Kiev': (50.4501, 30.5234), 'Chine': (35.8617, 104.1954),
    'Afrique': (9.1021, 18.2812), 'États-Unis': (39.8283, -98.5795)
}
for k, v in defaults.items():
    if k not in coord_dict:
        coord_dict[k] = v

print("Loading data...")
with open('donne.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = []

# Extract from metadata -> year
if 'metadata' in data and 'year' in data['metadata']:
    years = data['metadata']['year']
    for year, year_data in years.items():
        if 'loc' in year_data:
            locs = year_data['loc']
            # Limit to top 50 per year for performance/relevance
            # or keep all if manageable. Let's keep top 100.
            sorted_locs = sorted(locs.items(), key=lambda x: x[1], reverse=True)[:100]
            
            for loc, count in sorted_locs:
                rows.append({'Year': year, 'Location': loc, 'Count': count})

df = pd.DataFrame(rows)
print(f"Extracted {len(df)} rows of yearly location data.")

# Geocode missing
unique_locs = df['Location'].unique()
print(f"Unique locations to ensure coordinates for: {len(unique_locs)}")

geolocator = Nominatim(user_agent="geo_app_analysis_time")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.0)

updated_coords = 0

for loc in unique_locs:
    clean_name = loc.strip().replace('"', '')
    if clean_name not in coord_dict:
        print(f"Geocoding {clean_name}...")
        try:
            location = geocode(clean_name)
            if location:
                coord_dict[clean_name] = (location.latitude, location.longitude)
                updated_coords += 1
            else:
                coord_dict[clean_name] = (None, None) # Mark as not found
        except Exception as e:
            print(f"Error geocoding {clean_name}: {e}")
            coord_dict[clean_name] = (None, None)

# Map back to DF
def get_lat(loc):
    clean = loc.strip().replace('"', '')
    if clean in coord_dict:
        return coord_dict[clean][0]
    return None

def get_lon(loc):
    clean = loc.strip().replace('"', '')
    if clean in coord_dict:
        return coord_dict[clean][1]
    return None

df['Latitude'] = df['Location'].apply(get_lat)
df['Longitude'] = df['Location'].apply(get_lon)

# Drop those without coords
df_final = df.dropna(subset=['Latitude', 'Longitude'])

df_final.to_csv('locations_by_year.csv', index=False)
print(f"Saved {len(df_final)} rows to locations_by_year.csv")

# Also update the Master Geocoded list if we found new ones
# (Optional, but good practice)
