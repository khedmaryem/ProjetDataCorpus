import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Style CSS personnalisé pour un look épuré
custom_style = {
    'backgroundColor': '#F4F7F9',
    'padding': '20px',
    'fontFamily': '"Poppins", sans-serif'
}

card_style = {
    'backgroundColor': 'white',
    'borderRadius': '10px',
    'box-shadow': '0 4px 6px rgba(0,0,0,0.1)',
    'padding': '15px',
    'margin': '10px',
    'border': 'none'
}

THEME_IMAGE_MAP = {
    "Conflit Militaire (Ukraine)": "Conflit_Militaire_Ukraine.png",
    "Actualité Virale et ONU": "Actualite_Virale_et_ONU.png",
    "Affaires Militaires et Défense": "Affaires_Militaires_et_Defense.png",
    "Diplomatie Bloc Occidental": "Diplomatie_Bloc_Occidental.png",
    "Grandes Relations Diplomatiques": "Grandes_Relations_Diplomatiques.png",
    "Manifestations et Mouvements Sociaux": "Manifestations_et_Mouvements_Sociaux.png",
    "Politique Française Générale":"Politique_Francaise_Generale.png",
    "Souveraineté Africaine et IA":"Souverainete_Africaine_et_IA.png",
}

def apply_global_style(fig, title_text):
    """Applique une charte graphique uniforme à tous les graphiques du dashboard."""
    fig.update_layout(
        title={
            'text': f"<b>{title_text}</b>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'family': 'Poppins, Arial, sans-serif', 'color': '#2C3E50'}
        },
        template="plotly_white",
        font=dict(family="Poppins, Arial, sans-serif", size=12, color="#7F8C8D"),
        hovermode="x unified",
        margin=dict(l=50, r=50, t=80, b=50),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)', # Fond transparent pour s'intégrer aux cartes
        plot_bgcolor='rgba(0,0,0,0)',
        
        # Légende uniforme pour tous les graphes
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color="#2C3E50"),
            bgcolor="rgba(255, 255, 255, 0)"
        ),
        
        # Style des axes uniforme
        xaxis=dict(
            showgrid=False,
            linecolor='#BDC3C7',
            title_font={'size': 13, 'color': '#2C3E50'}
        ),
        yaxis=dict(
            gridcolor='#ECF0F1',
            linecolor='#BDC3C7',
            title_font={'size': 13, 'color': '#2C3E50'}
        )
    )
    return fig
# --- 1. CHARGEMENT ET PRÉPARATION GLOBALE DES DONNÉES ---
try:
    df_dashboard = pd.read_csv("dashboard_data_final.csv")
    df_top_words = pd.read_csv("df_top_words_clean.csv")
    df_dashboard['year'] = df_dashboard['year'].astype(str)
    # Préparation de la colonne temporelle YYYY-MM
    df_dashboard['month'] = df_dashboard['month'].apply(lambda x: f'{x:02d}')
    df_dashboard['YearMonth'] = df_dashboard['year'] + '-' + df_dashboard['month']
except FileNotFoundError:
    print("Erreur : Les fichiers de données sont introuvables. Assurez-vous d'avoir exécuté la partie Data Mining.")
    exit()

# --- CHARGEMENT DONNÉES UTILISATEUR (GÉO) ---
try:
    df_geo_map = pd.read_csv('aggregated_locations_geocoded.csv')
    if 'Count' in df_geo_map.columns:
        df_geo_map['normalized'] = df_geo_map['Count'] / df_geo_map['Count'].max()
except:
    df_geo_map = pd.DataFrame()

try:
    df_geo_year = pd.read_csv('locations_by_year.csv')
except:
    df_geo_year = pd.DataFrame()

# Préparation des options pour le menu déroulant
ALL_YEARS = [{'label': 'Global (Toutes Années)', 'value': 'ALL'}] + \
            [{'label': str(y), 'value': str(y)} for y in sorted(df_dashboard['year'].unique(), reverse=True)]

# --- 2. FONCTIONS DE GÉNÉRATION DES GRAPHIQUES STATIQUES (SANS 'self') ---

