#!/usr/bin/env python3
"""
Submit ComfyUI enemy sprite workflows and save outputs to C:/game/assets/enemies/
"""

import json
import time
import shutil
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: 'requests' not installed. Run: pip install requests")

# ── Config ─────────────────────────────────────────────────────────────────────
COMFY_URL        = "http://127.0.0.1:8188"
WORKFLOW_DIR     = Path("C:/game/comfy_workflows")
OUTPUT_DIR       = Path("C:/game/assets/enemies")
COMFY_OUTPUT_DIR = Path("C:/ComfyUI/output")   # overridden below via /system_stats if possible
POLL_INTERVAL    = 2   # seconds between history polls
POLL_TIMEOUT     = 300 # max seconds to wait per job

# Map JSON filename → desired output filename
ENEMY_MAP = {
    "enemy_glitch_slime.json": "glitch_slime.png",
    "enemy_neon_wraith.json":  "neon_wraith.png",
    "enemy_cyber_beast.json":  "cyber_beast.png",
    "enemy_rogue_drone.json":  "rogue_drone.png",
    "enemy_data_golem.json":   "data_golem.png",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def check_comfy_alive():
    global COMFY_OUTPUT_DIR
    try:
        r = requests.get(f"{COMFY_URL}/system_stats", timeout=5)
        r.raise_for_status()
        print(f"[OK] ComfyUI is reachable at {COMFY_URL}")
    except requests.exceptions.ConnectionError:
        sys.exit(f"[FATAL] Cannot reach ComfyUI at {COMFY_URL}. Is it running?")
    except requests.exceptions.HTTPError as e:
        sys.exit(f"[FATAL] ComfyUI returned error: {e}")

    # Try to discover the output directory from ComfyUI's settings
    try:
        r2 = requests.get(f"{COMFY_URL}/object_info", timeout=5)
        # Fall back: probe common locations
        candidates = [
            Path("C:/ComfyUI/output"),
            Path("C:/ComfyUI_windows_portable/ComfyUI/output"),
            Path.home() / "ComfyUI" / "output",
        ]
        for c in candidates:
            if c.exists():
                COMFY_OUTPUT_DIR = c
                print(f"[OK] ComfyUI output dir: {COMFY_OUTPUT_DIR}")
                break
        else:
            print(f"[WARN] Could not auto-detect ComfyUI output dir; using {COMFY_OUTPUT_DIR}")
    except Exception:
        pass


def submit_workflow(workflow: dict) -> str | None:
    """POST workflow to /prompt, return prompt_id or None on failure."""
    payload = {"prompt": workflow}
    try:
        r = requests.post(f"{COMFY_URL}/prompt", json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            print(f"  [ERROR] ComfyUI validation error: {data['error']}")
            if "node_errors" in data:
                for node_id, err in data["node_errors"].items():
                    print(f"         Node {node_id}: {err}")
            return None
        prompt_id = data.get("prompt_id")
        print(f"  [SUBMITTED] prompt_id = {prompt_id}")
        return prompt_id
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Failed to submit workflow: {e}")
        return None


def poll_until_done(prompt_id: str) -> dict | None:
    """Poll /history/{prompt_id} until job finishes. Returns output dict or None."""
    deadline = time.time() + POLL_TIMEOUT
    dots = 0
    while time.time() < deadline:
        try:
            r = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=10)
            r.raise_for_status()
            history = r.json()
        except requests.exceptions.RequestException as e:
            print(f"\n  [WARN] Poll request failed: {e}. Retrying...")
            time.sleep(POLL_INTERVAL)
            continue

        if prompt_id in history:
            job = history[prompt_id]
            status = job.get("status", {})
            # Check for failure
            if status.get("status_str") == "error" or status.get("completed") is False:
                messages = status.get("messages", [])
                print(f"\n  [ERROR] Job failed. Messages: {messages}")
                return None
            # Check for completion — outputs key is populated when done
            outputs = job.get("outputs", {})
            if outputs:
                print(f" done.")
                return outputs

        # Still running
        dots += 1
        if dots % 5 == 1:
            elapsed = int(time.time() - (deadline - POLL_TIMEOUT))
            print(f"  [WAITING] {elapsed}s elapsed...", end="\r", flush=True)
        time.sleep(POLL_INTERVAL)

    print(f"\n  [ERROR] Timed out after {POLL_TIMEOUT}s waiting for job {prompt_id}")
    return None


def find_output_image(outputs: dict) -> Path | None:
    """
    Extract the first image filename from the ComfyUI outputs dict.
    outputs looks like: {"8": {"images": [{"filename": "...", "subfolder": "", "type": "output"}]}}
    """
    for node_id, node_output in outputs.items():
        images = node_output.get("images", [])
        for img in images:
            if img.get("type") == "output":
                subfolder = img.get("subfolder", "")
                filename  = img.get("filename", "")
                if filename:
                    candidate = COMFY_OUTPUT_DIR / subfolder / filename
                    return candidate
    return None


def copy_image(src: Path, dest_name: str) -> bool:
    """Copy src image to OUTPUT_DIR with dest_name. Returns True on success."""
    if not src.exists():
        # Try a filename-only search in COMFY_OUTPUT_DIR in case subfolder is wrong
        alt = COMFY_OUTPUT_DIR / src.name
        if alt.exists():
            src = alt
        else:
            print(f"  [WARN] Output image not found at {src} (or {alt}). Skipping copy.")
            return False
    dest = OUTPUT_DIR / dest_name
    shutil.copy2(src, dest)
    print(f"  [SAVED] {src.name}  ->  {dest}")
    return True


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  ComfyUI Enemy Sprite Generator")
    print("=" * 60)

    check_comfy_alive()
    print()

    results = {}   # dest_name → True/False

    for json_file, dest_name in ENEMY_MAP.items():
        workflow_path = WORKFLOW_DIR / json_file
        enemy_label   = dest_name.replace(".png", "").replace("_", " ").upper()

        print(f"-- {enemy_label} ------------------------------")

        # 1. Load workflow
        if not workflow_path.exists():
            print(f"  [ERROR] Workflow file not found: {workflow_path}")
            results[dest_name] = False
            continue

        with open(workflow_path, "r") as f:
            workflow = json.load(f)

        # 2. Submit
        prompt_id = submit_workflow(workflow)
        if not prompt_id:
            results[dest_name] = False
            continue

        # 3. Poll
        print(f"  [POLLING] Waiting for generation to finish...")
        outputs = poll_until_done(prompt_id)
        if not outputs:
            results[dest_name] = False
            continue

        # 4. Find and copy output image
        img_path = find_output_image(outputs)
        if not img_path:
            print(f"  [WARN] Could not locate output image in job outputs. Raw outputs:\n  {outputs}")
            results[dest_name] = False
            continue

        success = copy_image(img_path, dest_name)
        results[dest_name] = success
        print()

    # ── Summary ─────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    ok  = [k for k, v in results.items() if v]
    bad = [k for k, v in results.items() if not v]

    for name in ok:
        dest = OUTPUT_DIR / name
        size = dest.stat().st_size if dest.exists() else 0
        print(f"  [OK]   {name}  ({size:,} bytes)")
    for name in bad:
        print(f"  [FAIL] {name}")

    print()
    print(f"  Generated: {len(ok)}/5   Failed: {len(bad)}/5")
    print(f"  Output dir: {OUTPUT_DIR}")

    if ok:
        print("\n  Files in C:/game/assets/enemies/:")
        for p in sorted(OUTPUT_DIR.iterdir()):
            print(f"    {p.name}  ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
