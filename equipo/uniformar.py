#!/usr/bin/env python3
"""Unifica los retratos del equipo: recorta a la cara, recorta el fondo original
y compone a todos sobre el mismo fondo de marca.

Entrada:  equipo/_src/<slug>.(jpg|jpeg|png)
Salida:   equipo/<slug>.jpg  (cuadrado, fondo uniforme)

Necesita rembg (segmentación de personas). Si no lo tienes:

    python3 -m venv .venv && .venv/bin/pip install rembg onnxruntime pillow
    .venv/bin/python equipo/uniformar.py

La primera ejecución descarga el modelo u2net_human_seg (176 MB) a ~/.u2net.
"""
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

EQ = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(EQ, "_src")
OUT = 640                      # lado del JPG final
BG_TOP = (243, 238, 229)       # arena cálida, un punto por debajo del papel de marca
BG_BOTTOM = (228, 220, 207)
SLUGS = [
    "rogelio-alcaraz", "andrew-schwartz", "luis-paloma",
    "massimo-angelini", "paula-camprecios", "alvaro-entrena",
]


def backdrop(size):
    """Fondo de marca: degradado vertical suave + halo claro detrás de la cabeza."""
    w = h = size
    bg = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(
            int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)))
    halo = Image.new("L", (w, h), 0)
    ImageDraw.Draw(halo).ellipse(
        [w * 0.14, -h * 0.08, w * 0.86, h * 0.72], fill=90)
    halo = halo.filter(ImageFilter.GaussianBlur(size * 0.11))
    return Image.composite(Image.new("RGB", (w, h), (250, 247, 240)), bg, halo)


def clean_mask(rgb, alpha):
    """Quita el fleco del recorte y los restos de cielo que se cuelan junto al pelo."""
    px, ap = rgb.load(), alpha.load()
    w, h = alpha.size
    for y in range(int(h * 0.5)):
        for x in range(w):
            if ap[x, y] < 20:
                continue
            r, g, b = px[x, y]
            if b - r > 22 and b > 140 and b - g > 8:
                ap[x, y] = 0
    return alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))


def crop_box(mask, side_factor=2.75):
    """Cuadrado centrado en la cabeza, con aire arriba, a partir de la silueta.

    Devuelve la caja en coordenadas de la imagen; puede salirse, el lienzo se
    rellena luego con el fondo de marca. Así todas las cabezas salen del mismo
    tamaño aunque el original venga más o menos apretado.
    """
    w, h = mask.size
    px = mask.load()
    rows = []
    for y in range(h):
        n = sum(1 for x in range(0, w, 2) if px[x, y] > 128)
        rows.append(n * 2)
    thr = max(6, int(w * 0.012))
    top = next((y for y, n in enumerate(rows) if n > thr), 0)
    band = slice(top, min(h, top + int(h * 0.18)))
    head_w = max(rows[band] or [int(w * 0.3)])
    xs = [x for y in range(band.start, band.stop, 3)
          for x in range(0, w, 3) if px[x, y] > 128]
    cx = sum(xs) / len(xs) if xs else w / 2
    side = int(head_w * side_factor)
    left = int(cx - side / 2)
    t = int(top - side * 0.20)
    return (left, t, left + side, t + side)


def main():
    try:
        from rembg import new_session, remove
    except ImportError:
        sys.exit("Falta rembg. Mira la cabecera de este fichero.")
    session = new_session("u2net_human_seg")
    done = []
    for slug in SLUGS:
        srcs = [p for ext in ("jpg", "jpeg", "png", "webp", "JPG", "JPEG", "PNG")
                for p in glob.glob(os.path.join(SRC, f"{slug}.{ext}"))]
        if not srcs:
            print("sin origen:", slug)
            continue
        im = Image.open(srcs[0]).convert("RGB")
        cut = remove(im, session=session, post_process_mask=True)
        alpha = clean_mask(im, cut.getchannel("A"))
        box = crop_box(alpha)
        person = im.crop(box).resize((OUT, OUT), Image.LANCZOS)
        cut_a = alpha.crop(box).resize((OUT, OUT), Image.LANCZOS)

        # mismo tratamiento tonal para todos: un punto menos de saturación y luz cálida
        rgb = ImageEnhance.Color(person).enhance(0.86)
        rgb = ImageEnhance.Contrast(rgb).enhance(1.04)
        r, g, b = rgb.split()
        rgb = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.02))), g,
                                  b.point(lambda v: int(v * 0.985))))

        canvas = backdrop(OUT)
        canvas.paste(rgb, (0, 0), cut_a)
        canvas.save(os.path.join(EQ, f"{slug}.jpg"),
                    "JPEG", quality=88, optimize=True, progressive=True)
        done.append(slug)
    print("retratos uniformados:", len(done), done)


if __name__ == "__main__":
    main()