def generate_3d_scatter(df):
    """Génère une version améliorée du Nuage de Points 3D (ACP)."""
    fig = px.scatter_3d(
        df,x='CP1', y='CP2', z='CP3', 
        color='Theme', 
        hover_name='Theme',
        # On peut ajouter le titre de l'article ou les mots clés au survol :
        hover_data={'CP1':True, 'CP2':True, 'CP3':True, 'Theme':True},
        title='<b>Analyse Spatiale des Thématiques (ACP 3D)</b>',
        opacity=0.7,      # Ajoute de la transparence pour voir à travers les amas
        size_max=10       # Contrôle la taille maximale des points
    )

    # Personnalisation avancée du design
    fig.update_traces(
        marker=dict(
            size=5, 
            line=dict(width=1, color='DarkSlateGrey') # Ajoute un contour aux points
        )
    )

    fig.update_layout(
        template="plotly_white", # Fond blanc plus professionnel
        margin=dict(l=0, r=0, b=0, t=50), # Maximise l'espace pour le graphique
        scene=dict(
            xaxis=dict(title='Axe d\'importance 1', showbackground=False),
            yaxis=dict(title='Axe d\'importance 2', showbackground=False),
            zaxis=dict(title='Axe d\'importance 3', showbackground=False),
        ),
        legend=dict(
            title="Thématiques identifiées",
            orientation="v",
            yanchor="top",
            y=0.9,
            xanchor="left",
            x=1.1
        )
    )
    return fig

def generate_treemap(df):
    """Génère le Treemap de distribution globale."""
    df_count_theme = df['Theme'].value_counts().rename_axis('Theme').reset_index(name='Count')
    fig = px.treemap(
        df_count_theme, 
        path=['Theme'], 
        values='Count', 
        color='Count', 
        color_continuous_scale=px.colors.sequential.Blues, 
        title='<b>Distribution Globale du Corpus par Thème</b>'
    )
    return fig

def generate_article_per_year(df):
    """Génère le Bar Chart du nombre d'articles par Année (Global)."""
    fig = px.bar(
        df.groupby("year").size().reset_index(name='Count'), 
        x='year', 
        y='Count', 
        title="<b>Nombre d'articles par Année</b>"
    )
    fig.update_traces(width=0.2)
    fig.update_layout(xaxis_title="<b>Année</b>", yaxis_title="<b>Nombre d'articles</b>",title_font_size=18, # Augmenter la taille du titre
        font=dict(size=12))
    return fig

def generate_article_per_month(df, annee):
    """Génère le Bar Chart + Ligne de Tendance pour une année donnée."""
    df_annee = df[df['year'] == annee]
    article_per_month = df_annee.groupby("month").size().reset_index(name='Count')
    article_per_month['Trend'] = article_per_month['Count'].rolling(window=3, center=True).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=article_per_month['month'], y=article_per_month['Count'], marker_color='rgba(52, 152, 219, 0.3)',marker_line=dict(width=1, color='rgba(52, 152, 219, 0.6)'),
        width=0.5, showlegend=False))
    fig.add_trace(go.Scatter(x=article_per_month['month'], y=article_per_month['Trend'], mode='lines+markers', name='Tendance (Moyenne Mobile 3 Mois)', line=dict(color='#EF553B', width=3, shape='spline')))
    fig.update_layout(
        title=f"<b>Analyse du Volume Mensuel en {annee}</b>",
        template="plotly_white",
        hovermode="x unified",
        
        # Positionnement de la légende au-dessus (horizontal)
        legend=dict(
            orientation="h",      # "h" pour horizontal
            yanchor="bottom",
            y=1.02,               # Juste au-dessus du graphique
            xanchor="right",
            x=1,                  # Aligné à droite
            bgcolor="rgba(255, 255, 255, 0)" # Fond transparent
        ),
        
        # Réduction des marges pour gagner de la place
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(title="Mois de l'année"),
        yaxis=dict(title="Nombre d'articles", gridcolor='#F0F0F0')
    )
    return fig

