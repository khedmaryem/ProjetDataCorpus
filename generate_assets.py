import pandas as pd
import io
import re
import matplotlib.pyplot as plt
import altair as alt
import numpy as np

# --- 1. Données Brutes (Incluses dans le script pour la reproductibilité) ---
data_lines = [
    "L’Afrique,151", "SPIEF).Les pays africains,1", "Afrique,2237", "France,2663", "Adossée,1", "État,1400",
    "Eco,5", "Algérie,1287", "Moscou,2647", '"Algérie""",9', "Russie,8326", "Alger,330", "fennecs,1",
    "BRICS.Visite,2", "État de TebbouneAu,2", "Arménie,70", "Biélorussie,230", "Kazakhstan,96", "Kirghizstan,28",
    "Kremlin,511", "Kherson,595", "Ukraine,5423", "Lado Gamsakhurdia,1", "Turquie,947", "Géorgie,46",
    "Tbilissi-Batoumi-Istanbul-Izmail-Odessa,1", "Nikolaïev,25", "Donetsk,580", "Dniepr,101", "Kiev,2391",
    "Paris,874", "Troie,4", "Élysée,75", "Brésil,381", "Inde,552", "Chine,1643", "Afrique du Sud,864",
    "État africain,13", "Johannesburg,63", "Président russe,32", '"marche""",1', "Mali,1174", "Bamako,267",
    "Russie-Afrique,263", "Saint-Pétersbourg,270", "États,643", "Égypte,617", "Caire,111", "Argentine,132",
    "Iran,351", "Arabie saoudite,235", "Bahreïn,23", "Émirats arabes unis,107", "New Zimbabwe,6",
    "Afghanistan,144", "Bangladesh,51", "Indonésie,111", "Mexique,47", "Nicaragua,39", "Nigeria,473",
    "Pakistan,93", "Sénégal,364", "Soudan,405", "Syrie,451", "Thaïlande,43", "Tunisie,419", "Uruguay,20",
    "Venezuela,58", "Zimbabwe,329", "l’Afrique du Sud,132", "Salves,1", "sanctionsLes,2", "Occident,1256",
    "États-Unis,3016", "Moyen-Orient,186", "Washington,722", "États du Moyen-Orient,3", "Belgorod,81",
    "D-30.Une,1", "Défense russe,334", "Chebekino,15", "Maroc,1082", "Marrakech,37", "Royaume,85",
    "Afrique de l'Ouest,82", "Comores,34", "État sénégalais,17", "Angola,236", "Burundi,92", "Mozambique,156",
    "Rwanda,208", "île Maurice,30", "Myanmar,13", "Durban,54", "M.Ouchakov,5", "État africains,28",
    "États africains-ndlr,1", "État des Comores,3", "Zambie,100", "Ouganda,282", "République du Congo,55",
    "Afrique du Nord,107", "Amérique,197", "Arabie Saoudite,26", "A,11", "Haut-Karabakh,44", "Bakou,21",
    "Erevan,27", "Azerbaïdjan,73", "Bruxelles,203", "l’Arménie,11", "Zaporojié,655", "Maison Blanche,47",
    "Londres,181", "Côte d’Ivoire,184", "Côte d'Ivoire,150", "Franc,2", "l’Afrique,642", "Centre,146",
    "Europe,1170", "l’Algérie,147", "M.Souakri,5", "partenariat russo-algérien,2", "Sahara,43", "Donbass,491",
    "Burkina Faso,542", "Centrafrique,221", "Éthiopie,302", "Malawi,127", "Kenya,382",
    "république populaire de Donetsk,77", "Donetsk-Sud,89", "Koupiansk,206", "Krasny Liman,155",
    "D-20,40", "Msta-B,36", "Grad,68", "Akatsiya,34", "Krab,36", "hub d’Alger,1", "pagailleLes,3",
    "Al-Arabiya,7", "mer Rouge,19", "Hurghada,5", "aéroport de Vnoukovo,2", "NOS,1", "Pays-Bas,161",
    "Allemagne).Selon,1", "Nord,501", "FMI).Le pays des pharaons,1", "El-Dabaa,18", "Alliance,55", "Suis,1",
    "Terre,148", "Soleil,42", "I,13", "Lune,54", "Allemagne,806", "Belgique,139", "Italie,273", "️🪆,1",
    "Minsk,142", "Royaume-Uni,390", "Artiomovsk,280", "Bakhmout,128", "Etat russe,7", "Via,3", "Caucase,22",
    "Al-Qaïda*.,3", "barrage de Kakhovka,8", "Kakhovka,38", "État russe,80", "Pékin,467", "Maison-Blanche,97",
    "Danemark,148", "Kaliningrad,10", "Copenhague,24", "US,68", "Vilnius,10", "Johannesburg?Alors,1",
    "Johannesbourg,3", "Crimée,325", "Pentagone,264", "Pacifique,62", "Japon,202", "Okhotsk,3", "Défense,175",
    "Ouagadougou,155", "Afrique de l’Ouest,57", "mer du Japon,29", "mer d'Okhotsk,6", "WSJ,10", "Pologne,334",
    "Irak,181", "Pantsir-S.Missiles,1", "batailleLa Russie,1", "Kinjal,31", "Congo,133",
    "Port autonome d’Abidjan,1", "PAA,1"
]

