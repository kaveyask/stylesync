"""
app.py
StyleSync -- Intelligent Wardrobe & Outfit Matching System
Run with:  streamlit run app.py
"""

import os
import streamlit as st

import database as db
import outfit_logic as logic
from silhouette import draw_silhouette, SKIN_TONES, COLOR_HEX

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
db.init_db()

st.set_page_config(
    page_title="StyleSync | Outfit Matcher",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# Custom styling -- gradient header, rounded cards, soft shadows
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu, footer {visibility: hidden;}

        .stApp {
            background: linear-gradient(180deg, #F7F5FB 0%, #EFEAF7 100%);
        }

        .hero {
            background: linear-gradient(120deg, #6C63FF 0%, #A084FF 60%, #FF9AC6 100%);
            padding: 2.2rem 2rem;
            border-radius: 20px;
            color: white;
            margin-bottom: 1.6rem;
            box-shadow: 0 10px 30px rgba(108, 99, 255, 0.25);
        }
        .hero h1 {
            margin: 0;
            font-size: 2.3rem;
            font-weight: 800;
        }
        .hero p {
            margin: 0.3rem 0 0 0;
            opacity: 0.92;
            font-size: 1.02rem;
        }

        div[data-testid="stMetric"] {
            background: white;
            padding: 1rem 1.2rem;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(108, 99, 255, 0.08);
        }

        .item-card {
            background: white;
            border-radius: 16px;
            padding: 0.8rem;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            margin-bottom: 1rem;
        }

        .swatch {
            display: inline-block;
            width: 14px; height: 14px;
            border-radius: 50%;
            margin-right: 6px;
            vertical-align: middle;
            border: 1px solid rgba(0,0,0,0.15);
        }

        .outfit-panel {
            background: white;
            border-radius: 20px;
            padding: 1.6rem;
            box-shadow: 0 6px 22px rgba(108, 99, 255, 0.12);
        }

        div.stButton > button {
            border-radius: 12px;
            font-weight: 600;
            border: none;
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(120deg, #6C63FF, #A084FF);
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>👕 StyleSync</h1>
        <p>Your smart wardrobe &amp; outfit matcher -- upload, tag, and let the rules do the styling.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_dash, tab_add, tab_wardrobe, tab_suggest = st.tabs(
    ["🏠 Dashboard", "➕ Add Item", "👚 My Wardrobe", "✨ Suggest Outfit"]
)

# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
with tab_dash:
    total, week, last = db.get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Wardrobe Items", total)
    c2.metric("Outfits Worn This Week", week)
    c3.metric("Last Outfit Logged", str(last) if last else "—")

    st.markdown("#### Wardrobe breakdown")
    items = db.get_items()
    if items:
        cols = st.columns(3)
        for i, t in enumerate(["top", "bottom", "shoes"]):
            count = len([x for x in items if x["type"] == t])
            cols[i].info(f"**{t.title()}s:** {count}")
    else:
        st.info("Your wardrobe is empty -- add items in the **Add Item** tab.")

# ------------------------------------------------------------------
# Add Item
# ------------------------------------------------------------------
with tab_add:
    st.subheader("Add a clothing item")
    with st.form("add_item_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            type_ = st.selectbox("Type", ["top", "bottom", "shoes"])
            name = st.text_input("Name", placeholder="e.g. Blue Denim Shirt")
            color = st.selectbox("Color", sorted(COLOR_HEX.keys()))
        with col2:
            occasion = st.selectbox("Occasion", ["casual", "formal", "sport", "party"])
            photo = st.file_uploader("Photo (optional)", type=["jpg", "jpeg", "png"])

        submitted = st.form_submit_button("Add to Wardrobe", type="primary")
        if submitted:
            if not name.strip():
                st.error("Please give the item a name.")
            else:
                image_path = ""
                if photo is not None:
                    image_path = os.path.join(UPLOAD_DIR, photo.name)
                    with open(image_path, "wb") as f:
                        f.write(photo.getbuffer())
                db.add_item(type_, name.strip(), color, occasion, image_path)
                st.success(f"Added **{name}** to your wardrobe!")

# ------------------------------------------------------------------
# My Wardrobe
# ------------------------------------------------------------------
with tab_wardrobe:
    st.subheader("My Wardrobe")
    items = db.get_items()
    if not items:
        st.info("No items yet -- add some in the **Add Item** tab.")
    else:
        filter_type = st.selectbox("Filter by type", ["all", "top", "bottom", "shoes"])
        shown = items if filter_type == "all" else [i for i in items if i["type"] == filter_type]

        cols = st.columns(4)
        for i, item in enumerate(shown):
            with cols[i % 4]:
                st.markdown("<div class='item-card'>", unsafe_allow_html=True)
                if item["image_path"] and os.path.exists(item["image_path"]):
                    st.image(item["image_path"], use_container_width=True)
                swatch_hex = COLOR_HEX.get(item["color"].lower(), "#ccc")
                st.markdown(f"**{item['name']}**")
                st.markdown(
                    f"<span class='swatch' style='background:{swatch_hex}'></span>"
                    f"{item['color'].title()} · {item['type'].title()} · {item['occasion'].title()}",
                    unsafe_allow_html=True,
                )
                if st.button("🗑 Delete", key=f"del_{item['id']}"):
                    db.delete_item(item["id"])
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Suggest Outfit
# ------------------------------------------------------------------
with tab_suggest:
    st.subheader("Get today's outfit")

    col_a, col_b = st.columns(2)
    with col_a:
        skin_tone = st.select_slider("Skin tone", options=list(SKIN_TONES.keys()), value="Medium")
    with col_b:
        occasion_filter = st.selectbox("Occasion", ["casual", "formal", "sport", "party"], key="occasion_pick")

    if st.button("✨ Suggest an outfit", type="primary"):
        tops = [i for i in db.get_items("top") if i["occasion"] == occasion_filter]
        bottoms = [i for i in db.get_items("bottom") if i["occasion"] == occasion_filter]
        shoes = [i for i in db.get_items("shoes") if i["occasion"] == occasion_filter]

        if not (tops and bottoms and shoes):
            st.warning(
                f"Not enough **{occasion_filter}** items yet. "
                "Make sure you have at least one top, bottom, and pair of shoes tagged for this occasion."
            )
            st.session_state.pop("outfit", None)
        else:
            valid = logic.generate_valid_outfits(tops, bottoms, shoes)
            if not valid:
                st.warning("No color-compatible combination found. Try adding more variety to your wardrobe.")
                st.session_state.pop("outfit", None)
            else:
                recent = db.get_recent_outfit_ids()
                st.session_state["outfit"] = logic.pick_outfit(valid, recent)
                st.session_state["skin_tone"] = skin_tone

    if "outfit" in st.session_state and st.session_state["outfit"]:
        top, bottom, shoe = st.session_state["outfit"]
        st.markdown("<div class='outfit-panel'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1.3])
        with col1:
            img = draw_silhouette(
                top["color"], bottom["color"], shoe["color"],
                st.session_state.get("skin_tone", skin_tone),
            )
            st.image(img, use_container_width=True)
        with col2:
            st.markdown("##### Today's match")
            st.markdown(f"👕 **Top:** {top['name']}  ·  {top['color'].title()}")
            st.markdown(f"👖 **Bottom:** {bottom['name']}  ·  {bottom['color'].title()}")
            st.markdown(f"👟 **Shoes:** {shoe['name']}  ·  {shoe['color'].title()}")
            st.write("")
            if st.button("✅ Wear this today", type="primary"):
                db.log_outfit(top["id"], bottom["id"], shoe["id"])
                st.success("Logged! StyleSync will avoid repeating this for the next few days.")
                del st.session_state["outfit"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
