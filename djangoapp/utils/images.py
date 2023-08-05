from pathlib import Path

from django.conf import settings
from PIL import Image, ExifTags


def get_exif_orientation(image_pillow):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image_pillow._getexif()
        if exif is not None:
            return exif[orientation]
    except (AttributeError, KeyError, IndexError):
        pass
    return None


def fix_orientation(image_pillow):
    orientation = get_exif_orientation(image_pillow)
    if orientation == 3:
        return image_pillow.rotate(180, expand=True)
    elif orientation == 6:
        return image_pillow.rotate(270, expand=True)
    elif orientation == 8:
        return image_pillow.rotate(90, expand=True)
    return image_pillow


def resize_image(image_django, new_width=800, optimize=True, quality=60):
    image_path = Path(settings.MEDIA_ROOT / image_django.name).resolve()
    image_pillow = Image.open(image_path)

    # Corrigir a orientação da imagem (se necessário)
    image_pillow = fix_orientation(image_pillow)

    original_width, original_height = image_pillow.size

    if original_width <= new_width:
        return image_pillow

    new_height = round(new_width * original_height / original_width)

    new_image = image_pillow.resize((new_width, new_height), Image.LANCZOS)

    new_image.save(
        image_path,
        optimize=optimize,
        quality=quality,
    )

    return new_image
