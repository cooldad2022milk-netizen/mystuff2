"""Builds contact sheets from the showcase screenshots (run/screenshots) into build/sheets/."""
import glob
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "run", "screenshots")
OUT = os.path.join(ROOT, "build", "sheets")


def sheet(files, out, cols=4, crop=(290, 60, 990, 660), scale=0.5):
    if not files:
        return
    ims = [Image.open(f).crop(crop) for f in files]
    w, h = int(ims[0].width * scale), int(ims[0].height * scale)
    rows = (len(ims) + cols - 1) // cols
    s = Image.new("RGB", (w * cols, h * rows), (0, 0, 0))
    for i, im in enumerate(ims):
        s.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
    os.makedirs(OUT, exist_ok=True)
    s.save(os.path.join(OUT, out))


if __name__ == "__main__":
    for t in ("chainsaw", "crossbow", "flamethrower"):
        sheet(sorted(glob.glob(os.path.join(SHOTS, "csm_%s_0[0128]*.png" % t))), "%s_trigger.png" % t)
        sheet(sorted(glob.glob(os.path.join(SHOTS, "csm_%s_0[345]*.png" % t))), "%s_abilities.png" % t)
        sheet(sorted(glob.glob(os.path.join(SHOTS, "csm_%s_0[67]*.png" % t))), "%s_ui.png" % t, cols=2,
              crop=(0, 0, 1280, 720), scale=0.5)
    print("sheets in", OUT)
