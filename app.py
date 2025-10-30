import streamlit as st
import pandas as pd
from pathlib import Path
import unicodedata

# --- Safe startup configuration for Streamlit Cloud ---
import os, time

# ✅ Ensure Streamlit starts in the correct directory (important for cloud)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# ✅ Give a short delay to avoid race conditions during deployment
time.sleep(2)

# ✅ Create a helper function to safely load CSVs from the /data folder
DATA_PATH = os.path.join(BASE_DIR, "data")

def load_csv(filename):
    """Utility to load CSVs safely regardless of working directory"""
    filepath = os.path.join(DATA_PATH, filename)
    return pd.read_csv(filepath)
# -------------------------------------------------------

st.set_page_config(page_title="Rennes Relocation (Mock)", page_icon="🦞", layout="centered")

# ---------- global theme-aware styles ----------
st.markdown(
    """
    <style>
    :root {
        --card-bg: var(--secondary-background-color);
        --text-color: var(--text-color);
        --accent-bg: var(--background-color);
    }

    /* Apply default text color globally for markdowns */
    .stMarkdown, .stText, .st-expander {
        color: var(--text-color) !important;
    }

    /* Theme-aware box border for main content boxes */
    .theme-box {
        box-sizing: border-box;
        border: 1px solid #000; /* default black for light mode */
    }
    @media (prefers-color-scheme: dark) {
        .theme-box {
            border: 1px solid #fff;
        }
    }

    /* Modern GoLocal section banners */
    .section-banner {
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        color: white;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 1.8em;
        letter-spacing: -0.5px;
        position: relative;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        overflow: hidden;
        margin-bottom: 22px;
        text-shadow: 0 2px 6px rgba(0,0,0,0.09);
    }
    .section-banner::before {
        content: "";
        position: absolute;
        top: -40px;
        left: -40px;
        width: 120px;
        height: 120px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
        z-index: 0;
    }
    .section-banner::after {
        content: "";
        position: absolute;
        bottom: -50px;
        right: -50px;
        width: 140px;
        height: 140px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
        z-index: 0;
    }
    .banner-blue { background: linear-gradient(135deg, #0059b3, #00b4d8); }
    .banner-green { background: linear-gradient(135deg, #2e8b57, #4caf50); }
    .banner-pink { background: linear-gradient(135deg, #cc3399, #ff66cc); }
    .banner-gray { background: linear-gradient(135deg, #3a3a3a, #6b6b6b); }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    cities = load_csv("cities.csv")
    nationalities = load_csv("nationalities.csv")
    categories = load_csv("categories.csv")
    posts = load_csv("posts.csv")
    places = load_csv("places.csv")
    checklists = load_csv("checklists.csv")
    checklist_items = load_csv("checklist_items.csv")
    return cities, nationalities, categories, posts, places, checklists, checklist_items

cities, nationalities, categories, posts, places, checklists, checklist_items = load_data()

import math
import numpy as np

def safe_str(x):
    if x is None:
        return ""
    try:
        # treat NaN/NaT as empty
        if isinstance(x, float) or isinstance(x, np.floating):
            if math.isnan(x):
                return ""
        return str(x)
    except Exception:
        return ""

# Sanitize key string columns to avoid NaN concatenation errors
for col in ["name","type","neighborhood","price_level","short_blurb","website","map_url"]:
    if col in places.columns:
        places[col] = places[col].apply(safe_str)

for col in ["title","summary","body_md","category_id","name"]:
    if col in posts.columns:
        posts[col] = posts[col].apply(safe_str)

for col in ["name","category_id","parent_category_id"]:
    if col in categories.columns:
        categories[col] = categories[col].apply(safe_str)

# ---------- helpers ----------
def normalize_type(t):
    t = t.lower().strip()
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    return t

places["type_normalized"] = places["type"].apply(normalize_type)

# ---------- helpers ----------
def set_current_view(new_view: str):
    st.session_state["current_view"] = new_view

def reset_home():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state["current_view"] = "landing"

# ---------- banner ----------
st.markdown(
    """
    <style>
    .golocal-banner {
        background: linear-gradient(135deg, #001F3F, #007ACC);
        padding: 45px 25px;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        margin-bottom: 35px;
        position: relative;
        overflow: hidden;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    .golocal-banner::before {
        content: "";
        position: absolute;
        top: -60px;
        left: -60px;
        width: 180px;
        height: 180px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 50%;
        z-index: 0;
    }

    .golocal-banner::after {
        content: "";
        position: absolute;
        bottom: -80px;
        right: -80px;
        width: 220px;
        height: 220px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 50%;
        z-index: 0;
    }

    .golocal-banner h1 {
        font-size: 2.5em;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
        z-index: 1;
        position: relative;
    }

    .golocal-banner h1 span {
        color: #00B4D8;
    }

    .golocal-banner p {
        font-size: 1.2em;
        margin: 0;
        color: #E0F7FF;
        font-weight: 400;
        z-index: 1;
        position: relative;
    }

    .golocal-banner p strong {
        color: #ffffff;
        font-weight: 600;
    }
    </style>

    <div class="golocal-banner">
        <h1>🗺️ Go<span>Local</span></h1>
        <p>The <strong>new</strong> way to make any city feel like <strong>home</strong>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- language selection ----------
if "lang" not in st.session_state:
    st.session_state["lang"] = "English"

lang = st.selectbox("🌐 Choose your language:", ["English", "Français", "Español"], index=0)
st.session_state["lang"] = lang

# ---------- translations ----------
TEXT = {
    "home": {"English": "🏠 Home", "Français": "🏠 Accueil", "Español": "🏠 Inicio"},
    "switch_planning": {
        "English": "🔄 Switch to Planning",
        "Français": "🔄 Passer à la préparation",
        "Español": "🔄 Cambiar a planificación",
    },
    "switch_arrived": {
        "English": "🔄 Switch to Already in Rennes",
        "Français": "🔄 Passer à déjà à Rennes",
        "Español": "🔄 Cambiar a ya en Rennes",
    },
    "continue": {
        "English": "Continue",
        "Français": "Continuer",
        "Español": "Continuar",
    },
    "welcome": {
        "English": "Welcome! Let's get started 🛫",
        "Français": "Bienvenue ! Commençons 🛫",
        "Español": "¡Bienvenido! Empecemos 🛫",
    },
    "planning_banner": {
        "English": "📝 Pre‑Departure Essentials",
        "Français": "📝 Préparatifs avant le départ",
        "Español": "📝 Preparativos antes del viaje",
    },
    "infohub_banner": {
        "English": "🧭 Pre‑Departure Info Hub",
        "Français": "🧭 Centre d’informations avant le départ",
        "Español": "🧭 Centro de información previa al viaje",
    },
    "explore_banner": {
        "English": "🌆 Explore Rennes",
        "Français": "🌆 Explorez Rennes",
        "Español": "🌆 Explora Rennes",
    },
    "admin_banner": {
        "English": "🏛️ Administrative Guides",
        "Français": "🏛️ Guides administratifs",
        "Español": "🏛️ Guías administrativas",
    },
    "community_banner": {
        "English": "👥 Community",
        "Français": "👥 Communauté",
        "Español": "👥 Comunidad",
    },
    "looking_filter_title": {
        "English": "🔍 Looking for an activity or place to visit?",
        "Français": "🔍 Vous cherchez une activité ou un lieu à visiter ?",
        "Español": "🔍 ¿Buscas una actividad o un lugar para visitar?",
    },
    "looking_filter_sub": {
        "English": "Use the filters below to discover your favorite spots in Rennes.",
        "Français": "Utilisez les filtres ci‑dessous pour découvrir vos endroits préférés à Rennes.",
        "Español": "Usa los filtros de abajo para descubrir tus lugares favoritos en Rennes.",
    },
}

# ---------- init state ----------
st.session_state.setdefault("current_view", "landing")  # landing | planning | arrived

# ---------- top nav ----------
c1, c2 = st.columns([1,1])
with c1:
    if st.session_state["current_view"] != "landing":
        if st.button(TEXT["home"][st.session_state["lang"]]):
            reset_home()
            st.rerun()
with c2:
    if st.session_state["current_view"] in ("planning", "arrived"):
        # quick switch between branches
        if st.session_state["current_view"] == "planning":
            if st.button(TEXT["switch_arrived"][st.session_state["lang"]]):
                set_current_view("arrived")
                st.rerun()
        else:
            if st.button(TEXT["switch_planning"][st.session_state["lang"]]):
                set_current_view("planning")
                st.rerun()

st.markdown("<hr style='border:1px solid #ddd;margin:20px 0;'>", unsafe_allow_html=True)

# =========================
# VIEWS
# =========================
view = st.session_state["current_view"]

# ---- LANDING ----
if view == "landing":
    st.subheader(TEXT["welcome"][st.session_state["lang"]])
    col1, col2 = st.columns(2)
    nationality = col1.selectbox("Your nationality", options=nationalities["name"].tolist(), index=0)
    destination = col2.selectbox("Where are you going?", options=cities["name"].tolist(), index=0)
    arrival_status = st.radio("Have you arrived?", ["Planning", "Already in Rennes"], horizontal=True)
    go = st.button(TEXT["continue"][st.session_state["lang"]], type="primary")

    if go:
        # store selections
        st.session_state["nationality"] = nationality
        st.session_state["destination"] = destination
        st.session_state["status"] = arrival_status
        # jump directly to next view (NO double click)
        set_current_view("planning" if arrival_status == "Planning" else "arrived")
        st.rerun()

# ---- PLANNING ----
elif view == "planning":
    # Modern GoLocal banners
    st.markdown(
        f'<div class="section-banner banner-blue">{TEXT["planning_banner"][st.session_state["lang"]]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="section-banner banner-blue">{TEXT["infohub_banner"][st.session_state["lang"]]}</div>',
        unsafe_allow_html=True,
    )

    with st.expander("🌍 About Rennes"):
        st.markdown(
            """
<div class="theme-box" style="padding: 8px; border-radius:8px;">
<strong>Rennes</strong> is the <strong>capital of Brittany</strong>, located in northwestern France. With a population of around <strong>220,000</strong>, it’s known for its <strong>large student community</strong>, welcoming atmosphere, and balance of culture and technology.<br>
<ul>
  <li>🎓 <strong>Education hub:</strong> Two major universities and many engineering &amp; business schools.</li>
  <li>🚄 <strong>Connected:</strong> 1h25 from Paris by TGV high‑speed train.</li>
  <li>🎭 <strong>Culture:</strong> Famous for music festivals, street art, and Breton heritage.</li>
  <li>🌦️ <strong>Climate:</strong> Mild oceanic climate – cool winters and moderate summers.</li>
</ul>
Rennes is small enough to get around easily but big enough to offer everything you need.
</div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("🛂 Visa Process"):
        st.markdown(
            """
<div class="theme-box" style="padding: 8px; border-radius:8px;">
If you are a <strong>non‑EU citizen</strong>, you’ll likely need a <strong>long‑stay visa (VLS‑TS)</strong> for studies or work.<br><br>
<strong>Student visa process:</strong>
<ol>
  <li>Apply through the <a href="https://www.campusfrance.org/" target="_blank">Campus France</a> platform (Études en France procedure).</li>
  <li>Once accepted by your university, book an appointment at your <strong>nearest French consulate</strong>.</li>
  <li>Prepare documents: acceptance letter, proof of resources (~€800/month), accommodation proof, passport, and photo.</li>
  <li>After arrival in France, validate your visa online within <strong>3 months</strong> at <a href="https://administration-etrangers-en-france.interieur.gouv.fr" target="_blank">administration-etrangers-en-france.interieur.gouv.fr</a>.</li>
</ol>
<br>
<strong>Work or other visas</strong> follow a similar process but require an employment contract or specific reason for stay.
</div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("🤝 Understanding the Guarantor System"):
        st.markdown(
            """
<div class="theme-box" style="padding: 8px; border-radius:8px;">
In France, landlords usually ask for a <strong>guarantor (garant)</strong> — someone who commits to paying your rent if you cannot.<br>
<br>
Options:
<ul>
  <li>👪 <strong>Family or friend guarantor</strong> living in France.</li>
  <li>💼 <strong>VISALE guarantee:</strong> A <strong>free government service</strong> that can act as your guarantor. Apply online at <a href="https://www.visale.fr/" target="_blank">visale.fr</a>.</li>
  <li>🏦 Some private rental insurance companies also offer paid guarantee options.</li>
</ul>
You’ll need to provide your guarantor’s proof of income or the VISALE certificate as part of your rental file.
</div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("🏠 Housing Basics"):
        st.markdown(
            """
<div class="theme-box" style="padding: 8px; border-radius:8px;">
<strong>Common accommodation types:</strong>
<ul>
  <li>🏢 <strong>Studios (T1)</strong> – €400‑€600/month</li>
  <li>👥 <strong>Shared flats (colocation)</strong> – €350‑€500/month</li>
  <li>🏡 <strong>1‑bedroom apartments (T2)</strong> – €550‑€800/month</li>
  <li>🎓 <strong>Student residences (CROUS/private)</strong> – €250‑€450/month</li>
</ul>
<strong>Documents you’ll need:</strong>
<ul>
  <li>Passport or ID</li>
  <li>Proof of enrollment or employment</li>
  <li>Proof of income or guarantor</li>
  <li>VISALE or guarantee letter</li>
</ul>
<br>
💡 <strong>Tip:</strong> Start searching early (June–August) and beware of scams; always visit or verify the property before sending money.
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border:1px solid #eee;margin:10px 0;'>", unsafe_allow_html=True)

    # Checklists
    for _, cl in checklists[checklists["stage"]=="Planning"].iterrows():
        with st.expander(f"✅ {cl['title']}"):
            st.markdown('<div class="theme-box" style="padding: 8px; border-radius:8px;">', unsafe_allow_html=True)
            items = checklist_items[checklist_items["checklist_id"]==cl["checklist_id"]]
            for _, it in items.iterrows():
                st.checkbox(it["text"], key=f"{cl['checklist_id']}_{it['item_id']}")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid #eee;margin:10px 0;'>", unsafe_allow_html=True)

    st.info("💡 Looking for planning guides? See 'Banking Setup' and 'Phone/SIM & Internet' below.")

    # Show planning guides: posts in categories 'banking' or 'communication'
    planning_category_ids = ["banking", "communication"]
    planning_posts = posts[posts["category_id"].isin(planning_category_ids)]
    for _, post in planning_posts.iterrows():
        with st.expander(f"📄 {post['title']} — {post['summary']}"):
            st.markdown(
                f'<div class="theme-box" style="padding: 8px; border-radius:8px;">{post["body_md"]}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("<hr style='border:1px solid #eee;margin:10px 0;'>", unsafe_allow_html=True)

# ---- ARRIVED ----
elif view == "arrived":
    # Tabs for Lifestyle vs Administrative vs Community
    tabs = st.tabs(["🌆 Lifestyle", "🏛️ Administrative", "👥 Community"])

    with tabs[0]:
        st.markdown(
            f'<div class="section-banner banner-green">{TEXT["explore_banner"][st.session_state["lang"]]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="theme-box" style="padding:18px; border-radius:12px; margin-bottom:20px; font-size:1.05em; line-height:1.6;">
                <p>Rennes offers a unique mix of <strong>vibrant culture</strong>, <strong>green spaces</strong>, and a <strong>thriving student community</strong>. The city blends its rich Breton heritage with modern energy — perfect for professionals, students, and newcomers alike.</p>
                <p>🕺 Enjoy local festivals like <strong>Les Trans Musicales</strong> and open-air events, explore cozy cafés and art galleries, and stroll through parks like <strong>Thabor Gardens</strong>. With a compact city center, everything is within reach — from nightlife to nature trails.</p>
                <p>💡 Whether you're looking to socialize, study, or relax, Rennes offers a lifestyle that's both dynamic and welcoming.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Get unique normalized types for dropdown display
        unique_normalized_types = sorted(places["type_normalized"].unique())
        # Map normalized types back to a display version (capitalize first letter)
        normalized_to_display = {t: t.capitalize() for t in unique_normalized_types}
        display_types = ["All"] + [normalized_to_display[t] for t in unique_normalized_types]

        # --- Insert a title above the filters encouraging exploration ---
        st.markdown(
            f"""
            <h3 style="font-family:'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#00B4D8; margin-bottom:8px; text-align:center;">
                {TEXT["looking_filter_title"][st.session_state["lang"]]}
            </h3>
            <p style="text-align:center; color:var(--text-color); font-size:1.05em; margin-top:0;">
                {TEXT["looking_filter_sub"][st.session_state["lang"]]}
            </p>
            """,
            unsafe_allow_html=True,
        )
        t_display = st.selectbox("Type", options=display_types, index=0, key="lifestyle_type")
        t_norm = normalize_type(t_display) if t_display != "All" else "all"
        neighs = ["All"] + sorted(places["neighborhood"].unique().tolist())
        n = st.selectbox("Neighborhood", options=neighs, index=0, key="lifestyle_neighborhood")

        # Emoji mapping for normalized types
        emoji_map = {
            "restaurant": "🍽️",
            "restaurants": "🍽️",
            "cafe": "☕",
            "cafes": "☕",
            "bar": "🍸",
            "bars": "🍸",
            "park": "🏞️",
            "parks": "🏞️",
            "activity": "🏞️",
            "activities": "🏞️",
            "cowork": "💼",
            "coworking": "💼",
        }

        def render_stars(rating):
            try:
                rating_float = float(rating)
                full_stars = int(rating_float)
                half_star = rating_float - full_stars >= 0.5
                stars = "⭐" * full_stars
                if half_star:
                    stars += "⭐"  # Using full star for half star for simplicity
                return stars
            except:
                return ""

        # Determine which types to show based on selection
        if t_norm != "all":
            types_to_show = [t_norm]
        else:
            types_to_show = unique_normalized_types

        # Always start from the full places DataFrame
        df_places = places.copy()



        for group_type_norm in types_to_show:
            group_df = df_places[df_places["type_normalized"] == group_type_norm]
            if n != "All":
                group_df = group_df[group_df["neighborhood"] == n]

            # Sort by rating descending if rating column exists
            if "rating" in group_df.columns:
                group_df = group_df.copy()
                group_df["rating_numeric"] = pd.to_numeric(group_df["rating"], errors='coerce').fillna(-1)
                group_df = group_df.sort_values(by="rating_numeric", ascending=False)
            else:
                group_df["rating_numeric"] = -1  # dummy column for uniformity

            emoji = emoji_map.get(group_type_norm, "🏞️")
            display_type_name = normalized_to_display.get(group_type_norm, group_type_norm.capitalize())
            plural_name = display_type_name + ("s" if not display_type_name.endswith("s") else "")

            st.markdown(f"**{emoji} {plural_name}**")

            if group_df.empty:
                st.info(f"No {plural_name.lower()} match your selection.")
            else:
                for _, row in group_df.iterrows():
                    website = safe_str(row.get("website"))
                    map_url = safe_str(row.get("map_url"))
                    website_ok = website and website.lower() != "nan"
                    map_ok = map_url and map_url.lower() != "nan"
                    links = []
                    if website_ok:
                        links.append(f"<a href='{website}' target='_blank'>🌐 Website</a>")
                    if map_ok:
                        links.append(f"<a href='{map_url}' target='_blank'>🗺️ Map</a>")
                    links_html = " | ".join(links)

                    name = safe_str(row.get('name'))
                    address = safe_str(row.get('address'))
                    rating_val = safe_str(row.get("rating"))
                    rating_display = ""
                    if rating_val and rating_val.lower() != "nan":
                        try:
                            rating_float = float(rating_val)
                            stars = render_stars(rating_float)
                            rating_display = f"{stars} {rating_float:.1f} / 5"
                        except:
                            rating_display = rating_val
                    short_blurb = safe_str(row.get('short_blurb'))
                    price_level = safe_str(row.get('price_level'))
                    place_type = safe_str(row.get('type'))
                    hours = safe_str(row.get('hours')) if 'hours' in places.columns else ""
                    phone = safe_str(row.get('phone')) if 'phone' in places.columns else ""
                    category = safe_str(row.get('category')) if 'category' in places.columns else ""

                    links_html_clean = f"""
<div style='margin-top:8px; font-weight:500; color:#004080;'>
    {links_html if links_html else ''}
</div>
"""

            card_html = f"""
<div class="theme-box" style="
    background-color: var(--card-bg);
    color: var(--text-color);
    padding:18px;
    border-radius:10px;
    margin-bottom:18px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    line-height:1.5;
">
    <strong style="font-size:1.3em; color:var(--text-color);">{emoji} {name}</strong><br>
    <small style="color:var(--text-color);">📍 {address}</small><br>
    <span style="color:#b8860b; font-weight: 600;">⭐ {rating_display}</span><br>
    <em style="color:var(--text-color);">💬 {short_blurb}</em><br>
    <small style="color:var(--text-color);">💰 {place_type} · {price_level}</small><br>
    {f'<small style=\"color:var(--text-color);\">⏰ Hours: {hours}</small><br>' if hours else ''}
    {f'<small style=\"color:var(--text-color);\">☎️ Phone: {phone}</small><br>' if phone else ''}
    {f'<small style=\"color:var(--text-color);\">📂 Category: {category}</small><br>' if category else ''}
    {links_html_clean}
</div>
"""
            st.markdown(card_html, unsafe_allow_html=True)

    with tabs[1]:
        st.markdown(
            f'<div class="section-banner banner-pink">{TEXT["admin_banner"][st.session_state["lang"]]}</div>',
            unsafe_allow_html=True,
        )

        # New logic: Display admin guides by matching category names directly, not by parent_category_id
        admin_main_categories = {
            "housing": {
                "display": "Housing",
                "desc": "Guides and resources related to finding and managing housing in Rennes.",
                "icon": "🏠",
            },
            "transport": {
                "display": "Transport",
                "desc": "Information about public transport, commuting, and travel options.",
                "icon": "🚆",
            },
            "healthcare": {
                "display": "Healthcare",
                "desc": "Details on accessing healthcare services and insurance.",
                "icon": "🏥",
            },
            "legal": {
                "display": "Legal Paperwork",
                "desc": "Step-by-step guides for legal documentation and permits.",
                "icon": "📄",
            },
            "cost": {
                "display": "Cost of Living",
                "desc": "Insights into budgeting and managing expenses in Rennes.",
                "icon": "💶",
            },
        }

        posts_filled = posts.fillna("")
        categories_filled = categories.fillna("")

        # Build category name->category_id mapping (lowercase for match)
        cat_name_to_id = {row["name"].strip().lower(): row["category_id"] for _, row in categories_filled.iterrows()}

        for cat_key, cat_info in admin_main_categories.items():
            cat_display = cat_info["display"]
            cat_desc = cat_info["desc"]
            cat_icon = cat_info["icon"]
            cat_id = cat_name_to_id.get(cat_key, None)

            with st.expander(f"📂 {cat_display}"):
                if cat_key == "housing":
                    st.markdown(
                        """
<div class="theme-box" style="font-family: Arial, sans-serif; line-height: 1.6; border-radius:8px; padding:8px;">
  <h3>🏠 How to Find Housing in Rennes</h3>
  <p>Looking for accommodation in Rennes? Here’s a comprehensive guide with local tips, recommended neighborhoods, resources, and practical advice to help you settle in smoothly!</p>

  <h4>📍 <u>Recommended Neighborhoods</u></h4>
  <ul>
    <li><b>Centre</b>: The vibrant city center, close to shops, restaurants, nightlife, and public transport.</li>
    <li><b>Thabor</b>: Peaceful, green, and family-friendly near Parc du Thabor.</li>
    <li><b>Saint-Hélier</b>: Cosmopolitan, central, and convenient for transport and shops.</li>
    <li><b>Jeanne d’Arc</b>: Quiet, residential, and well-connected.</li>
    <li><b>Arsenal-Redon, Bourg-l’Évêque</b>: Good value neighborhoods near the center.</li>
  </ul>

  <h4>⚠️ <u>Areas to Visit and Consider Carefully</u></h4>
  <ul>
    <li><b>Kennedy</b>: Affordable and diverse but further from the city center — visit before choosing.</li>
    <li><b>Maurepas</b>: Economical but less lively; check it fits your needs.</li>
  </ul>
  <p style="font-size: 0.95em; color: #888;">These areas are not unsafe, just less convenient for newcomers.</p>

  <h4>💡 <u>Housing Types</u></h4>
  <ul>
    <li>Studio (T1): €400–€600/month</li>
    <li>Shared flat (colocation): €350–€500/month</li>
    <li>1-bedroom (T2): €550–€800/month</li>
    <li>Student residence: €250–€450/month</li>
  </ul>

  <h4>🔗 <u>Where to Search</u></h4>
  <ul>
    <li><a href="https://www.leboncoin.fr/" target="_blank">Le Bon Coin</a></li>
    <li><a href="https://www.seloger.com/" target="_blank">SeLoger</a></li>
    <li><a href="https://www.studapart.com/" target="_blank">Studapart</a></li>
    <li><a href="https://www.crous-rennes.fr/logements/" target="_blank">CROUS Rennes</a></li>
  </ul>

  <h4>💡 <u>Documents & Practical Tips</u></h4>
  <ul>
    <li>Prepare a <b>dossier</b>: ID, income proof, and guarantor info.</li>
    <li>Use <a href="https://www.visale.fr/" target="_blank">VISALE</a> for free rental guarantee.</li>
    <li>Expect a one-month <b>deposit</b> and possible <b>agency fees</b>.</li>
    <li>Read your <b>rental contract</b> (“bail”) carefully before signing.</li>
  </ul>

  <p>Good luck with your search and welcome to Rennes! 🦞</p>
</div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown(f'<div class="theme-box" style="border-radius:8px; padding:8px;"><strong>{cat_desc}</strong></div>', unsafe_allow_html=True)
                # Show posts for this category name directly
                if cat_id:
                    cat_posts = posts_filled[posts_filled["category_id"] == cat_id]
                else:
                    # fallback: try to match posts by category_id == cat_key directly
                    cat_posts = posts_filled[posts_filled["category_id"] == cat_key]
                import re
                def markdown_to_html(md):
                    # Convert Markdown tables to HTML tables
                    def table_repl(match):
                        table_md = match.group(0)
                        lines = [line.strip() for line in table_md.strip().split('\n') if line.strip()]
                        rows = []
                        for line in lines:
                            # Ignore separator lines (containing only | --- | --- | etc)
                            if re.match(r"^\|\s*:?-{2,}.*\|$", line.replace(' ', '')):
                                continue
                            # Remove leading/trailing '|', then split
                            cells = [cell.strip() for cell in line.strip('|').split('|')]
                            tds = ''.join([f'<td style="border: 1px solid #ccc; padding: 6px;">{cell}</td>' for cell in cells])
                            rows.append(f'<tr>{tds}</tr>')
                        if not rows:
                            return table_md  # fallback
                        table_html = (
                            '<table style="border-collapse: collapse; width: 100%; text-align:left; margin-bottom: 1em;">'
                            + ''.join(rows) +
                            '</table>'
                        )
                        return table_html

                    # Headings: ### and ####
                    html = md
                    html = re.sub(r"^####\s*(.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
                    html = re.sub(r"^###\s*(.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
                    # Bold: **text** or __text__
                    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
                    html = re.sub(r"__(.+?)__", r"<strong>\1</strong>", html)
                    # Inline links: [text](url)
                    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', html)
                    # Unordered lists: lines starting with -
                    def ul_repl(match):
                        items = match.group(0).strip().split('\n')
                        lis = ''.join(f"<li>{re.sub(r'^-\\s*', '', item).strip()}</li>" for item in items)
                        return f"<ul>{lis}</ul>"
                    html = re.sub(r"((?:^\-\s+.*(?:\n|$))+)", ul_repl, html, flags=re.MULTILINE)
                    # Markdown tables: lines with | ... | (at least 2 lines)
                    html = re.sub(
                        r"((?:^\|.*\|\n?){2,})",
                        table_repl,
                        html,
                        flags=re.MULTILINE
                    )
                    # Blank lines to <br>
                    html = re.sub(r"\n\s*\n", "<br>", html)
                    # Single newlines to <br> (but not inside <ul> or <table>)
                    def br_outside_blocks(m):
                        s = m.group(0)
                        # Don't add <br> if inside <ul> or <table>
                        if any(tag in s for tag in ("</ul>", "<ul>", "<table>", "</table>")):
                            return s
                        return s.replace("\n", "<br>")
                    html = re.sub(r"([^\n]+)\n([^\n]+)", lambda m: m.group(1) + "<br>" + m.group(2), html)
                    return html

                if not cat_posts.empty:
                    for _, post in cat_posts.iterrows():
                        post_title = post.get("title", "").strip()
                        post_summary = post.get("summary", "").strip()
                        post_body = post.get("body_md", "").strip()

                        if post_title:
                            st.markdown(f"#### {post_title}")
                        if post_summary:
                            st.caption(post_summary)
                        else:
                            st.caption("No summary available.")
                        if post_body:
                            post_body_html = markdown_to_html(post_body)
                            st.markdown(
                                f'<div class="theme-box" style="border-radius:8px; padding:8px;">{post_body_html}</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.info("Content not available for this guide.")
                        st.markdown("<hr style='border:1px solid #eee;margin:10px 0;'>", unsafe_allow_html=True)
                else:
                    st.info("No guides available in this section yet.")


    with tabs[2]:
        st.markdown(
            f'<div class="section-banner banner-blue">{TEXT["community_banner"][st.session_state["lang"]]}</div>',
            unsafe_allow_html=True,
        )

        import csv

        community_file = Path(__file__).parent / "community.csv"
        if community_file.exists():
            community_data = pd.read_csv(community_file)
        else:
            community_data = pd.DataFrame(
                [
                    {"type": "question", "title": "Where can I find good second-hand bikes?", "content": "Locals often recommend the market near Place Sainte-Anne!", "author": "Alice"},
                    {"type": "recommendation", "title": "Open Mic Night", "content": "Every Thursday at Le Papier Timbré — live music and poetry!", "author": "Lucas"},
                    {"type": "recommendation", "title": "Sunday Flea Market", "content": "Don’t miss the vintage stands at Les Lices!", "author": "Marie"},
                    {"type": "question", "title": "Any good coworking spaces for students?", "content": "Check out La Cordée or Le Loft Coworking.", "author": "Tom"},
                ]
            )
            community_data.to_csv(community_file, index=False)

        st.markdown("### 💬 Ask Locals")
        questions = community_data[community_data["type"] == "question"]
        for _, q in questions.iterrows():
            st.markdown(
                f"""
                <div class="theme-box" style="background-color: var(--card-bg); padding:12px; border-radius:8px; margin-bottom:10px;">
                    <strong>❓ {q['title']}</strong><br>
                    <em>{q['content']}</em><br>
                    <small>👤 {q['author']}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("### 🎉 Local Recommendations")
        recs = community_data[community_data["type"] == "recommendation"]
        for _, r in recs.iterrows():
            st.markdown(
                f"""
                <div class="theme-box" style="background-color: var(--card-bg); padding:12px; border-radius:8px; margin-bottom:10px;">
                    <strong>📍 {r['title']}</strong><br>
                    <em>{r['content']}</em><br>
                    <small>👤 Recommended by {r['author']}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

# Footer divider
st.markdown("<hr style='border:1px solid #ddd;margin:20px 0;'>", unsafe_allow_html=True)
