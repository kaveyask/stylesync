"""
StyleSync - Wardrobe & Outfit Matching (no AI, no avatar, per-user accounts)

Run:
    pip install -r requirements.txt
    streamlit run app.py

Every wardrobe is private to the account that created it - the app opens
on a Login / Sign Up screen, and every database call is scoped to the
logged-in user's id. Outfits are shown as a flat-lay of your real garment
photos with a rule-based Match Score. Wardrobes, suggestions, and stats
are further split by Male/Female within each account. No AI/model calls
anywhere.
"""

import os
from pathlib import Path

import streamlit as st

import database as db
import outfit_logic as logic
import auth
from colors import COLOR_HEX, GENDERS


db.init_db()

st.set_page_config(
    page_title="StyleSync | Wardrobe & Outfit Matching",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# Purple theme + animations
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu, footer, header {visibility:hidden;}

        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

        @keyframes fadeInUp {
            from { opacity:0; transform: translateY(14px); }
            to   { opacity:1; transform: translateY(0); }
        }
        @keyframes floatSparkle {
            0%,100% { transform: translateY(0) rotate(0deg); }
            50%     { transform: translateY(-6px) rotate(6deg); }
        }
        @keyframes fillBar {
            from { width: 0%; }
        }
        @keyframes pulseGlow {
            0%,100% { box-shadow: 0 0 0 0 rgba(168,85,247,.35); }
            50%     { box-shadow: 0 0 0 10px rgba(168,85,247,0); }
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 4%, rgba(196,159,255,.35), transparent 30%),
                radial-gradient(circle at 92% 8%, rgba(255,159,231,.30), transparent 32%),
                linear-gradient(180deg,#f7f2ff 0%,#efe4ff 100%);
            font-family:'DM Sans',sans-serif;
            color:#3c2e57;
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
            background:linear-gradient(110deg,#7c3aed 0%,#a855f7 52%,#e879c9 100%);
            box-shadow:0 16px 40px rgba(124,58,237,.28);
            animation: fadeInUp .5s ease both;
        }

        .hero:after {
            content:"✦   ♡   ✦";
            position:absolute;
            right:28px;
            top:18px;
            color:#fff;
            opacity:.55;
            font-size:1.45rem;
            letter-spacing:10px;
            animation: floatSparkle 3.5s ease-in-out infinite;
        }

        .hero h1 {
            margin:0;
            color:#fff;
            font-family:'Playfair Display',serif;
            font-size:2.55rem;
        }

        .hero p {
            margin:.4rem 0 0;
            color:#f3e8ff;
            max-width:720px;
        }

        .badge {
            display:inline-block;
            margin-top:.75rem;
            padding:.4rem .75rem;
            border-radius:999px;
            background:rgba(255,255,255,.20);
            border:1px solid rgba(255,255,255,.35);
            color:#fff;
            font-size:.76rem;
            font-weight:700;
            backdrop-filter: blur(4px);
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
            transition: all .2s ease;
        }

        button[data-baseweb="tab"]:hover {
            background:rgba(168,85,247,.10) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background:linear-gradient(135deg,#a855f7,#e879c9) !important;
            color:#fff !important;
        }

        div[data-testid="stMetric"],
        .item-card,
        .outfit-card,
        .info-card,
        .fav-card,
        .auth-card {
            background:rgba(255,255,255,.90);
            border:1px solid rgba(126,94,206,.10);
            box-shadow:0 9px 28px rgba(83,63,111,.10);
            animation: fadeInUp .45s ease both;
        }

        div[data-testid="stMetric"] {
            border-radius:18px;
            padding:1rem;
            transition: transform .2s ease;
        }
        div[data-testid="stMetric"]:hover { transform: translateY(-3px); }

        .item-card, .fav-card {
            border-radius:20px;
            padding:.8rem;
            margin-bottom:1rem;
            transition: transform .25s ease, box-shadow .25s ease;
        }
        .item-card:hover, .fav-card:hover {
            transform: translateY(-4px);
            box-shadow:0 16px 32px rgba(124,58,237,.18);
        }

        .outfit-card {
            border-radius:26px;
            padding:1.3rem;
        }

        .info-card, .auth-card {
            border-radius:18px;
            padding:1.4rem 1.5rem;
            margin:.5rem 0;
        }

        .kicker {
            color:#8668ce;
            font-size:.72rem;
            text-transform:uppercase;
            letter-spacing:1.5px;
            font-weight:800;
        }

        .flatlay-item {
            border-radius:18px;
            overflow:hidden;
            transition: transform .3s ease;
            box-shadow:0 8px 20px rgba(83,63,111,.14);
        }
        .flatlay-item:hover { transform: rotate(0deg) scale(1.03) !important; }

        .score-wrap {
            margin:.4rem 0 1rem;
        }
        .score-track {
            width:100%;
            height:16px;
            border-radius:999px;
            background:rgba(168,85,247,.14);
            overflow:hidden;
        }
        .score-fill {
            height:100%;
            border-radius:999px;
            background:linear-gradient(90deg,#a855f7,#ec4899);
            animation: fillBar 1s ease-out both;
        }
        .score-label {
            font-weight:800;
            color:#7c3aed;
            font-size:1.05rem;
        }

        .gender-chip {
            display:inline-block;
            padding:.2rem .6rem;
            border-radius:999px;
            font-size:.7rem;
            font-weight:800;
            letter-spacing:.4px;
        }
        .chip-male   { background:#e0e7ff; color:#4338ca; }
        .chip-female { background:#fce7f3; color:#be185d; }
        .chip-unisex { background:#ede9fe; color:#6d28d9; }

        .heat-grid {
            display:grid;
            grid-template-columns: repeat(12, 1fr);
            gap:4px;
            margin-top:.4rem;
        }
        .heat-cell {
            width:100%;
            padding-top:100%;
            border-radius:4px;
            position:relative;
            transition: transform .15s ease;
        }
        .heat-cell:hover { transform: scale(1.25); }

        .stButton > button {
            border-radius:13px;
            font-weight:700;
            transition: transform .15s ease, box-shadow .15s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
        }

        .stButton > button[kind="primary"] {
            background:linear-gradient(120deg,#7c3aed,#e879c9);
            color:#fff;
            border:0;
            box-shadow:0 8px 20px rgba(145,92,212,.28);
            animation: pulseGlow 2.5s ease-in-out infinite;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Auth gate — nothing below this runs until someone is logged in
# ------------------------------------------------------------------
def show_login_signup():
    st.markdown(
        """
        <div class="hero">
            <h1>StyleSync ✨</h1>
            <p>Your private wardrobe stylist. Sign in to see only your own clothes.</p>
            <span class="badge">♡ Your wardrobe is private to your account</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab = st.tabs(["🔑 Log In", "🆕 Sign Up"])

    with login_tab:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
                autocomplete="current-password"
            )
            submitted = st.form_submit_button("Log In", type="primary")

            if submitted:
                user = db.get_user_by_email(email)
                if user and auth.verify_password(password, user["salt"], user["password_hash"]):
                    st.session_state["user"] = {"id": user["id"], "email": user["email"]}
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")
        st.markdown("</div>", unsafe_allow_html=True)

    with signup_tab:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input(
                "Create Password",
                type="password",
                key="signup_password",
                autocomplete="new-password"
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="signup_confirm",
                autocomplete="new-password"
            )
            submitted = st.form_submit_button("Create Account", type="primary")

            if submitted:
                if not auth.is_valid_email(new_email):
                    st.error("Please enter a valid email address.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_password != confirm_password:
                    st.error("Passwords don't match.")
                else:
                    password_hash, salt = auth.hash_password(new_password)
                    user_id = db.create_user(new_email, password_hash, salt)
                    if user_id is None:
                        st.error("An account with that email already exists — try logging in instead.")
                    else:
                        st.session_state["user"] = {"id": user_id, "email": new_email.strip().lower()}
                        st.success("Account created! ✨")
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


if "user" not in st.session_state:
    show_login_signup()
    st.stop()

current_user = st.session_state["user"]
UID = current_user["id"]

UPLOAD_DIR = Path("uploads") / str(UID)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

top_l, top_r = st.columns([5, 1])
with top_r:
    st.markdown(f"<div style='padding-top:.6rem;font-size:.85rem;color:#7c3aed;'>👤 {current_user['email']}</div>", unsafe_allow_html=True)
    if st.button("Log Out"):
        del st.session_state["user"]
        st.rerun()

st.markdown(
    """
    <div class="hero">
        <h1>StyleSync ✨</h1>
        <p>
            Your wardrobe stylist — real garment photos, rule-based outfit
            matching, and a Match Score. No AI, no avatar, just your clothes.
        </p>
        <span class="badge">♡ Private wardrobe · Gender-separated · Match Score · Favorites</span>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_dash, tab_add, tab_wardrobe, tab_suggest, tab_fav = st.tabs(
    ["🏠 Dashboard", "➕ Add Item", "👚 My Wardrobe", "✨ Style Me", "💖 Favorites"]
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def gender_chip(gender):
    cls = {"Male": "chip-male", "Female": "chip-female"}.get(gender, "chip-unisex")
    return f"<span class='gender-chip {cls}'>{gender}</span>"


def score_meter(score, label="Match Score"):
    score = 0 if score is None else score
    st.markdown(
        f"""
        <div class="score-wrap">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.3rem;">
                <span class="kicker">{label}</span>
                <span class="score-label">{score}%</span>
            </div>
            <div class="score-track">
                <div class="score-fill" style="width:{score}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def heat_color(score):
    if score is None:
        return "rgba(124,58,237,.08)"
    if score >= 90:
        return "#7c3aed"
    if score >= 75:
        return "#a855f7"
    if score >= 60:
        return "#c98af0"
    return "#e6d3fb"


def render_calendar_heatmap(history):
    parts = []
    for d, s in history:
        tooltip = f"{d.isoformat()}: {s}% match" if s is not None else f"{d.isoformat()}: not worn"
        parts.append(
            f"<div class='heat-cell' title='{tooltip}' style='background:{heat_color(s)};'></div>"
        )
    cells = "".join(parts)
    st.markdown(f"<div class='heat-grid'>{cells}</div>", unsafe_allow_html=True)
    st.caption("Each square is a day (last 12 weeks) · darker = higher Match Score that day")


def render_flatlay(top, bottom, shoe):
    cols = st.columns(3)
    rotations = [-3, 0, 3]
    labels = ["👕 Top", "👖 Bottom", "👟 Shoes"]
    for col, item, rot, label in zip(cols, [top, bottom, shoe], rotations, labels):
        with col:
            st.markdown(f"<div class='kicker'>{label}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='flatlay-item' style='transform:rotate({rot}deg);'>",
                unsafe_allow_html=True,
            )
            if item.get("image_path") and os.path.exists(item["image_path"]):
                st.image(item["image_path"], use_container_width=True)
            else:
                st.warning("No image")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"**{item['name']}**")
            st.caption(f"{item['color'].title()}")


def outfit_ids(outfit):
    t, b, s = outfit
    return t["id"], b["id"], s["id"]


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
with tab_dash:
    st.markdown("<div class='kicker'>Overview</div>", unsafe_allow_html=True)
    st.subheader("Dashboard")

    dash_male, dash_female = st.tabs(["🧑 Male", "👩 Female"])

    for dash_tab, gender in [(dash_male, "Male"), (dash_female, "Female")]:
        with dash_tab:
            total, week, last, avg_score = db.get_stats(UID, gender)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Wardrobe pieces", total)
            c2.metric("Looks worn this week", week)
            c3.metric("Avg. Match Score", f"{avg_score}%" if avg_score is not None else "—")
            c4.metric("Last look", str(last) if last else "Not yet")

            st.markdown("<div class='kicker' style='margin-top:1rem;'>Wear history</div>", unsafe_allow_html=True)
            history = db.get_wear_history(UID, gender, weeks=12)
            render_calendar_heatmap(history)

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
            occasion = st.selectbox("Occasion", ["casual", "formal", "sport", "party"])
            gender = st.selectbox("Gender", GENDERS, index=2)
            photo = st.file_uploader(
                "Upload the actual clothing photo",
                type=["jpg", "jpeg", "png", "webp"],
            )

        submitted = st.form_submit_button("＋ Add to Wardrobe", type="primary")

        if submitted:
            if not name.strip():
                st.error("Please give the item a name.")
            elif photo is None:
                st.error("Upload a photo of the actual garment.")
            else:
                safe_name = f"{st.session_state.get('upload_counter', 0)}_{photo.name}"
                st.session_state["upload_counter"] = st.session_state.get("upload_counter", 0) + 1

                image_path = UPLOAD_DIR / safe_name
                image_path.write_bytes(photo.getbuffer())

                db.add_item(UID, type_, name.strip(), color, occasion, gender, str(image_path))
                st.success(f"Added **{name}** to your {gender} wardrobe. ✨")
                st.rerun()

# ------------------------------------------------------------------
# My Wardrobe
# ------------------------------------------------------------------
with tab_wardrobe:
    st.markdown("<div class='kicker'>Everything you own</div>", unsafe_allow_html=True)
    st.subheader("My Wardrobe")

    filt1, filt2 = st.columns(2)
    with filt1:
        filter_type = st.selectbox("Filter by type", ["all", "top", "bottom", "shoes"])
    with filt2:
        filter_gender = st.selectbox("Filter by gender", ["all"] + GENDERS)

    items = db.get_items(UID)
    shown = items
    if filter_type != "all":
        shown = [i for i in shown if i["type"] == filter_type]
    if filter_gender != "all":
        shown = [i for i in shown if i["gender"] == filter_gender]

    if not shown:
        st.info("No items yet — add clothing photos in **Add Item**.")
    else:
        cols = st.columns(4)
        for i, item in enumerate(shown):
            with cols[i % 4]:
                st.markdown("<div class='item-card'>", unsafe_allow_html=True)

                if item["image_path"] and os.path.exists(item["image_path"]):
                    st.image(item["image_path"], use_container_width=True)
                else:
                    st.warning("No garment image")

                st.markdown(f"**{item['name']}** {gender_chip(item['gender'])}", unsafe_allow_html=True)
                st.caption(f"{item['color'].title()} · {item['type'].title()} · {item['occasion'].title()}")

                if st.button("🗑 Delete", key=f"del_{item['id']}"):
                    db.delete_item(UID, item["id"])
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Style Me
# ------------------------------------------------------------------
with tab_suggest:
    st.markdown("<div class='kicker'>Outfit suggestions</div>", unsafe_allow_html=True)
    st.subheader("Get a matched outfit from your real clothes")

    col_a, col_b = st.columns(2)
    with col_a:
        gender_pick = st.radio("Wardrobe", ["Female", "Male"], horizontal=True, key="gender_pick")
    with col_b:
        occasion_filter = st.selectbox(
            "Occasion", ["casual", "formal", "sport", "party"], key="occasion_pick"
        )

    st.markdown(
        """
        <div class="info-card">
            <b>How it works:</b> we pick a top, bottom and pair of shoes from your
            <b>own uploaded photos</b> that pass our color-compatibility rules, then
            score the combo with a deterministic Match Score. Nothing here calls an AI model.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("✨ Get My Look", type="primary"):
        tops = [i for i in db.get_items(UID, "top", gender_pick) if i["occasion"] == occasion_filter]
        bottoms = [i for i in db.get_items(UID, "bottom", gender_pick) if i["occasion"] == occasion_filter]
        shoes = [i for i in db.get_items(UID, "shoes", gender_pick) if i["occasion"] == occasion_filter]

        tops = [i for i in tops if i.get("image_path") and os.path.exists(i["image_path"])]
        bottoms = [i for i in bottoms if i.get("image_path") and os.path.exists(i["image_path"])]
        shoes = [i for i in shoes if i.get("image_path") and os.path.exists(i["image_path"])]

        if not (tops and bottoms and shoes):
            st.warning(
                f"Add at least one photo-based top, bottom and shoe for your "
                f"{gender_pick} / {occasion_filter} wardrobe."
            )
            st.session_state.pop("outfit", None)
        else:
            valid = logic.generate_valid_outfits(tops, bottoms, shoes)
            if not valid:
                st.warning("No compatible outfit was found by your existing wardrobe rules.")
                st.session_state.pop("outfit", None)
            else:
                recent = db.get_recent_outfit_ids(UID, gender_pick)
                chosen = logic.pick_outfit(valid, recent)
                score = logic.calculate_match_score(*chosen, recent_ids=recent)

                st.session_state["outfit"] = chosen
                st.session_state["outfit_gender"] = gender_pick
                st.session_state["outfit_score"] = score

    if st.session_state.get("outfit") and st.session_state.get("outfit_gender") == gender_pick:
        top, bottom, shoe = st.session_state["outfit"]
        score = st.session_state["outfit_score"]

        st.markdown("<div class='outfit-card'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='kicker'>Today's match · {gender_chip(gender_pick)}</div>",
            unsafe_allow_html=True,
        )
        score_meter(score)
        render_flatlay(top, bottom, shoe)

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("✓ Wear This Today", type="primary"):
                t, b, s = outfit_ids(st.session_state["outfit"])
                db.log_outfit(UID, t, b, s, gender_pick, score)
                st.success("Look logged! ✨")
                st.session_state.pop("outfit", None)
                st.rerun()
        with b2:
            if st.button("♡ Save to Favorites"):
                t, b, s = outfit_ids(st.session_state["outfit"])
                db.add_favorite(UID, t, b, s, gender_pick, score)
                st.success("Saved to Favorites! 💖")
        with b3:
            if st.button("🔄 Try Another"):
                recent = db.get_recent_outfit_ids(UID, gender_pick)
                tops = [i for i in db.get_items(UID, "top", gender_pick) if i["occasion"] == occasion_filter and i.get("image_path") and os.path.exists(i["image_path"])]
                bottoms = [i for i in db.get_items(UID, "bottom", gender_pick) if i["occasion"] == occasion_filter and i.get("image_path") and os.path.exists(i["image_path"])]
                shoes = [i for i in db.get_items(UID, "shoes", gender_pick) if i["occasion"] == occasion_filter and i.get("image_path") and os.path.exists(i["image_path"])]
                valid = logic.generate_valid_outfits(tops, bottoms, shoes)
                if valid:
                    chosen = logic.pick_outfit(valid, recent)
                    st.session_state["outfit"] = chosen
                    st.session_state["outfit_score"] = logic.calculate_match_score(*chosen, recent_ids=recent)
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Favorites
# ------------------------------------------------------------------
with tab_fav:
    st.markdown("<div class='kicker'>Saved looks</div>", unsafe_allow_html=True)
    st.subheader("Favorites")

    fav_gender = st.radio("Wardrobe", ["Female", "Male"], horizontal=True, key="fav_gender_pick")
    favorites = db.get_favorites(UID, fav_gender)

    if not favorites:
        st.info("No favorites saved yet — save a look from **Style Me**.")
    else:
        for fav in favorites:
            top = db.get_item_by_id(UID, fav["top_id"])
            bottom = db.get_item_by_id(UID, fav["bottom_id"])
            shoe = db.get_item_by_id(UID, fav["shoes_id"])

            if not (top and bottom and shoe):
                continue  # one of the items was deleted since

            st.markdown("<div class='fav-card'>", unsafe_allow_html=True)
            score_meter(fav["match_score"], label="Match Score")
            render_flatlay(top, bottom, shoe)

            fb1, fb2 = st.columns(2)
            with fb1:
                if st.button("✓ Wear This Today", key=f"wear_fav_{fav['id']}", type="primary"):
                    db.log_outfit(UID, top["id"], bottom["id"], shoe["id"], fav_gender, fav["match_score"])
                    st.success("Look logged! ✨")
                    st.rerun()
            with fb2:
                if st.button("🗑 Remove", key=f"del_fav_{fav['id']}"):
                    db.delete_favorite(UID, fav["id"])
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center;color:#9a8fa8;margin-top:1.5rem;font-size:.76rem'>"
    "Made with ♡ for easier everyday styling · StyleSync"
    "</div>",
    unsafe_allow_html=True,
)
