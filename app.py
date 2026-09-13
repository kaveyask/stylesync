"""
StyleSync - AI Virtual Try-On version

Run:
    pip install streamlit openai pillow
    streamlit run app.py

Set your OpenAI API key before running:
    Windows PowerShell:
        $env:OPENAI_API_KEY="your_key"

    macOS/Linux:
        export OPENAI_API_KEY="your_key"

The existing database.py and outfit_logic.py are kept as your project's
database/matching layer. The major change is that Style Me now sends the
actual uploaded garment images to the AI virtual try-on renderer instead of
painting only their colors onto a mannequin.
"""

import os
from pathlib import Path

import streamlit as st

import database as db
import outfit_logic as logic
from silhouette import SKIN_TONES, COLOR_HEX
from virtual_tryon import create_virtual_tryon


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

db.init_db()

st.set_page_config(
    page_title="StyleSync | AI Virtual Try-On",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# Reference-inspired UI
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu, footer, header {visibility:hidden;}

        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

        .stApp {
            background:
                radial-gradient(circle at 8% 4%, rgba(235,216,255,.82), transparent 25%),
                radial-gradient(circle at 92% 8%, rgba(255,215,241,.72), transparent 27%),
                linear-gradient(180deg,#fcf8ff 0%,#f4edff 100%);
            font-family:'DM Sans',sans-serif;
            color:#443657;
        }

        .block-container {
            max-width:1220px;
            padding-top:1.1rem;
            padding-bottom:3rem;
        }

        .hero {
            position:relative;
            overflow:hidden;
            padding:1.65rem 2rem;
            border-radius:26px;
            margin-bottom:1.1rem;
            background:linear-gradient(110deg,#eee5ff 0%,#faefff 52%,#ffeaf7 100%);
            border:1px solid rgba(125,94,206,.10);
            box-shadow:0 14px 38px rgba(105,78,145,.10);
        }

        .hero:after {
            content:"✦   ♡   ✦";
            position:absolute;
            right:28px;
            top:18px;
            color:#a58bdb;
            opacity:.42;
            font-size:1.45rem;
            letter-spacing:10px;
        }

        .hero h1 {
            margin:0;
            color:#4c376e;
            font-family:'Playfair Display',serif;
            font-size:2.55rem;
        }

        .hero p {
            margin:.4rem 0 0;
            color:#796a8b;
            max-width:720px;
        }

        .badge {
            display:inline-block;
            margin-top:.75rem;
            padding:.4rem .75rem;
            border-radius:999px;
            background:rgba(255,255,255,.72);
            border:1px solid rgba(126,94,206,.12);
            color:#7556b5;
            font-size:.76rem;
            font-weight:700;
        }

        div[data-baseweb="tab-list"] {
            gap:7px;
            padding:6px;
            border-radius:16px;
            background:rgba(255,255,255,.55);
            border:1px solid rgba(126,94,206,.08);
        }

        button[data-baseweb="tab"] {
            border-radius:12px !important;
            font-weight:700 !important;
            color:#756a83 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background:linear-gradient(135deg,#eee5ff,#ffe9f6) !important;
            color:#6847b5 !important;
        }

        div[data-testid="stMetric"],
        .item-card,
        .tryon-card,
        .info-card {
            background:rgba(255,255,255,.88);
            border:1px solid rgba(126,94,206,.09);
            box-shadow:0 9px 28px rgba(83,63,111,.08);
        }

        div[data-testid="stMetric"] {
            border-radius:18px;
            padding:1rem;
        }

        .item-card {
            border-radius:20px;
            padding:.8rem;
            margin-bottom:1rem;
        }

        .tryon-card {
            border-radius:26px;
            padding:1.2rem;
        }

        .info-card {
            border-radius:18px;
            padding:1rem 1.1rem;
            margin:.5rem 0;
        }

        .kicker {
            color:#8668ce;
            font-size:.72rem;
            text-transform:uppercase;
            letter-spacing:1.5px;
            font-weight:800;
        }

        .stButton > button {
            border-radius:13px;
            font-weight:700;
        }

        .stButton > button[kind="primary"] {
            background:linear-gradient(120deg,#9c69ed,#e287c4);
            color:#fff;
            border:0;
            box-shadow:0 8px 20px rgba(145,92,212,.20);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>StyleSync ✨</h1>
        <p>
            Your AI wardrobe stylist — see your actual clothes worn on a
            realistic 3D fashion avatar.
        </p>
        <span class="badge">♡ Real garments · AI virtual try-on · Personal styling</span>
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

# ------------------------------------------------------------------
# Add Item
# ------------------------------------------------------------------
with tab_add:
    st.markdown("<div class='kicker'>Build your closet</div>", unsafe_allow_html=True)
    st.subheader("Add a clothing item")

    with st.form("add_item_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            type_ = st.selectbox("Type", ["top", "bottom", "shoes"])
            name = st.text_input("Name", placeholder="e.g. Brown Casual Shirt")
            color = st.selectbox("Color", sorted(COLOR_HEX.keys()))

        with col2:
            occasion = st.selectbox(
                "Occasion", ["casual", "formal", "sport", "party"]
            )
            photo = st.file_uploader(
                "Upload the actual clothing photo",
                type=["jpg", "jpeg", "png", "webp"],
            )

        submitted = st.form_submit_button(
            "＋ Add to Wardrobe",
            type="primary",
        )

        if submitted:
            if not name.strip():
                st.error("Please give the item a name.")
            elif photo is None:
                st.error("Upload the actual clothing photo so AI can use the garment.")
            else:
                # Avoid collisions when two uploaded files have the same name.
                safe_name = f"{st.session_state.get('upload_counter', 0)}_{photo.name}"
                st.session_state["upload_counter"] = (
                    st.session_state.get("upload_counter", 0) + 1
                )

                image_path = UPLOAD_DIR / safe_name
                image_path.write_bytes(photo.getbuffer())

                db.add_item(
                    type_,
                    name.strip(),
                    color,
                    occasion,
                    str(image_path),
                )
                st.success(f"Added **{name}** with its real garment image. ✨")
                st.rerun()

# ------------------------------------------------------------------
# My Wardrobe
# ------------------------------------------------------------------
with tab_wardrobe:
    st.markdown("<div class='kicker'>Everything you own</div>", unsafe_allow_html=True)
    st.subheader("My Wardrobe")

    items = db.get_items()

    if not items:
        st.info("No items yet — add clothing photos in **Add Item**.")
    else:
        filter_type = st.selectbox(
            "Filter by type",
            ["all", "top", "bottom", "shoes"],
        )

        shown = (
            items
            if filter_type == "all"
            else [i for i in items if i["type"] == filter_type]
        )

        cols = st.columns(4)

        for i, item in enumerate(shown):
            with cols[i % 4]:
                st.markdown("<div class='item-card'>", unsafe_allow_html=True)

                if item["image_path"] and os.path.exists(item["image_path"]):
                    st.image(item["image_path"], use_container_width=True)
                else:
                    st.warning("No garment image")

                st.markdown(f"**{item['name']}**")
                st.caption(
                    f"{item['color'].title()} · "
                    f"{item['type'].title()} · "
                    f"{item['occasion'].title()}"
                )

                if st.button("🗑 Delete", key=f"del_{item['id']}"):
                    db.delete_item(item["id"])
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Style Me — AI Virtual Try-On
# ------------------------------------------------------------------
with tab_suggest:
    st.markdown("<div class='kicker'>AI virtual try-on</div>", unsafe_allow_html=True)
    st.subheader("See your actual outfit on a realistic avatar")

    col_a, col_b = st.columns(2)

    with col_a:
        gender = st.radio(
            "Avatar",
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

        st.markdown(
            """
            <div class="info-card">
                <b>Important:</b> StyleSync sends the actual uploaded clothing
                photos to the virtual try-on model. It does not simply recolor
                a mannequin.
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("✨ Create AI try-on", type="primary"):
        tops = [
            i for i in db.get_items("top")
            if i["occasion"] == occasion_filter
            and i.get("image_path")
            and os.path.exists(i["image_path"])
        ]

        bottoms = [
            i for i in db.get_items("bottom")
            if i["occasion"] == occasion_filter
            and i.get("image_path")
            and os.path.exists(i["image_path"])
        ]

        shoes = [
            i for i in db.get_items("shoes")
            if i["occasion"] == occasion_filter
            and i.get("image_path")
            and os.path.exists(i["image_path"])
        ]

        if not (tops and bottoms and shoes):
            st.warning(
                f"Add at least one photo-based top, bottom and shoe for "
                f"the {occasion_filter} occasion."
            )
            st.session_state.pop("outfit", None)
        else:
            valid = logic.generate_valid_outfits(tops, bottoms, shoes)

            if not valid:
                st.warning(
                    "No compatible outfit was found by your existing wardrobe rules."
                )
                st.session_state.pop("outfit", None)
            else:
                recent = db.get_recent_outfit_ids()
                chosen = logic.pick_outfit(valid, recent)

                st.session_state["outfit"] = chosen
                st.session_state["skin_tone"] = skin_tone
                st.session_state["gender"] = gender

                top, bottom, shoe = chosen

                with st.spinner(
                    "Creating your realistic virtual try-on from the actual garment photos..."
                ):
                    try:
                        result = create_virtual_tryon(
                            garment_paths=[
                                top["image_path"],
                                bottom["image_path"],
                                shoe["image_path"],
                            ],
                            gender=gender,
                            skin_tone=skin_tone,
                            output_name="latest_tryon.png",
                        )

                        st.session_state["tryon_result"] = result
                    except Exception as e:
                        st.error(
                            "AI try-on could not be generated. "
                            "Check your OPENAI_API_KEY and internet connection."
                        )
                        st.exception(e)

    if st.session_state.get("tryon_result") and st.session_state.get("outfit"):
        top, bottom, shoe = st.session_state["outfit"]
        result = st.session_state["tryon_result"]

        st.markdown("<div class='tryon-card'>", unsafe_allow_html=True)

        left, right = st.columns([1.05, 1])

        with left:
            st.image(
                result,
                caption="AI virtual try-on — your actual garment references",
                use_container_width=True,
            )

        with right:
            st.markdown("<div class='kicker'>Your curated look</div>", unsafe_allow_html=True)
            st.markdown("### Today's match")

            st.markdown(f"👕 **Top:** {top['name']}")
            st.image(top["image_path"], width=140)

            st.markdown(f"👖 **Bottom:** {bottom['name']}")
            st.image(bottom["image_path"], width=140)

            st.markdown(f"👟 **Shoes:** {shoe['name']}")
            st.image(shoe["image_path"], width=140)

            if st.button("♡ Wear this today", type="primary"):
                db.log_outfit(top["id"], bottom["id"], shoe["id"])
                st.success("Look logged! ✨")
                st.session_state.pop("outfit", None)
                st.session_state.pop("tryon_result", None)
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center;color:#9a8fa8;margin-top:1.5rem;font-size:.76rem'>"
    "Made with ♡ for easier everyday styling · StyleSync"
    "</div>",
    unsafe_allow_html=True,
)
