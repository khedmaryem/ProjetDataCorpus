import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk

# --- Configuration de la Page Streamlit ---
st.set_page_config(layout="wide", page_title="Géographie des Données")

st.title("🌍 Carte et Contexte Géographique")
st.markdown("### Analyse approfondie : Carte 3D et Contextualisation")

# --- 1. Chargement des Données ---
@st.cache_data
def load_data():
    try:
        df_stats = pd.read_csv('localisations.csv')
        if 'location' in df_stats.columns:
            df_stats = df_stats.rename(columns={'location': 'Location', 'count': 'Count'})
    except FileNotFoundError:
        try:
             df_stats = pd.read_csv('aggregated_locations.csv')
        except FileNotFoundError:
             return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df_stats = df_stats.sort_values(by='Count', ascending=False).reset_index(drop=True)
    df_stats['Rank'] = df_stats.index + 1
    total_count = df_stats['Count'].sum()
    df_stats['Share'] = df_stats['Count'] / total_count

    try:
        df_map = pd.read_csv('aggregated_locations_geocoded.csv')
        # Merge stats to map to get Rank/Share securely
        df_map = pd.merge(df_map, df_stats[['Location', 'Rank', 'Share']], on='Location', how='left')
    except FileNotFoundError:
        df_map = pd.DataFrame()
        
    try:
        df_context = pd.read_csv('location_context.csv')
    except FileNotFoundError:
        df_context = pd.DataFrame()
    
    return df_stats, df_map, df_context

df_agg, df_map, df_context = load_data()

if df_agg.empty:
    st.error("Aucune donnée.")
    st.stop()

# --- SIDEBAR & INSPECTOR ---
st.sidebar.header("🔍 Inspecteur de Lieu")
# Dropdown linked to map data
selected_location = st.sidebar.selectbox("Choisir un lieu pour voir les détails :", ["(Aucun)"] + sorted(df_map['Location'].unique().tolist()) if not df_map.empty else [])

# Main Metrics
total_mentions = df_agg['Count'].sum()
col1, col2, col3 = st.columns(3)
col1.metric("Total Lieux", len(df_agg))
col2.metric("Mentions Totales", f"{total_mentions:,}")
col3.metric("Lieux Géolocalisés", len(df_map))

st.divider()

# --- 2. CARTE 3D (PYDECK ColumnLayer) ---
# Better for "Importance" visualization

if not df_map.empty:
    # Prepare data for PyDeck
    # Normalize height
    df_map['normalized_count'] = df_map['Count'] / df_map['Count'].max()
    
    # Layer: 3D Columns
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df_map,
        get_position='[Longitude, Latitude]',
        get_elevation='Count',
        elevation_scale=100, # Scale factor
        radius=20000, # 20km radius columns
        get_fill_color='[255, 140, 0, 200]', # Orange
        pickable=True,
        auto_highlight=True,
    )
    
    text_layer = pdk.Layer(
        "TextLayer",
        data=df_map.head(20), # Only labels for top 20 to avoid clutter
        get_position='[Longitude, Latitude]',
        get_text='Location',
        get_color=[0, 0, 0, 200],
        get_size=16,
        get_alignment_baseline="'bottom'",
        pixel_offset=[0, -20] # Shift up 
    )

    tooltip = {
        "html": """
        <div style="background-color: white; padding: 10px; color: black; border-radius: 5px;">
            <b>{Location}</b><br/>
            Rank: <b>#{Rank}</b><br/>
            Mentions: <b>{Count}</b> ({Share:.2%})
        </div>
        """
    }

    view_state = pdk.ViewState(
        latitude=20,
        longitude=0,
        zoom=2,
        pitch=45, # 3D view
        bearing=0
    )

    r = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style='mapbox://styles/mapbox/light-v9'
    )
    
    st.pydeck_chart(r)

# --- 3. CONTEXTE & DÉTAILS ---

if selected_location != "(Aucun)":
    st.markdown(f"### 📍 Détails pour : **{selected_location}**")
    
    # Get stats
    loc_stats = df_agg[df_agg['Location'] == selected_location].iloc[0]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Classement", f"#{loc_stats['Rank']}")
    c2.metric("Nombre de Mentions", loc_stats['Count'])
    c3.metric("Part du Corpus", f"{loc_stats['Share']:.2%}")
    
    # Show Context if available
    if not df_context.empty:
        ctx_row = df_context[df_context['Location'] == selected_location]
        if not ctx_row.empty:
            st.markdown("#### 📰 Exemples de Titres / Contexte :")
            snippets = ctx_row.iloc[0]['Context'].split(" | ")
            for snippet in snippets:
                st.info(f"📄 {snippet}")
        else:
            st.warning("Pas de contexte extrait pour ce lieu.")
    
elif not df_context.empty:
    # Show random context snippets for discovery
    st.markdown("### 📰 Aperçu des Actualités Géolocalisées (Top 5)")
    st.dataframe(df_context.head(5), hide_index=True)