def generate_heatmap_themes(df, annee):
    """Génère une Heatmap filtrée par année : Thèmes en ligne, Mois en colonne."""
    # On filtre les données pour l'année sélectionnée
    df_filtered = df[df['year'] == annee]
    
    # On groupe par mois et par thème
    df_heat = df_filtered.groupby(['month', 'Theme']).size().reset_index(name='Count')
    
    fig = px.density_heatmap(
        df_heat, 
        x="month", 
        y="Theme", 
        z="Count", 
        color_continuous_scale='Viridis',
        title=f"<b>Intensité Médiatique par Thème en {annee}</b>",
        labels={'month': 'Mois', 'Count': 'Nombre d\'articles'},
        # On force l'affichage des 12 mois pour la clarté
        category_orders={"month": [f"{m:02d}" for m in range(1, 13)]} 
    )
    
    fig.update_layout(
        height=450,
        margin=dict(t=50, b=50, l=50, r=50),
        xaxis_title="Mois",
        yaxis_title="Thématiques"
    )
    return fig

def generate_comparison_chart(df):
    """Génère le Bar Chart Groupé de comparaison Thèmes 2024 vs 2025."""
    df_comparison = df.groupby(['Theme', 'year']).size().reset_index(name='Count')
    df_pivot = df_comparison.pivot(index='Theme', columns='year', values='Count').fillna(0).reset_index()
    df_comparison_full = pd.melt(df_pivot, id_vars=['Theme'], value_vars=df_pivot.columns.drop('Theme'), var_name='year', value_name='Count')
    
    fig = px.bar(df_comparison_full, x='Theme', y='Count', color='year', barmode='group', title="<b>Volume d'Articles par Thème</b>")
    fig.update_layout(xaxis_title="<b>Thème</b>", yaxis_title="<b>Nombre d'articles</b>", xaxis={'categoryorder':'total descending', 'tickangle': -45},title_font_size=18, font=dict(size=12)) # Police des axes/légendes)
    return fig

