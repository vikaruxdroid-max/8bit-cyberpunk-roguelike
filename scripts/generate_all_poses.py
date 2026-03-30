"""Generate all character pose sprites sequentially via ComfyUI."""

import subprocess
import sys
import os
import time

SCRIPT = os.path.join(os.path.dirname(__file__), "generate_sprite.py")

BASE = (
    "cyberpunk female character, blue skin, pink spiky hair, "
    "magenta and cyan mechanical suit, neon armor, full body, anime style, "
    "glowing accents, pink and blue color palette, dark background, "
    "comic book shading, flat colors, bold outlines"
)

POSES = [
    ("idle",    f"idle standing relaxed pose, {BASE}"),
    ("attack1", f"lunging forward attack pose, {BASE}"),
    ("attack2", f"uppercut punch pose, {BASE}"),
    ("cast",    f"arms raised casting magic pose, {BASE}"),
    ("hit",     f"recoiling from hit pose, {BASE}"),
    ("death",   f"falling backward death pose, {BASE}"),
    ("victory", f"arms raised victory pose, {BASE}"),
    ("run",     f"running forward pose, {BASE}"),
]


def main():
    total = len(POSES)
    print(f"=== Generating {total} character poses ===\n")
    start_all = time.time()

    for i, (pose_name, prompt) in enumerate(POSES, 1):
        print(f"--- [{i}/{total}] Generating: {pose_name} ---")
        start = time.time()

        result = subprocess.run(
            [sys.executable, SCRIPT, pose_name, prompt],
            capture_output=False,
        )

        elapsed = time.time() - start

        if result.returncode != 0:
            print(f"!!! FAILED: {pose_name} (exit code {result.returncode}) !!!")
            print(f"    Continuing with next pose...\n")
        else:
            print(f"    {pose_name}.png saved successfully ({elapsed:.1f}s)\n")

    total_time = time.time() - start_all
    print(f"=== All poses complete in {total_time:.1f}s ===")


if __name__ == "__main__":
    main()