data = "\n".join(data_lines)
df = pd.read_csv(io.StringIO(data), header=None, names=['location', 'count'])
df['location'] = df['location'].astype(str).str.replace(r'^"|"$', '', regex=True).str.strip()

# --- 2. Fonction de Nettoyage et de Consolidation ---
def clean_location(loc):
    # Logique de nettoyage et d'unification des noms de lieux (identique à celle que nous avons affinée)
    loc = str(loc).replace("l’", "").replace("l'", "").replace("’", "'").replace("d'", "")
    loc = loc.replace("Afrique du Sud", "Afrique du Sud")
    loc = loc.replace("Côte d'Ivoire", "Cote d'Ivoire").replace("Côte d'Ivoire", "Cote d'Ivoire")
    loc = loc.replace("Johannesburg", "Johannesburg").replace("Johannesbourg", "Johannesburg")
    loc = loc.replace("État africain", "Afrique").replace("États africains", "Afrique").replace("État africains", "Afrique")
    loc = loc.replace("Etat russe", "Russie")
    loc = loc.replace("Donetsk-Sud", "Donetsk")
    loc = loc.replace("Tbilissi-Batoumi-Istanbul-Izmail-Odessa", "Tbilissi")
    loc = loc.replace("Etat des Comores", "Comores")
    loc = loc.replace("État sénégalais", "Sénégal")
    loc = loc.replace("Port autonome d'Abidjan", "Abidjan").replace("PAA", "Abidjan")
    loc = loc.replace("republique populaire de ", "")
    loc = loc.replace("Afrique de l'Ouest", "Afrique de l'Ouest")

    noise_patterns = [
        r"(?i)\bSPIEF\b", r"(?i)\bde TebbouneAu\b", r"(?i)\?Alors\b", r"(?i)-ndlr\b", r"(?i)\bEtat des Comores\b",
        r"(?i)\bRussie-Afrique\b", r"(?i)\bPrésident russe\b", r"(?i)\"marche\"\"\"", r"(?i)\bM\.Ouchakov\b",
        r"(?i)\bM\.Souakri\b", r"(?i)\bpartenariat russo-algérien\b", r"(?i)\bhub d'Alger\b", r"(?i)\bpagailleLes\b",
        r"(?i)\bAl-Arabiya\b", r"(?i)\baéroport de Vnoukovo\b", r"(?i)\bNOS\b", r"(?i)\bFMI\)\.Le pays des pharaons\b",
        r"(?i)\bAllemagne\)\.Selon\b", r"(?i)\bDéfense russe\b", r"(?i)\bDéfense\b", r"(?i)\bPentagone\b",
        r"(?i)\bAl-Qaïda\*\.\b", r"(?i)\bCaucase\b", r"(?i)\bKremlin\b", r"(?i)\bÉlysée\b", r"(?i)\bMaison Blanche\b",
        r"(?i)\bMaison-Blanche\b", r"(?i)\bRoyaume\b", r"(?i)\bÉtats\b", r"(?i)\bEtat\b", r"(?i)\bEco\b",
        r"(?i)\bAdossée\b", r"(?i)️🪆\b", r"(?i)\bVia\b", r"(?i)\bWSJ\b", r"(?i)\bFranc\b", r"(?i)\bSalves\b",
        r"(?i)\bsanctionsLes\b", r"(?i)\bfennecs\b", r"(?i)\bBRICS\.Visite\b", r"(?i)\bUS\b", r"(?i)\bTerre\b",
        r"(?i)\bSoleil\b", r"(?i)\bLune\b", r"(?i)\bAlliance\b", r"(?i)\bOccident\b", r"(?i)\bMoyen-Orient\b",
        r"(?i)\bAfrique du Nord\b", r"(?i)\bAmérique\b", r"(?i)\bCentre\b", r"(?i)\bEurope\b", r"(?i)\bD-30\.Une\b",
        r"(?i)\bD-20\b", r"(?i)\bMsta-B\b", r"(?i)\bGrad\b", r"(?i)\bAkatsiya\b", r"(?i)\bKrab\b",
        r"(?i)\bPantsir-S\.Missiles\b", r"(?i)\bKinjal\b", r"(?i)\bbarrage de Kakhovka\b", r"(?i)\bbatailleLa Russie\b",
        r"(?i)\bPays africains\b", r"(?i)\bAfrique du Sud\b", r"(?i)\bÉtat africain\b", r"(?i)\bÉtats du Moyen-Orient\b"
    ]

    for pattern in noise_patterns:
        loc = re.sub(pattern, "", loc).strip()

    loc = loc.split(',')[0].strip()
    loc = loc.split(')')[0].strip()
    loc = loc.split('?')[0].strip()
    loc = loc.split('-')[0].strip()

    if len(loc) < 2 or loc.lower() in ['a', 'i', 'ile', 'mer', 'nord', 'sud', 'est', 'ouest', 'soud', 'congo', 'kazakhstan', 'kirghizstan', 'bengladesh', 'afghanistan', 'indonesie', 'mexique', 'nicaragua', 'pakistan', 'thailande', 'uruguay', 'venezuela', 'zimbabwe', 'bahrein', 'afrique']:
        return None

    loc = loc.replace('"', '').strip()
    return loc

