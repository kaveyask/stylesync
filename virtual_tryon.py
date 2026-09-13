import os
import base64
from pathlib import Path
from typing import Optional, Sequence

from openai import OpenAI

AVATAR_DIR = Path("avatars")
RESULT_DIR = Path("tryon_results")
AVATAR_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)


def _client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to your environment or Streamlit secrets."
        )
    return OpenAI(api_key=key)


def _save_b64(response, output_path: Path) -> str:
    data = response.data[0].b64_json
    output_path.write_bytes(base64.b64decode(data))
    return str(output_path)


def _avatar_prompt(gender: str, skin_tone: str) -> str:
    return f"""
Create a single full-body, photorealistic 3D fashion-avatar reference image.

Gender presentation: {gender}.
Skin tone: {skin_tone}.

The avatar must:
- stand straight, facing the camera
- be visible from head to shoes
- have realistic human proportions
- have a natural face and realistic hair
- use a neutral, simple studio pose
- have both arms relaxed slightly away from the torso
- use a soft off-white studio background
- wear a plain fitted neutral base outfit so clothing can be replaced later
- look like a premium fashion-shopping application mannequin
- have realistic fabric, skin, hair and lighting
- NOT look like a cartoon, illustration, plastic doll, or line drawing

This is a reusable avatar reference. Keep the person centered and leave enough space
around the complete body for later virtual try-on edits.
""".strip()


def get_avatar_reference(gender: str, skin_tone: str) -> str:
    key = f"{gender.lower()}_{skin_tone.lower()}.png".replace(" ", "_")
    path = AVATAR_DIR / key

    if path.exists():
        return str(path)

    client = _client()
    response = client.images.generate(
        model="gpt-image-2",
        prompt=_avatar_prompt(gender, skin_tone),
        size="1024x1536",
        quality="medium",
    )
    return _save_b64(response, path)


def _tryon_prompt(
    gender: str,
    skin_tone: str,
    garment_labels: Sequence[str],
) -> str:
    labels = ", ".join(garment_labels)
    return f"""
Create a premium e-commerce virtual try-on image.

Use the FIRST image as the human avatar reference.
The remaining images are clothing/product references: {labels}.

Dress the exact same avatar in the supplied garments.

CRITICAL GARMENT-FIDELITY RULES:
1. Use the supplied garment images as the source of truth.
2. Preserve each garment's actual color, print, embroidery, buttons, seams,
   collar, sleeves, silhouette, material appearance and distinctive details.
3. Do NOT replace the supplied clothing with generic clothing.
4. Do NOT merely recolor the avatar's existing clothes.
5. Make the garments look physically worn on the body with natural folds,
   draping, shadows and perspective.
6. Fit the clothing to realistic human anatomy while preserving the original
   garment design.
7. If a supplied image is a one-piece dress/kurti, treat it as one-piece clothing
   and do not invent a separate top.
8. If a supplied item is footwear, put that exact style on the feet.
9. Keep the complete person visible from head to shoes.
10. Keep the face, hairstyle, skin tone and body proportions of the avatar reference.
11. Use realistic studio lighting and a clean warm-white/pale-lavender background.
12. Do not show the source product images as floating objects.
13. Do not add logos, text, accessories or extra garments that are not present in
    the references.
14. The result should look like a real 3D fashion-model render photographed for
    a premium shopping app, not an illustration.

Gender: {gender}
Skin tone: {skin_tone}
""".strip()


def create_virtual_tryon(
    garment_paths: Sequence[str],
    gender: str = "Female",
    skin_tone: str = "Medium",
    output_name: str = "tryon.png",
) -> str:
    garment_paths = [str(p) for p in garment_paths if p and Path(p).exists()]
    if not garment_paths:
        raise ValueError("No clothing images were found.")

    avatar_path = get_avatar_reference(gender, skin_tone)

    image_files = [open(avatar_path, "rb")]
    try:
        for path in garment_paths:
            image_files.append(open(path, "rb"))

        labels = []
        for path in garment_paths:
            name = Path(path).stem.replace("_", " ").replace("-", " ")
            labels.append(name)

        prompt = _tryon_prompt(gender, skin_tone, labels)
        client = _client()

        # GPT Image supports multiple reference images for an edit.
        response = client.images.edit(
            model="gpt-image-2",
            image=image_files,
            prompt=prompt,
            size="1024x1536",
            quality="medium",
        )

        return _save_b64(response, RESULT_DIR / output_name)
    finally:
        for f in image_files:
            f.close()
