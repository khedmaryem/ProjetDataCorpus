import json
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# --- 1. Load Data from JSON ---
print("Loading donne.json...")
try:
    with open('donne.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    locations_dict = data.get('metadata', {}).get('all', {}).get('loc', {})
    print(f"Found {len(locations_dict)} unique locations.")
except Exception as e:
    print(f"Error loading JSON: {e}")
    locations_dict = {}

if not locations_dict:
    print("No locations found. Exiting.")
    exit()

# Convert to DataFrame
# df_locs = pd.DataFrame(cols=list(locations_dict.items())) # Error line removed
df_locs = pd.DataFrame(list(locations_dict.items()), columns=['Location', 'Count'])
df_locs = df_locs.sort_values(by='Count', ascending=False).reset_index(drop=True)

print("Top 10 locations:")
print(df_locs.head(10))

# --- 2. Existing Coordinates ---
# Copied from app.py to avoid re-geocoding known ones
existing_coords = {
    'Russie': (61.523112, 105.1), 'Ukraine': (48.379889, 31.168139), 'France': (46.232193, 2.209667),
    'Moscou': (55.7558, 37.6173), 'Kiev': (50.4501, 30.5234), 'Chine': (35.8617, 104.1954),
    'Algérie': (28.0339, 1.6596), 'Mali': (17.0, -4.0), 'Maroc': (31.7917, -7.0926),
    'Turquie': (38.9637, 35.2433), 'États-Unis': (39.8283, -98.5795), 'Égypte': (26.8206, 30.8025),
    'Afrique du Sud': (-30.5595, 22.9375), 'Saint-Pétersbourg': (59.9343, 30.3351),
    'Washington': (38.9072, -77.0369), 'Alger': (36.7538, 3.0588), 'Paris': (48.8566, 2.3522),
    'Brésil': (-14.2350, -51.9253), 'Inde': (20.5937, 78.9629), 'Johannesburg': (-26.2041, 28.0473),
    'Bamako': (12.6392, -8.0029), 'Caire': (30.0333, 31.2333), 'Argentine': (-34.6037, -58.3816),
    'Iran': (32.4279, 53.6880), 'Arabie saoudite': (23.8859, 45.0792), 'Émirats arabes unis': (23.4241, 53.8478),
    'Nigeria': (9.0820, 8.6753), 'Sénégal': (14.4974, -14.4524), 'Tunisie': (33.8869, 9.5375),
    'Zimbabwe': (-19.0154, 29.1549), 'Marrakech': (31.6295, -7.9811), 'Comores': (-11.8750, 43.8722),
    'Angola': (-11.2027, 17.8739), 'Burundi': (-3.3731, 29.9189), 'Mozambique': (-18.6657, 35.5296),
    'Rwanda': (-1.9403, 29.8739), 'Zambie': (-13.1339, 27.8493), 'Ouganda': (1.3733, 32.2903),
    'République du Congo': (-0.2280, 15.8277), 'Azerbaïdjan': (40.1431, 47.5769), 'Burkina Faso': (12.2383, -1.8641),
    'Éthiopie': (8.9806, 38.7578), 'Kenya': (-0.0236, 37.9062), 'Pologne': (51.9194, 19.1451),
    'Irak': (33.3152, 43.6062), 'Congo': (-4.0383, 21.7587), 'Abidjan': (5.3180, -4.0083),
    'Belgique': (50.8503, 4.3517), 'Italie': (41.9028, 12.4964), 'Allemagne': (51.1657, 10.4515),
    'Japon': (36.2048, 138.2529), 'Biélorussie': (53.7098, 27.9534), 'Kazakhstan': (48.0196, 66.9237),
    'Kirghizstan': (41.2044, 74.7661), 'Kherson': (46.6354, 32.6181), 'Donetsk': (48.0159, 37.8028),
    'Tbilissi': (41.7151, 44.8271), 'Uruguay': (-32.5228, -55.7658), 'Venezuela': (6.4238, -66.5897),
    'Danemark': (56.2639, 9.5018), 'Royaume-Uni': (55.3781, -3.4360), 'Koupiansk': (49.7225, 37.6083),
    'Krasny Liman': (48.9861, 37.8222), 'Minsk': (53.9045, 27.5615), 'Pékin': (39.9042, 116.4074),
    'Kaliningrad': (54.7065, 20.5110), 'Copenhague': (55.6761, 12.5683), 'Vilnius': (54.6872, 25.2797),
    'Crimée': (45.3453, 34.0000), 'Afghanistan': (33.9391, 67.7099), 'Bangladesh': (23.6850, 90.3563),
    'Indonésie': (-0.7893, 113.9213), 'Mexique': (23.6345, -102.5528), 'Nicaragua': (12.8654, -85.2072),
    'Pakistan': (30.3753, 69.3451), 'Syrie': (34.8021, 38.9968), 'Thaïlande': (15.8700, 100.9925),
    'Okhotsk': (59.3800, 143.3100)
}

# Add 'Afrique' manually as it's a continent often centroid located
existing_coords['Afrique'] = (9.1021, 18.2812) 

# --- 3. Geocode Top Locations ---
# Initialize Geolocator
geolocator = Nominatim(user_agent="geo_app_analysis")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1) # Respect rate limits

results = []

# Focus on Top N locations to save time, users care about most frequent.
# N=50 because users waiting.
TOP_N = 100 

print(f"Processing Top {TOP_N} locations...")

for index, row in df_locs.head(TOP_N).iterrows():
    loc_name = row['Location']
    count = row['Count']
    
    lat, lon = None, None
    
    # Clean name slightly
    clean_name = loc_name.strip().replace('"', '')
    
    if clean_name in existing_coords:
        lat, lon = existing_coords[clean_name]
    else:
        # Try to geocode
        print(f"Geocoding: {clean_name}")
        try:
            location = geocode(clean_name)
            if location:
                lat, lon = location.latitude, location.longitude
                print(f"  Found: {lat}, {lon}")
            else:
                print("  Not found.")
        except Exception as e:
            print(f"  Error: {e}")
            
    if lat is not None and lon is not None:
        results.append({
            'Location': clean_name, # Use cleaned name
            'Count': count,
            'Latitude': lat,
            'Longitude': lon
        })

# Create final DataFrame
df_final = pd.DataFrame(results)

# Save to CSV
output_file = 'aggregated_locations_geocoded.csv'
df_final.to_csv(output_file, index=False)
print(f"Saved {len(df_final)} locations to {output_file}")