# --- 3. Exécution du Nettoyage et Agrégation ---
df['cleaned_location'] = df['location'].apply(clean_location)
df_cleaned = df.dropna(subset=['cleaned_location'])
df_agg = df_cleaned.groupby('cleaned_location')['count'].sum().reset_index()
df_agg.columns = ['Location', 'Count']
df_agg = df_agg.sort_values(by='Count', ascending=False).reset_index(drop=True)

# Export du fichier CSV nettoyé et agrégé
df_agg.to_csv('aggregated_locations.csv', index=False)


# --- 4. Génération des Actifs Visuels Statiques et Interactifs ---

# A. Top 20 Bar Chart (Matplotlib)
df_top20 = df_agg.head(20).copy()
plt.figure(figsize=(12, 8))
plt.barh(df_top20['Location'], df_top20['Count'], color='skyblue')
plt.xlabel("Nombre d'Occurrences (Count)")
plt.title("Top 20 Localisations par Nombre d'Occurrences")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('top20_bar_chart.png')
plt.close()

# B. Top 10 Pie Chart (Matplotlib)
df_top10 = df_agg.head(10).copy()
total_count = df_agg['Count'].sum()
top10_sum = df_top10['Count'].sum()
other_count = total_count - top10_sum
df_pie = pd.concat([
    df_top10,
    pd.DataFrame({'Location': ['Autres (Reste des ' + str(len(df_agg) - 10) + ' lieux)'], 'Count': [other_count]})
], ignore_index=True)

plt.figure(figsize=(10, 10))
plt.pie(df_pie['Count'], labels=df_pie['Location'], autopct='%1.1f%%', startangle=90,
        textprops={'fontsize': 10}, wedgeprops={'edgecolor': 'black'})
plt.title("Distribution des Occurrences (Top 10 vs. Reste)", y=1.05)
plt.tight_layout()
plt.savefig('top10_pie_chart.png')
plt.close()

# C. Carte Géographique Interactive (Altair/JSON)
coordinates = {
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
df_coords = pd.DataFrame([
    {'Location': loc, 'Latitude': lat, 'Longitude': lon}
    for loc, (lat, lon) in coordinates.items()
])

df_merged = pd.merge(df_agg, df_coords, on='Location', how='inner')
df_merged = df_merged[~df_merged['Location'].isin(['État', 'Nord', 'Sud', 'Est', 'Ouest', 'mer Rouge', 'mer du Japon', 'mer d\'Okhotsk', 'Sahara', 'Amérique', 'Europe', 'Occident', 'Moyen-Orient', 'Afrique', 'Afrique de l\'Ouest'])]

def create_map_chart(df):
    """Crée une carte à bulles Altair (JSON) pour l'affichage géographique."""
    chart = alt.Chart(df).mark_circle().encode(
        longitude='Longitude:Q',
        latitude='Latitude:Q',
        size=alt.Size('Count:Q', scale=alt.Scale(range=[50, 2000]), legend=alt.Legend(title="Count (Occurrence)")),
        color=alt.Color('Location:N', legend=None),
        tooltip=['Location', 'Count:Q', 'Latitude', 'Longitude'],
    ).properties(
        title='Occurrence des Mots-Clés Géographiques sur une Carte'
    ).interactive()
    return chart

chart = create_map_chart(df_merged)
chart.save('location_map_new.json')

print("Fichiers de sortie générés : 'aggregated_locations.csv', 'top20_bar_chart.png', 'top10_pie_chart.png', 'location_map_new.json'")