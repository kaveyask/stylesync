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
# StyleSync visual theme
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu, footer {visibility: hidden;}

        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

        .stApp {
            background:
                radial-gradient(circle at 8% 8%, rgba(255,154,198,.16), transparent 25%),
                radial-gradient(circle at 92% 18%, rgba(160,132,255,.18), transparent 28%),
                linear-gradient(180deg, #fbf9ff 0%, #f4effb 100%);
            font-family: 'DM Sans', sans-serif;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        /* Soft floating decoration */
        .orb {
            position: fixed;
            border-radius: 50%;
            pointer-events: none;
            z-index: 0;
            filter: blur(1px);
            opacity: .45;
            animation: floatOrb 7s ease-in-out infinite;
        }
        .orb.one { width: 110px; height: 110px; right: 5%; top: 24%; background: #ffd6e8; }
        .orb.two { width: 70px; height: 70px; left: 3%; bottom: 14%; background: #dcd2ff; animation-delay: -3s; }

        @keyframes floatOrb {
            0%,100% { transform: translateY(0) translateX(0); }
            50% { transform: translateY(-18px) translateX(8px); }
        }

        .hero {
            position: relative;
            overflow: hidden;
            background: linear-gradient(120deg, #6257e8 0%, #8c78f5 55%, #f28fbe 100%);
            padding: 2.35rem 2.3rem;
            border-radius: 28px;
            color: white;
            margin-bottom: 1.4rem;
            box-shadow: 0 18px 45px rgba(98,87,232,.22);
            animation: heroIn .7s ease-out both;
        }
        .hero:after {
            content: "✦  ♡  ✦";
            position: absolute;
            right: 35px;
            top: 22px;
            font-size: 2rem;
            opacity: .24;
            letter-spacing: 12px;
            animation: sparkle 3s ease-in-out infinite;
        }
        .hero h1 {
            margin: 0;
            font-family: 'Playfair Display', serif;
            font-size: 2.65rem;
            font-weight: 700;
            letter-spacing: -.5px;
        }
        .hero p {
            margin: .45rem 0 0;
            opacity: .93;
            font-size: 1.03rem;
        }
        .hero-badge {
            display: inline-block;
            margin-top: 1rem;
            padding: .42rem .8rem;
            border: 1px solid rgba(255,255,255,.28);
            border-radius: 999px;
            background: rgba(255,255,255,.13);
            font-size: .82rem;
            font-weight: 600;
        }

        @keyframes heroIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes sparkle {
            0%,100% { transform: rotate(0deg) scale(1); }
            50% { transform: rotate(8deg) scale(1.06); }
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            font-weight: 700 !important;
            border-radius: 12px 12px 0 0 !important;
            transition: all .2s ease !important;
        }
        button[data-baseweb="tab"]:hover {
            color: #6c63ff !important;
            transform: translateY(-2px);
        }

        /* Cards */
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,.88);
            padding: 1.1rem 1.25rem;
            border-radius: 20px;
            border: 1px solid rgba(108,99,255,.08);
            box-shadow: 0 8px 25px rgba(54,42,91,.07);
            transition: transform .25s ease, box-shadow .25s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 14px 30px rgba(108,99,255,.13);
        }

        .mini-card {
            background: rgba(255,255,255,.72);
            border: 1px solid rgba(108,99,255,.08);
            border-radius: 18px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 6px 20px rgba(54,42,91,.05);
        }

        .item-card {
            background: rgba(255,255,255,.92);
            border-radius: 20px;
            padding: .85rem;
            border: 1px solid rgba(108,99,255,.07);
            box-shadow: 0 7px 22px rgba(54,42,91,.07);
            margin-bottom: 1rem;
            transition: transform .25s ease, box-shadow .25s ease;
            animation: cardIn .45s ease both;
        }
        .item-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 15px 32px rgba(108,99,255,.13);
        }
        .item-card img {
            border-radius: 15px;
        }

        @keyframes cardIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .outfit-panel {
            background: rgba(255,255,255,.94);
            border: 1px solid rgba(108,99,255,.10);
            border-radius: 26px;
            padding: 1.4rem 1.5rem;
            box-shadow: 0 15px 38px rgba(54,42,91,.10);
            animation: resultIn .65s cubic-bezier(.2,.8,.2,1) both;
        }

        @keyframes resultIn {
            from { opacity: 0; transform: translateY(18px) scale(.985); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        .section-kicker {
            color: #776be9;
            font-size: .78rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 800;
            margin-bottom: .15rem;
        }
        .style-note {
            background: linear-gradient(135deg, #f5f0ff, #fff2f8);
            border-radius: 17px;
            padding: .9rem 1rem;
            margin-top: .9rem;
            border: 1px solid rgba(108,99,255,.08);
        }

        div.stButton > button {
            border-radius: 13px;
            font-weight: 700;
            border: 0;
            transition: transform .18s ease, box-shadow .18s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(120deg, #665bea, #9b83ff);
            color: white;
            box-shadow: 0 8px 20px rgba(102,91,234,.20);
        }

        .stTextInput input, .stSelectbox div[data-baseweb="select"],
        .stFileUploader section {
            border-radius: 13px !important;
        }

        .footer-note {
            text-align: center;
            color: #8b8499;
            font-size: .78rem;
            margin-top: 2rem;
        }
    </style>

    <div class="orb one"></div>
    <div class="orb two"></div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>StyleSync ✨</h1>
        <p>Your wardrobe, styled beautifully — discover combinations that feel made for you.</p>
        <span class="hero-badge">♡ Smart matching · Personal style · Everyday confidence</span>
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

    col_a, col_b = st.columns(2)
    with col_a:
        gender = st.radio(
            "Who is this outfit for?",
            ["Female", "Male"],
            horizontal=True,
            key="gender_pick",
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
