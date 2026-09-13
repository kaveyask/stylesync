"""
app.py
StyleSync -- Intelligent Wardrobe & Outfit Matching System
Run with: streamlit run app.py
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
    page_title="StyleSync | Your Personal Stylist",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# StyleSync visual theme — inspired by the supplied reference
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

        .stApp {
            background:
                radial-gradient(circle at 10% 4%, rgba(245,214,255,.80), transparent 24%),
                radial-gradient(circle at 92% 12%, rgba(255,215,242,.65), transparent 25%),
                linear-gradient(180deg, #fbf7ff 0%, #f3edff 100%);
            color: #3c3150;
            font-family: 'DM Sans', sans-serif;
        }
        .block-container { max-width: 1240px; padding-top: 1.1rem; padding-bottom: 3rem; }

        .hero {
            position: relative; overflow: hidden; min-height: 170px;
            background: linear-gradient(110deg, #eee5ff 0%, #f9ecff 52%, #ffeaf7 100%);
            border: 1px solid rgba(126,94,206,.10);
            padding: 1.7rem 2rem; border-radius: 26px; color: #4e3971;
            margin-bottom: 1.15rem; box-shadow: 0 14px 36px rgba(112,82,158,.10);
        }
        .hero:before {
            content: "✦  ♡  ✦"; position: absolute; right: 30px; top: 18px;
            color: #aa8fe8; opacity: .45; font-size: 1.5rem; letter-spacing: 12px;
        }
        .hero h1 { margin: 0; font-family: 'Playfair Display', serif; font-size: 2.55rem; color: #49336d; }
        .hero p { margin: .35rem 0 0; color: #77678d; font-size: .98rem; max-width: 650px; }
        .hero-badge {
            display: inline-block; margin-top: .8rem; padding: .42rem .78rem;
            border: 1px solid rgba(126,94,206,.14); border-radius: 999px;
            background: rgba(255,255,255,.68); color: #7556b5; font-size: .78rem; font-weight: 700;
        }

        div[data-baseweb="tab-list"] {
            gap: 8px; background: rgba(255,255,255,.55); padding: 6px;
            border-radius: 16px; border: 1px solid rgba(126,94,206,.08);
        }
        button[data-baseweb="tab"] {
            border-radius: 12px !important; font-weight: 700 !important;
            color: #776b8d !important; transition: all .2s ease !important;
        }
        button[data-baseweb="tab"]:hover { color: #7556d6 !important; transform: translateY(-1px); }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #efe6ff, #ffe8f6) !important; color: #6847b5 !important;
        }

        div[data-testid="stMetric"], .mini-card, .item-card, .outfit-panel, .gender-card {
            background: rgba(255,255,255,.86);
            border: 1px solid rgba(126,94,206,.09);
            box-shadow: 0 9px 28px rgba(83,63,111,.08);
        }
        div[data-testid="stMetric"] { padding: 1rem 1.15rem; border-radius: 18px; }
        div[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: 0 13px 30px rgba(112,82,158,.13); }
        .mini-card { border-radius: 18px; padding: 1rem; text-align: center; }
        .item-card { border-radius: 20px; padding: .8rem; margin-bottom: 1rem; transition: transform .2s ease, box-shadow .2s ease; }
        .item-card:hover { transform: translateY(-4px); box-shadow: 0 15px 32px rgba(112,82,158,.14); }
        .item-card img { border-radius: 15px; }
        .outfit-panel { border-radius: 25px; padding: 1.2rem 1.35rem; }

        .section-kicker {
            color: #8668ce; font-size: .73rem; text-transform: uppercase;
            letter-spacing: 1.6px; font-weight: 800; margin-bottom: .12rem;
        }
        .style-note {
            background: linear-gradient(135deg, #f4edff, #fff0f8); border-radius: 16px;
            padding: .9rem 1rem; margin-top: .8rem;
            border: 1px solid rgba(126,94,206,.08); color: #645773;
        }
        .gender-card { border-radius: 19px; padding: 1rem 1.15rem; margin: .25rem 0 .8rem; }
        .gender-title { color: #4d3970; font-size: 1.03rem; font-weight: 800; margin-bottom: .15rem; }
        .gender-subtitle { color: #8a7c9b; font-size: .78rem; margin-bottom: .65rem; }

        div.stButton > button {
            border-radius: 13px; font-weight: 700;
            border: 1px solid rgba(126,94,206,.12);
            background: rgba(255,255,255,.84); color: #5d4b73;
            transition: transform .18s ease, box-shadow .18s ease;
        }
        div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(112,82,158,.12); }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(120deg, #a36df0, #e285c2);
            color: white; border: 0; box-shadow: 0 8px 20px rgba(145,92,212,.20);
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stFileUploader section { border-radius: 13px !important; }
        div[data-testid="stRadio"] label, div[data-testid="stSelectSlider"] label { color: #5d4d70; font-weight: 600; }
        .footer-note { text-align: center; color: #9a8fa8; font-size: .76rem; margin-top: 1.7rem; }

        .orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(2px); opacity: .35; }
        .orb.one { width: 90px; height: 90px; right: 4%; top: 26%; background: #f5d4ea; }
        .orb.two { width: 62px; height: 62px; left: 3%; bottom: 13%; background: #dcd1ff; }
    </style>
    <div class="orb one"></div><div class="orb two"></div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
        <h1>StyleSync ✨</h1>
        <p>Your personal wardrobe stylist — choose a style, match your pieces, and discover a look that feels made for you.</p>
        <span class="hero-badge">♡ Smart outfit matching · Personal style · Everyday confidence</span>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_dash, tab_add, tab_wardrobe, tab_suggest = st.tabs(
    ["🏠 Dashboard", "➕ Add Item", "👚 My Wardrobe", "✨ Style Me"]
)

# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
with tab_dash:
    total, week, last = db.get_stats()

    c1, c2, c3 = st.columns(3)
    c1.metric("Wardrobe pieces", total)
    c2.metric("Looks worn this week", week)
    c3.metric("Last look", str(last) if last else "Not yet")

    st.markdown("### Your wardrobe at a glance")
    items = db.get_items()
    if items:
        cols = st.columns(3)
        for col, label, key in zip(cols, ["Tops", "Bottoms", "Shoes"], ["top", "bottom", "shoes"]):
            count = len([x for x in items if x["type"] == key])
            with col:
                st.markdown(
                    f"<div class='mini-card'><div style='font-size:1.8rem'>{'👕' if key=='top' else '👖' if key=='bottom' else '👟'}</div>"
                    f"<b>{count}</b><br><span style='color:#777'>{label}</span></div>",
                    unsafe_allow_html=True,
                )
    else:
        st.info("Your wardrobe is waiting ✨ Add your first item in **Add Item**.")

# ------------------------------------------------------------------
# Add Item
# ------------------------------------------------------------------
with tab_add:
    st.markdown("<div class='section-kicker'>Build your closet</div>", unsafe_allow_html=True)
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

        submitted = st.form_submit_button("＋ Add to Wardrobe", type="primary")
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
                st.success(f"Added **{name}** to your wardrobe! ✨")
                st.balloons()

# ------------------------------------------------------------------
# My Wardrobe
# ------------------------------------------------------------------
with tab_wardrobe:
    st.markdown("<div class='section-kicker'>Everything you own</div>", unsafe_allow_html=True)
    st.subheader("My Wardrobe")
    items = db.get_items()
    if not items:
        st.info("No items yet — add some in the **Add Item** tab.")
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
                    f"<span class='swatch' style='display:inline-block;width:14px;height:14px;border-radius:50%;"
                    f"background:{swatch_hex};margin-right:6px;vertical-align:middle'></span>"
                    f"{item['color'].title()} · {item['type'].title()} · {item['occasion'].title()}",
                    unsafe_allow_html=True,
                )
                if st.button("🗑 Delete", key=f"del_{item['id']}"):
                    db.delete_item(item["id"])
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Style Me
# ------------------------------------------------------------------
with tab_suggest:
    st.markdown("<div class='section-kicker'>Personal styling</div>", unsafe_allow_html=True)
    st.subheader("What are we styling today?")

    # Reference-inspired mannequin preview
    preview_left, preview_right = st.columns(2)
    with preview_left:
        female_preview = draw_silhouette("white", "blue", "white", "Light", "Female", (240, 430))
        st.image(female_preview, use_container_width=False)
    with preview_right:
        male_preview = draw_silhouette("white", "black", "white", "Medium", "Male", (240, 430))
        st.image(male_preview, use_container_width=False)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            """
            <div class="gender-card">
                <div class="gender-title">Who is this outfit for?</div>
                <div class="gender-subtitle">Choose the gender to see the perfect look for your mannequin.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        gender = st.radio(
            "Gender",
            ["Female", "Male"],
            horizontal=True,
            key="gender_pick",
            label_visibility="collapsed",
        )
        skin_tone = st.select_slider(
            "Skin tone",
            options=list(SKIN_TONES.keys()),
            value="Medium",
            key="skin_tone_pick",
        )
    with col_b:
        occasion_filter = st.selectbox(
            "Occasion",
            ["casual", "formal", "sport", "party"],
            key="occasion_pick",
        )

        st.caption("We'll match your top, bottom and shoes using your wardrobe rules.")

    if st.button("✨ Create my look", type="primary"):
        tops = [i for i in db.get_items("top") if i["occasion"] == occasion_filter]
        bottoms = [i for i in db.get_items("bottom") if i["occasion"] == occasion_filter]
        shoes = [i for i in db.get_items("shoes") if i["occasion"] == occasion_filter]

        if not (tops and bottoms and shoes):
            st.warning(
                f"Not enough **{occasion_filter}** items yet. Add at least one top, bottom and pair of shoes for this occasion."
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
                st.session_state["gender"] = gender

    if "outfit" in st.session_state and st.session_state["outfit"]:
        top, bottom, shoe = st.session_state["outfit"]

        st.markdown("<div class='outfit-panel'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1.25])

        with col1:
            img = draw_silhouette(
                top_color=top["color"],
                bottom_color=bottom["color"],
                shoes_color=shoe["color"],
                skin_tone=st.session_state.get("skin_tone", skin_tone),
                gender=st.session_state.get("gender", gender),
            )
            st.image(img, use_container_width=True)

        with col2:
            st.markdown("<div class='section-kicker'>Your curated look</div>", unsafe_allow_html=True)
            st.markdown("### Today's match")
            st.markdown(f"👕 **Top:** {top['name']}  ·  {top['color'].title()}")
            st.markdown(f"👖 **Bottom:** {bottom['name']}  ·  {bottom['color'].title()}")
            st.markdown(f"👟 **Shoes:** {shoe['name']}  ·  {shoe['color'].title()}")

            st.markdown(
                f"""
                <div class="style-note">
                    <b>✦ Style note</b><br>
                    This {occasion_filter} look combines <b>{top['color'].title()}</b>,
                    <b>{bottom['color'].title()}</b> and <b>{shoe['color'].title()}</b>
                    for a balanced palette.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")
            if st.button("♡ Wear this today", type="primary"):
                db.log_outfit(top["id"], bottom["id"], shoe["id"])
                st.success("Look logged! We'll help you avoid repeating it for a few days. ✨")
                st.balloons()
                del st.session_state["outfit"]
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='footer-note'>Made with ♡ for easier everyday styling · StyleSync</div>",
    unsafe_allow_html=True,
)
