import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px



st.set_page_config(layout="wide", page_title="Géographie de l'Information - Sputnik Analysis", page_icon="🌍")



# --- Custom CSS for Premium Feel ---

st.markdown("""

<style>

    .reportview-container {

        background: #0e1117;

    }

    h1 {

        font-family: 'Helvetica Neue', sans-serif;

        font-weight: 700;

        color: #f0f2f6;

    }

    h2, h3 {

        font-family: 'Helvetica Neue', sans-serif;

        color: #d0d2d6;

    }

    .stMetric {

        background-color: #1f2937;

        padding: 15px;

        border-radius: 10px;

        border: 1px solid #374151;

    }

</style>

""", unsafe_allow_html=True)



st.title("🌍 Observatoire Géopolitique")

st.markdown("**Visualisation Avancée des Flux d'Information (Sputnik News)**")


# --- Loading Data ---
@st.cache_data
def load_data():
    try:
        df_map = pd.read_csv('aggregated_locations_geocoded.csv')
        if 'Count' in df_map.columns:
            df_map['normalized'] = df_map['Count'] / df_map['Count'].max()
    except:
        df_map = pd.DataFrame()

    try:
        df_year = pd.read_csv('locations_by_year.csv')
    except:
        df_year = pd.DataFrame()
        
    return df_map, df_year

df_map, df_year = load_data()

if df_map.empty:
    st.error("Les données géographiques ne sont pas encore prêtes. Veuillez vérifier vos fichiers CSV.")
    st.stop()

# --- Sidebar Controls ---
st.sidebar.title("⚙️ Paramètres")
years = sorted(df_year['Year'].unique()) if not df_year.empty else []
view_mode = st.sidebar.radio("Mode de Vue", ["Vue Globale (Cumulée)", "Évolution Temporelle"])

selected_year = None
if view_mode == "Évolution Temporelle" and years:
    selected_year = st.sidebar.select_slider("Sélectionner l'Année", options=years)

map_type = st.sidebar.selectbox(
    "Type de Visualisation", 
    ["Colonnes 3D (Volume)", "Heatmap & Densité (Analyse)", "Cellules Hexagonales (Précision)", "Scatter (Points)"]
)

# Filter Data
if view_mode == "Évolution Temporelle" and selected_year:
    current_df = df_year[df_year['Year'] == selected_year].copy()
else:
    current_df = df_map.copy()

# --- Main Dashboard ---

# 1. KPI Row
total_locs = len(current_df)
top_loc = current_df.iloc[0]['Location'] if not current_df.empty else "N/A"
top_count = current_df.iloc[0]['Count'] if not current_df.empty else 0

c1, c2, c3 = st.columns(3)
c1.metric("Lieux Mentionnés", total_locs)
c2.metric("Lieu le plus cité", top_loc)
c3.metric("Volume max (Mentions)", top_count)

st.divider()

