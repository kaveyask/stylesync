"""
silhouette.py
Reference-style fashion mannequins for StyleSync.
Uses Pillow only; clothing colors remain dynamic.
"""
from PIL import Image, ImageDraw

SKIN_TONES = {
    "Light": "#F4D9C0", "Medium": "#E0AC81", "Tan": "#C68863",
    "Deep": "#8D5524", "Dark": "#4A2C1B",
}
COLOR_HEX = {
    "white":"#F5F5F5","black":"#252525","grey":"#A5A5AE","blue":"#4B82D9",
    "navy":"#213C67","red":"#D9535F","green":"#2F6D5B","yellow":"#E8B84B",
    "brown":"#87563A","beige":"#D8C3A5","pink":"#E78DB8","purple":"#8467D8",
    "orange":"#E78A45",
}

def _hex(color_name, fallback="#A5A5AE"):
    return COLOR_HEX.get((color_name or "").lower(), fallback)

def _mix(c, amount=.15, toward="white"):
    h=c.lstrip("#"); r,g,b=int(h[:2],16),int(h[2:4],16),int(h[4:6],16)
    t=255 if toward=="white" else 0
    return f"#{int(r+(t-r)*amount):02X}{int(g+(t-g)*amount):02X}{int(b+(t-b)*amount):02X}"

def draw_silhouette(top_color,bottom_color,shoes_color,skin_tone="Medium",
                    gender="Female",size=(360,680)):
    """Smooth full-body fashion mannequin inspired by the supplied reference."""
    sc=2; W,H=size[0]*sc,size[1]*sc
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    S=lambda v:int(v*sc); cx=W//2
    skin=SKIN_TONES.get(skin_tone,SKIN_TONES["Medium"])
    top=_hex(top_color,"#4B82D9"); bottom=_hex(bottom_color,"#D8C3A5")
    shoes=_hex(shoes_color,"#F5F5F5"); hair="#3A2925"; line=(72,53,86,42)
    female=str(gender).strip().lower()=="female"

    d.ellipse([S(70),S(645),S(290),S(670)],fill=(89,71,115,24))

    # Hair behind head
    if female:
        d.ellipse([cx-S(48),S(20),cx+S(48),S(126)],fill=hair)
        d.ellipse([cx-S(59),S(61),cx-S(18),S(205)],fill=hair)
        d.ellipse([cx+S(18),S(61),cx+S(59),S(205)],fill=hair)
    else:
        d.pieslice([cx-S(48),S(22),cx+S(48),S(116)],180,360,fill=hair)
        d.polygon([(cx-S(45),S(54)),(cx-S(31),S(28)),(cx+S(8),S(18)),
                   (cx+S(47),S(45)),(cx+S(40),S(68)),(cx-S(42),S(70))],fill=hair)

    # Face
    r=43 if female else 45
    d.ellipse([cx-S(r),S(77-r),cx+S(r),S(77+r)],fill=skin,outline=line,width=S(1))
    if female:
        d.pieslice([cx-S(43),S(24),cx+S(43),S(95)],180,345,fill=hair)
        d.ellipse([cx-S(49),S(62),cx-S(25),S(128)],fill=hair)
        d.ellipse([cx+S(25),S(62),cx+S(49),S(128)],fill=hair)
    else:
        d.pieslice([cx-S(43),S(28),cx+S(43),S(92)],180,350,fill=hair)
    eye=(61,49,54,190)
    d.ellipse([cx-S(16),S(74),cx-S(11),S(79)],fill=eye)
    d.ellipse([cx+S(11),S(74),cx+S(16),S(79)],fill=eye)
    d.arc([cx-S(10),S(82),cx+S(10),S(96)],15,165,fill=(120,73,77,120),width=S(1))

    # Neck
    d.rounded_rectangle([cx-S(15),S(112),cx+S(15),S(153)],radius=S(8),fill=skin)

    # Arms behind clothing
    if female:
        la=[(cx-S(65),S(157)),(cx-S(92),S(270)),(cx-S(78),S(275)),(cx-S(49),S(185))]
        ra=[(cx+S(65),S(157)),(cx+S(92),S(270)),(cx+S(78),S(275)),(cx+S(49),S(185))]
    else:
        la=[(cx-S(75),S(160)),(cx-S(108),S(292)),(cx-S(88),S(300)),(cx-S(55),S(192))]
        ra=[(cx+S(75),S(160)),(cx+S(108),S(292)),(cx+S(88),S(300)),(cx+S(55),S(192))]
    d.polygon(la,fill=skin,outline=line); d.polygon(ra,fill=skin,outline=line)
    d.ellipse([cx-S(92),S(263),cx-S(73),S(282)],fill=skin)
    d.ellipse([cx+S(73),S(263),cx+S(92),S(282)],fill=skin)

    # Top
    if female:
        tp=[(cx-S(55),S(146)),(cx+S(55),S(146)),(cx+S(72),S(252)),
            (cx+S(52),S(306)),(cx-S(52),S(306)),(cx-S(72),S(252))]
    else:
        tp=[(cx-S(76),S(146)),(cx+S(76),S(146)),(cx+S(92),S(282)),
            (cx+S(72),S(315)),(cx-S(72),S(315)),(cx-S(92),S(282))]
    d.polygon(tp,fill=top,outline=line)
    d.line([(cx-S(5),S(172)),(cx-S(8),S(275))],fill=_mix(top,.18),width=S(2))

    # Bottom
    if female:
        hp=[(cx-S(55),S(298)),(cx+S(55),S(298)),(cx+S(79),S(365)),
            (cx+S(63),S(487)),(cx-S(63),S(487)),(cx-S(79),S(365))]
    else:
        hp=[(cx-S(72),S(302)),(cx+S(72),S(302)),(cx+S(76),S(490)),(cx-S(76),S(490))]
    d.polygon(hp,fill=bottom,outline=line)
    d.line([(cx-S(54),S(310)),(cx+S(54),S(310))],fill=_mix(bottom,.20,"black"),width=S(2))
    d.line([(cx,S(325)),(cx,S(482))],fill=_mix(bottom,.14,"black"),width=S(2))

    # Legs
    d.polygon([(cx-S(63),S(475)),(cx-S(8),S(475)),(cx-S(10),S(612)),(cx-S(55),S(612))],
              fill=bottom,outline=line)
    d.polygon([(cx+S(8),S(475)),(cx+S(63),S(475)),(cx+S(55),S(612)),(cx+S(10),S(612))],
              fill=bottom,outline=line)

    # Sneakers
    shoe_hi=_mix(shoes,.10,"black")
    d.rounded_rectangle([cx-S(74),S(598),cx-S(3),S(630)],radius=S(12),fill=shoes,outline=line)
    d.rounded_rectangle([cx+S(3),S(598),cx+S(74),S(630)],radius=S(12),fill=shoes,outline=line)
    d.line([(cx-S(68),S(618)),(cx-S(10),S(618))],fill=shoe_hi,width=S(2))
    d.line([(cx+S(10),S(618)),(cx+S(68),S(618))],fill=shoe_hi,width=S(2))

    return img.resize(size,Image.Resampling.LANCZOS)
