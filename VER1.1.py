import streamlit as st
import pandas as pd
from pathlib import Path
import unicodedata

st.set_page_config(page_title="Rennes Relocation (Mock)", page_icon="🦞", layout="centered")

DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    cities = pd.read_csv(DATA_DIR / "cities.csv")
    nationalities = pd.read_csv(DATA_DIR / "nationalities.csv")
    categories = pd.read_csv(DATA_DIR / "categories.csv")
    posts = pd.read_csv(DATA_DIR / "posts.csv")
    places = pd.read_csv(DATA_DIR / "places.csv")
    checklists = pd.read_csv(DATA_DIR / "checklists.csv")
    checklist_items = pd.read_csv(DATA_DIR / "checklist_items.csv")
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
    <div style="background-color:#f0f8ff; padding: 20px; border-radius: 10px; text-align:center; margin-bottom: 20px;">
        <h1 style="color:#007ACC; font-weight: 700; margin: 0;"> Rennes Relocation — Mock Prototype</h1>
        <p style="color:#555; font-size:18px; margin-top:5px;">Your guide to moving and living in Rennes</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- init state ----------
st.session_state.setdefault("current_view", "landing")  # landing | planning | arrived

# ---------- top nav ----------
c1, c2 = st.columns([1,1])
with c1:
    if st.button("🏠 Home"):
        reset_home()
with c2:
    if st.session_state["current_view"] in ("planning", "arrived"):
        # quick switch between branches
        if st.session_state["current_view"] == "planning":
            if st.button("🔄 Switch to Already in Rennes"):
                set_current_view("arrived")
        else:
            if st.button("🔄 Switch to Planning"):
                set_current_view("planning")

st.markdown("<hr style='border:1px solid #ddd;margin:20px 0;'>", unsafe_allow_html=True)

# =========================
# VIEWS
# =========================
view = st.session_state["current_view"]

# ---- LANDING ----
if view == "landing":
    st.subheader("Welcome! Let's get started 🛫")
    col1, col2 = st.columns(2)
    nationality = col1.selectbox("Your nationality", options=nationalities["name"].tolist(), index=0)
    destination = col2.selectbox("Where are you going?", options=cities["name"].tolist(), index=0)
    arrival_status = st.radio("Have you arrived?", ["Planning", "Already in Rennes"], horizontal=True)
    go = st.button("Continue", type="primary")

    if go:
        # store selections
        st.session_state["nationality"] = nationality
        st.session_state["destination"] = destination
        st.session_state["status"] = arrival_status
        # jump directly to next view (NO double click)
        set_current_view("planning" if arrival_status == "Planning" else "arrived")
        st.experimental_rerun()

# ---- PLANNING ----
elif view == "planning":
    st.markdown(
        """
        <div style="background-color:#e6f2ff; padding:15px; border-radius:8px; margin-bottom:20px;">
        <h2 style="color:#0059b3; margin:0;">📝 Pre-Departure Essentials</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Checklists
    for _, cl in checklists[checklists["stage"]=="Planning"].iterrows():
        with st.expander(f"✅ {cl['title']}"):
            items = checklist_items[checklist_items["checklist_id"]==cl["checklist_id"]]
            for _, it in items.iterrows():
                st.checkbox(it["text"], key=f"{cl['checklist_id']}_{it['item_id']}")
        st.markdown("<hr style='border:1px solid #eee;margin:10px 0;'>", unsafe_allow_html=True)

    st.info("💡 Looking for planning guides? See 'Banking Setup' and 'Phone/SIM & Internet' below.")

    # Show planning guides: posts in categories 'banking' or 'communication'
    planning_category_ids = ["banking", "communication"]
    planning_posts = posts[posts["category_id"].isin(planning_category_ids)]
    for _, post in planning_posts.iterrows():
        with st.expander(f"📄 {post['title']} — {post['summary']}"):
            st.markdown(post["body_md"], unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid #eee;margin:10px 0;'>", unsafe_allow_html=True)

# ---- ARRIVED ----
elif view == "arrived":
    # Tabs for Lifestyle vs Administrative
    tabs = st.tabs(["🌆 Lifestyle", "🏛️ Administrative"])

    with tabs[0]:
        st.markdown(
            """
            <div style="background-color:#e6ffe6; padding:15px; border-radius:8px; margin-bottom:20px;">
            <h2 style="color:#228B22; margin:0;">🌆 Explore Rennes</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Get unique normalized types for dropdown display
        unique_normalized_types = sorted(places["type_normalized"].unique())
        # Map normalized types back to a display version (capitalize first letter)
        normalized_to_display = {t: t.capitalize() for t in unique_normalized_types}
        display_types = ["All"] + [normalized_to_display[t] for t in unique_normalized_types]

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

        # Section header above all place categories
        st.markdown(
            """
            <div style="background-color:#d9f9d9; padding:15px; border-radius:8px; margin-bottom:20px;">
                <h3 style="color:#2e8b57; margin:0;">🏙️ Top Spots & Activities in Rennes</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
<div style="
    background-color:#ffffff;
    color:#111;
    padding:18px;
    border-radius:10px;
    margin-bottom:18px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    line-height:1.5;
">
    <strong style="font-size:1.3em; color:#000;">{emoji} {name}</strong><br>
    <small style="color:#333;">📍 {address}</small><br>
    <span style="color:#b8860b; font-weight: 600;">⭐ {rating_display}</span><br>
    <em style="color:#444;">💬 {short_blurb}</em><br>
    <small style="color:#333;">💰 {place_type} · {price_level}</small><br>
    {f'<small style="color:#333;">⏰ Hours: {hours}</small><br>' if hours else ''}
    {f'<small style="color:#333;">☎️ Phone: {phone}</small><br>' if phone else ''}
    {f'<small style="color:#333;">📂 Category: {category}</small><br>' if category else ''}
    {links_html_clean}
</div>
"""
                    st.markdown(card_html, unsafe_allow_html=True)

    with tabs[1]:
        st.markdown(
            """
            <div style="background-color:#ffe6f2; padding:15px; border-radius:8px; margin-bottom:20px;">
            <h2 style="color:#cc3399; margin:0;">🏛️ Administrative Guides</h2>
            </div>
            """,
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
<div style="font-family: Arial, sans-serif; line-height: 1.6;">
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
                st.markdown(f"**{cat_desc}**")
                # Show posts for this category name directly
                if cat_id:
                    cat_posts = posts_filled[posts_filled["category_id"] == cat_id]
                else:
                    # fallback: try to match posts by category_id == cat_key directly
                    cat_posts = posts_filled[posts_filled["category_id"] == cat_key]
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
                            st.markdown(post_body)
                        else:
                            st.info("Content not available for this guide.")
                        st.markdown("<hr style='border:1px solid #eee;margin:10px 0;'>", unsafe_allow_html=True)
                else:
                    st.info("No guides available in this section yet.")

# Footer divider
st.markdown("<hr style='border:1px solid #ddd;margin:20px 0;'>", unsafe_allow_html=True)