# 2. GRAPHIQUES DE SYNTHÈSE (Nouveau - Correspondant à vos images)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Top 15 des Lieux")
    top_15 = current_df.nlargest(15, 'Count')
    fig_bar = px.bar(
        top_15, x='Count', y='Location', orientation='h',
        color='Count', color_continuous_scale='Oranges',
        labels={'Count': 'Volume de mentions', 'Location': 'Lieu'}
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("📈 Évolution des Top Lieux")
    if not df_year.empty:
        # On prend les 5 lieux les plus importants historiquement
        top_5_ever = df_map.nlargest(5, 'Count')['Location'].tolist()
        df_top_evolution = df_year[df_year['Location'].isin(top_5_ever)]
        
        fig_line = px.line(
            df_top_evolution, x='Year', y='Count', color='Location',
            markers=True, line_shape='spline'
        )
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Données d'évolution non disponibles.")

st.divider()

# 3. CARTE INTERACTIVE
st.subheader("🌍 Carte Interactive des Pays & Lieux")
view_state = pdk.ViewState(latitude=46.0, longitude=2.0, zoom=1, pitch=45 if "3D" in map_type else 0)

if map_type == "Scatter (Points)":
    fig_map = px.scatter_geo(
        current_df, lat='Latitude', lon='Longitude', hover_name='Location',
        size='Count', color='Count', projection='natural earth',
        color_continuous_scale='Plasma', size_max=40,
        template="plotly_dark"

    )
    fig_map.update_geos(
        showcoastlines=True, coastlinecolor="RebeccaPurple",
        showland=True, landcolor="#e5e5e5", # Terre en gris clair
        showocean=True, oceancolor="#c9d2e0", # Océan en bleu-gris
        showlakes=True, lakecolor="Blue",
        showcountries=True, countrycolor="white" # Frontières visibles
    )
    
    fig_map.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
    selection = st.plotly_chart(fig_map, on_select="rerun", selection_mode="points", use_container_width=True)
else:
    # Logic Pydeck (3D / Heatmap / Hexagon)
    layers = []
    if map_type == "Colonnes 3D (Volume)":
        layers.append(pdk.Layer("ColumnLayer", data=current_df, get_position='[Longitude, Latitude]', get_elevation='Count', elevation_scale=100, radius=20000, get_fill_color='[255, 140, 0, 140]', pickable=True))
    elif map_type == "Heatmap & Densité (Analyse)":
        layers.append(pdk.Layer("HeatmapLayer", data=current_df, get_position='[Longitude, Latitude]', get_weight='Count', radiusPixels=60))
    elif map_type == "Cellules Hexagonales (Précision)":
        layers.append(pdk.Layer("HexagonLayer", data=current_df, get_position='[Longitude, Latitude]', get_elevation_weight='Count', elevation_scale=50, elevation_range=[0, 3000], extruded=True, radius=20000, pickable=True, upper_percentile=98, material=True))
    
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state, map_style=pdk.map_styles.DARK, tooltip={"html": "<b>{Location}</b>: {Count} mentions"}))
    selection = None

# 4. ANALYSE DÉTAILLÉE AU CLIC
if selection and selection.get('selection', {}).get('point_indices'):
    idx = selection['selection']['point_indices'][0]
    target_location = current_df.iloc[idx]['Location']
    
    st.divider()
    st.markdown(f"## 🔎 Focus : **{target_location}**")
    # (Le reste de votre code d'analyse détaillée peut rester ici)
    
    # 1. Stats Cards
    # Ensure we can find the location in current_df
    loc_data_rows = current_df[current_df['Location'] == target_location]
    if not loc_data_rows.empty:
        loc_data = loc_data_rows.iloc[0]
        c1, c2 = st.columns(2)
        c1.metric("Occurrences Totales", loc_data['Count'])
        
        # Calculate Rank
        current_df_sorted = current_df.sort_values(by="Count", ascending=False).reset_index(drop=True)
        rank = current_df_sorted[current_df_sorted['Location'] == target_location].index[0] + 1
        c2.metric("Classement Global", f"#{rank}")
    
    # 2. Dynamic Evolution (Line Chart) or Heatmap context
    st.subheader("📈 Dynamique Temporelle")
    
    if not df_year.empty:
        trend_data = df_year[df_year['Location'] == target_location].sort_values(by='Year')
        
        if not trend_data.empty:
            fig_trend = px.area(
                trend_data, 
                x='Year', 
                y='Count', 
                markers=True,
                line_shape='spline',
                title=f"Évolution des mentions de {target_location}",
                color_discrete_sequence=['#FF8C00']
            )
            fig_trend.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                font_color='white',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#333')
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("Pas de données temporelles détaillées disponibles pour ce lieu.")
    else:
        st.warning("Données annuelles non disponibles.")

st.divider()
st.caption("Données extraites de Sputnik News. Visualisation générée par Deepmind Agent.")