def generate_trend_chart(df):
    """Génère le Area Chart de Tendance des Thèmes."""
    df_themes_trend = df.groupby(['YearMonth', 'Theme']).size().reset_index(name='Count')
    df_themes_trend_clean = df_themes_trend[df_themes_trend['Theme'] != 'Bruit Média/Podcast']
    
    fig = px.area(
        df_themes_trend_clean, 
        x='YearMonth', 
        y='Count', 
        color='Theme', 
        title="<b>Évolution Mensuelle du Volume d'Articles par Thème</b>", 
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig.update_layout(xaxis_tickangle=-45, xaxis = dict(dtick="M1", tickformat="%Y-%m"))
    return fig

# Dans la Section 2. FONCTIONS DE GÉNÉRATION DES GRAPHIQUES STATIQUES (SANS 'self')

def generate_theme_volume_bar(df, annee):
    """Génère le Bar Chart des volumes thématiques pour une année donnée."""
    if annee == 'ALL': # Gère le cas où vous voudriez utiliser 'ALL' ailleurs
        df_filtered = df.copy()
        title_text = "Volume d'Articles par Thème (Global)"
    else:
        df_filtered = df[df['year'] == annee]
        title_text = f"<b>Volume d'Articles par Thème en {annee}</b>"

    df_count = df_filtered.groupby('Theme').size().reset_index(name='Count')
    # Optionnel: Exclure le "Bruit Média" pour la clarté
    df_count = df_count[df_count['Theme'] != 'Bruit Média/Podcast'] 
    
    fig = px.bar(
        df_count.sort_values(by='Count', ascending=False),
        x='Theme',
        y='Count',
        color='Theme',
        title=title_text,
        height=600
    )
    fig.update_layout(xaxis={'categoryorder': 'total descending', 'tickangle': -45}, margin=dict(t=50, b=100))
    return fig

def generate_top_words_bar(df_words):
    """
    Génère un bar chart horizontal (facetté) montrant
    les 3 mots-clés les plus significatifs par thème
    selon leur poids TF-IDF.
    """

    # S'assurer que les mots sont triés par importance dans chaque thème
    df_words_sorted = df_words.sort_values(
        by=['Theme', 'Importance_Poids_TFIDF'],
        ascending=[True, False]
    )

    fig = px.bar(
        df_words_sorted,
        x='Importance_Poids_TFIDF',
        y='Mot_Cle',
        color='Theme',
        facet_col='Theme',
        facet_col_wrap=2,   # 2 colonnes de facettes
        orientation='h',
        facet_col_spacing=0.1, 
        title="<b>Top 3 des mots-clés les plus significatifs par thème (TF-IDF)</b>",
        labels={
            'Importance_Poids_TFIDF': 'Poids TF-IDF',
            'Mot_Cle': 'Mot-clé'
        }
    )

    # Permet d'avoir des axes Y indépendants (mots différents par thème)
    fig.update_yaxes(matches=None, showticklabels=True)

    # Amélioration de la lisibilité globale
    fig.update_layout(
        showlegend=False,
        height=900,
        margin=dict(t=80, l=80, r=40, b=40)
    )

    return fig





# --- FONCTIONS VISUALISATION UTILISATEUR (GÉO) ---
def generate_geo_map(df):
    if df.empty:
        return px.scatter_geo(title="Pas de données géographiques")
    fig = px.scatter_geo(
        df, lat='Latitude', lon='Longitude', hover_name='Location',
        size='Count', color='Count', projection='natural earth',
        color_continuous_scale='Plasma', size_max=40,
        template="plotly_dark",
        title="<b>Distribution Géographique des Mentions</b>"
    )
    fig.update_geos(
        showcoastlines=True, coastlinecolor="RebeccaPurple",
        showland=True, landcolor="#e5e5e5",
        showocean=True, oceancolor="#c9d2e0",
        showlakes=True, lakecolor="Blue",
        showcountries=True, countrycolor="white"
    )
    fig.update_layout(height=600, margin={"r":0,"t":50,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
    return fig

def generate_geo_top15(df):
    if df.empty: return go.Figure()
    top_15 = df.nlargest(15, 'Count')
    fig = px.bar(
        top_15, x='Count', y='Location', orientation='h',
        color='Count', color_continuous_scale='Oranges',
        labels={'Count': 'Volume de mentions', 'Location': 'Lieu'},
        title="<b>Top 15 des Lieux Cités</b>"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#2C3E50', height=500)
    return fig

def generate_geo_trends(df_year, df_map):
    if df_year.empty or df_map.empty: return go.Figure()
    # Top 5 locations ever
    top_5_ever = df_map.nlargest(5, 'Count')['Location'].tolist()
    df_top_evolution = df_year[df_year['Location'].isin(top_5_ever)]
    
    fig = px.line(
        df_top_evolution, x='Year', y='Count', color='Location',
        markers=True, line_shape='spline',
        title="<b>Évolution Temporelle des Top Lieux</b>"
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#2C3E50', height=500)
    return fig

# --- 3. DÉFINITION DE L'APPLICATION ET DU LAYOUT (AVEC ONGLET) ---

app = dash.Dash(
    __name__,
    external_stylesheets=['https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap']
)


# --- Contenu de l'Onglet 2 : Analyse Annuelle Détaillée ---
# Déterminons l'année par défaut pour l'initialisation (l'année la plus récente)
DEFAULT_YEAR = sorted(df_dashboard['year'].unique(), reverse=True)[0] # Ex: '2025'

# --- 3. DÉFINITION DE L'APPLICATION ET DU LAYOUT (AVEC ONGLET) ---

# Ajout du CSS externe pour retirer les marges du body et permettre le plein écran sans scroll
#app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# --- Contenu de l'Onglet 2 : Comparaison Globale ---
tab_comparison_content = html.Div(style={'padding': '0 15px'}, children=[ 

    html.Div([
        dcc.Graph(figure=generate_article_per_year(df_dashboard), style={'width': '30%', 'height': '600px'}),
        dcc.Graph(figure=generate_comparison_chart(df_dashboard), style={'width': '60%', 'height': '600px'}),
        
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px', 'flexWrap': 'wrap','marginTop': '10px'}),
    ])

# --- Contenu de l'Onglet 1 : Analyse Annuelle Détaillée ---
tab_detail_content = html.Div(style={'padding': '0 15px'}, children=[
    
    # SÉLECTION D'ANNÉE UNIQUE
    html.Div([
        html.P("Sélectionnez l'Année à Analyser:", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='year-dropdown-detail',
            options=[{'label': str(y), 'value': str(y)} for y in sorted(df_dashboard['year'].unique(), reverse=True)],
            value=DEFAULT_YEAR, 
            clearable=False,
            style={'width': '200px', 'marginBottom': '20px'}
        ),
    ], style={'display': 'flex', 'alignItems': 'center', 'gap': '20px', 'marginLeft': '20px','marginTop': '10px'}),

    # Conteneur des graphiques dynamiques
    html.Div([
        # 1. Articles par Mois (Dynamique) 
        dcc.Graph(
            id='articles-per-month-dynamic', 
            figure=generate_article_per_month(df_dashboard, DEFAULT_YEAR), 
            style={'width': '30%', 'height': '600px'}
        ),
        # 2. Volume Thématique (Dynamique) 
        dcc.Graph(
            id='theme-volume-bar-dynamic', 
            figure=generate_theme_volume_bar(df_dashboard, DEFAULT_YEAR), 
            style={'width': '60%', 'height': '600px'}
        ),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px', 'flexWrap': 'wrap'}),
    
    html.Div([
        dcc.Graph(
            id='heatmap-themes-dynamic', 
            figure=generate_heatmap_themes(df_dashboard, DEFAULT_YEAR)
        )
    ]), 

    html.Div([
        dcc.Graph(
            id='trend-chart',
            figure=generate_trend_chart(df_dashboard)
        )
    ]),


])
    

# --- Contenu de l'Onglet 3 : Aperçu Global (Structure) ---
# Ajout de 'padding' au conteneur principal de l'onglet
# --- Contenu de l'Onglet 3 : Aperçu Global (Structure Sémantique et Spatiale) ---
tab_global_structure_content = html.Div(style={'padding': '0 15px'}, children=[

    # 4. SECTION GÉOPOLITIQUE (UTILISATEUR) - Moved to Top
    html.H2("🌍 Carte Interactive des Pays & Lieux", style={'textAlign': 'center', 'color': '#2C3E50', 'marginTop': '30px'}),
    
    html.Div([
        # Carte
        html.Div([
            dcc.Graph(figure=generate_geo_map(df_geo_map), style={'width': '100%', 'height': '600px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'borderRadius': '10px', 'padding': '10px', 'backgroundColor': 'white'}),
        ], style={'width': '100%', 'marginBottom': '20px'}),
        
        # Stats charts side-by-side
        html.Div([
            html.Div([dcc.Graph(figure=generate_geo_top15(df_geo_map))], style={'width': '48%', 'display': 'inline-block', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'borderRadius': '10px', 'padding': '10px', 'backgroundColor': 'white'}),
            html.Div([dcc.Graph(figure=generate_geo_trends(df_geo_year, df_geo_map))], style={'width': '48%', 'display': 'inline-block', 'float': 'right', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'borderRadius': '10px', 'padding': '10px', 'backgroundColor': 'white'}),
        ], style={'width': '100%', 'marginBottom': '30px'}),
        
    ]),
    html.Hr(),

    # 1. Le graphique des mots-clés (Top Words) prend toute la largeur en haut
    html.Div([
        dcc.Graph(figure=generate_top_words_bar(df_top_words), style={'width': '100%', 'height': '700px'}),
    ], style={'marginBottom': '30px','marginTop': '10px'}),

    # 2. Le Nuage 3D et la Heatmap côte à côte
    html.Div([
        dcc.Graph(figure=generate_3d_scatter(df_dashboard), style={'width': '100%', 'height': '600px'}),
        
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px', 'flexWrap': 'wrap'}),

    # 3. Treemap global
    html.Div([
        dcc.Graph(id='treemap-global',figure=generate_treemap(df_dashboard), style={'width': '100%', 'height': '600px'}),
        html.Div(id='theme-name-display', style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '10px'}),

    html.Div(
    id='theme-image-container',
    style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'marginTop': '30px',
        'width': '100%'
    },
    children=[
        html.Img(
            id='theme-image',
            src='',
            style={
                'maxWidth': '600px',
                'width': '100%',
                'height': 'auto',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                'borderRadius': '10px'
            }
        )
    ]
)
        
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px', 'flexWrap': 'wrap'}),

    
])

# LE LAYOUT FINAL AVEC LES ONGLETS (Plein écran : width: '100vw', margin: '0')
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'width': '100vw', 'margin': '0'}, children=[
    
    html.H1("Dashboard pour l'analyse de Corpus ", style={'textAlign': 'center', 'color': '#2C3E50', 'marginTop': '20px'}),
    html.Hr(), 

    dcc.Tabs(id="tabs-graph", value='tab-comparison', children=[ 
        

        # 1. Analyse Détaillée (Focus annuel)
        dcc.Tab(label='Analyse Annuelle Détaillée', value='tab-detail', children=[tab_detail_content]),

        # 2. Comparaison (Focus principal)
        dcc.Tab(label='Comparaison 2024 vs 2025', value='tab-comparison', children=[tab_comparison_content]),

        # 3. Aperçu Global (Structure)
        dcc.Tab(label='Aperçu Global du corpus(Structure)', value='tab-global-structure', children=[tab_global_structure_content]),

        
        
    
    ]),
])

# --- 4. CALLBACKS (Logique Interactive) ---
# NOTE: prevent_initial_call=True est ajouté car les figures sont initialisées dans le layout
# NOTE: allow_duplicate=True est obligatoire car les figures sont initialisées dans le layout


# Callback 1 : Mise à jour du Volume par Thème (Bar Chart)
@app.callback(
    Output('theme-volume-bar-dynamic', 'figure', allow_duplicate=True),
    [Input('year-dropdown-detail', 'value')],
    prevent_initial_call=True 
)
def update_theme_volume_bar(selected_year):
    # Appelle la fonction générée précédemment (generate_theme_volume_bar)
    return generate_theme_volume_bar(df_dashboard, selected_year)

# Callback 2 : Mise à jour des Articles par Mois (Bar Chart + Tendance)
@app.callback(
    Output('articles-per-month-dynamic', 'figure', allow_duplicate=True),
    [Input('year-dropdown-detail', 'value')],
    prevent_initial_call=True 
)
def update_article_per_month(selected_year):
    # Utilise la fonction existante (generate_article_per_month)
    return generate_article_per_month(df_dashboard, selected_year)

@app.callback(
    Output('heatmap-themes-dynamic', 'figure'),
    Input('year-dropdown-detail', 'value')
)
def update_heatmap(selected_year):
    # Appelle la fonction qui génère la heatmap pour l'année sélectionnée
    return generate_heatmap_themes(df_dashboard, selected_year)

# Callback 3 : Mise à jour de la Heatmap (Intensité médiatique)
@app.callback(
    [Output('theme-image', 'src'),
     Output('theme-name-display', 'children')],
    [Input('treemap-global', 'clickData')]
)
def display_theme_image(clickData):
    if clickData is None:
        return '', ''

    theme_clicked = clickData['points'][0]['label']

    # 🔍 Récupération du fichier image via le mapping
    image_filename = THEME_IMAGE_MAP.get(theme_clicked)

    if image_filename is None:
        return '', f"Aucune image disponible pour le thème : {theme_clicked}"

    image_path = f"/assets/wordclouds/{image_filename}"

    return image_path, f"Vous avez sélectionné : {theme_clicked}"

# --- 5. LANCEMENT DU SERVEUR ---
if __name__ == '__main__':
    # Utilisez app.run(debug=True)
    app.run(debug=True)