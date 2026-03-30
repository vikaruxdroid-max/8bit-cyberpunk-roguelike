"""
Neon Dungeon - 8-bit Character Sprite Generator
Generates 7 humorous combat poses for the devil horns character
Requires: ComfyUI running at http://127.0.0.1:8188
Usage: python scripts/generate_devil_sprites.py
"""

import requests
import json
import time
import os
import sys
import urllib.request

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = "assets/characters/devil"
WORKFLOW_PATH = "scripts/backanime.json"
FIXED_SEED = 885357046548253

BASE_PROMPT = """pixel art character sprite, 8-bit style, full body,
dark red devil horns, red and yellow puffy jacket,
blue baggy pants, red sneakers with cyan sole,
brown skin, blue eyes, short dark red hair,
chunky pixels, retro game sprite, white background,
bold pixel outlines, limited color palette,
humorous cartoon expression, NES style"""

NEGATIVE_PROMPT = """blurry, realistic, 3D, watermark, text,
smooth gradients, high resolution, anime,
multiple characters, background clutter,
nsfw, revealing"""

POSES = {
    "idle": "smug crossed arms standing pose, slightly bored expression,",
    "attack": "wildly swinging oversized fist punch, one shoe flying off, exaggerated attack pose, comedy action,",
    "special": "tiny dramatic magic casting pose, small spark effect, underwhelming spell, comedic expression,",
    "hit": "comically squashed flat from hit, stars circling head, x eyes dizzy expression, flattened body,",
    "death": "face-plant flat on ground, x eyes, lying face down, arms and legs splayed out, comedic death pose,",
    "victory": "finger guns pose, winking, smug grin, one eyebrow raised, confident stance,",
    "taunt": "inspecting fingernails unbothered, looking away, completely unimpressed expression, ignoring opponent,",
}


def load_workflow():
    with open(WORKFLOW_PATH, "r") as f:
        return json.load(f)


def find_positive_clip_node(workflow):
    # backanime.json uses a Text Multiline node ("26") that feeds CLIPTextEncode ("6")
    # Check for Text Multiline first (node whose text feeds a CLIPTextEncode)
    for node_id, node in workflow.items():
        if node.get("class_type") in ("Text Multiline", "CLIPTextEncode"):
            inputs = node.get("inputs", {})
            text = inputs.get("text", "")
            if isinstance(text, str) and len(text) > 10:
                if "watermark" not in text.lower() and "blurry" not in text.lower():
                    return node_id
    return None


def find_negative_clip_node(workflow):
    for node_id, node in workflow.items():
        if node.get("class_type") == "CLIPTextEncode":
            inputs = node.get("inputs", {})
            text = inputs.get("text", "")
            if isinstance(text, str):
                if "watermark" in text.lower() or "blurry" in text.lower():
                    return node_id
    return None


def find_ksampler_node(workflow):
    for node_id, node in workflow.items():
        if node.get("class_type") == "KSampler":
            return node_id
    return None


def find_latent_node(workflow):
    for node_id, node in workflow.items():
        if node.get("class_type") == "EmptyLatentImage":
            return node_id
    return None


def queue_prompt(workflow):
    payload = {"prompt": workflow}
    response = requests.post(f"{COMFYUI_URL}/prompt", json=payload)
    response.raise_for_status()
    return response.json()["prompt_id"]


def poll_until_done(prompt_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
        history = response.json()
        if prompt_id in history:
            return history[prompt_id]
        print(f"  Waiting... ({int(time.time() - start)}s)")
        time.sleep(2)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def download_output(history, pose_name, output_dir):
    outputs = history.get("outputs", {})
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            for image in node_output["images"]:
                filename = image["filename"]
                subfolder = image.get("subfolder", "")
                url = f"{COMFYUI_URL}/view?filename={filename}&subfolder={subfolder}&type=output"
                save_path = os.path.join(output_dir, f"{pose_name}.png")
                urllib.request.urlretrieve(url, save_path)
                return save_path
    return None


def generate_pose(pose_name, pose_prefix, output_dir):
    print(f"  Loading workflow...")
    workflow = load_workflow()

    full_prompt = f"{pose_prefix} {BASE_PROMPT}"

    pos_node = find_positive_clip_node(workflow)
    neg_node = find_negative_clip_node(workflow)
    ksampler_node = find_ksampler_node(workflow)
    latent_node = find_latent_node(workflow)

    if pos_node:
        workflow[pos_node]["inputs"]["text"] = full_prompt
        print(f"  Updated positive prompt in node {pos_node}")
    else:
        print("  WARNING: Could not find positive CLIP node")

    if neg_node:
        workflow[neg_node]["inputs"]["text"] = NEGATIVE_PROMPT

    if ksampler_node:
        workflow[ksampler_node]["inputs"]["seed"] = FIXED_SEED
        workflow[ksampler_node]["inputs"]["control_after_generate"] = "fixed"

    if latent_node:
        workflow[latent_node]["inputs"]["batch_size"] = 1

    print(f"  Queuing prompt...")
    prompt_id = queue_prompt(workflow)
    print(f"  Prompt ID: {prompt_id}")

    print(f"  Polling for completion...")
    history = poll_until_done(prompt_id)

    print(f"  Downloading output...")
    saved_path = download_output(history, pose_name, output_dir)

    if saved_path:
        print(f"  Saved: {saved_path}")
        return saved_path
    else:
        print(f"  ERROR: No output image found")
        return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

    try:
        requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        print(f"ComfyUI running at {COMFYUI_URL}")
    except requests.exceptions.ConnectionError:
        print(f"ERROR: ComfyUI not running at {COMFYUI_URL}")
        sys.exit(1)

    if not os.path.exists(WORKFLOW_PATH):
        print(f"ERROR: Workflow not found at {WORKFLOW_PATH}")
        sys.exit(1)

    results = {}
    total = len(POSES)

    for i, (pose_name, pose_prefix) in enumerate(POSES.items(), 1):
        print(f"\n[{i}/{total}] Generating: {pose_name}")
        print(f"  Pose: {pose_prefix[:60]}...")
        try:
            path = generate_pose(pose_name, pose_prefix, OUTPUT_DIR)
            results[pose_name] = "SUCCESS" if path else "FAILED - no output"
        except Exception as e:
            results[pose_name] = f"FAILED - {e}"
            print(f"  ERROR: {e}")

    print("\n" + "="*50)
    print("GENERATION COMPLETE")
    print("="*50)
    for pose_name, status in results.items():
        icon = "OK" if status == "SUCCESS" else "!!"
        print(f"  {icon} {pose_name}: {status}")

    success_count = sum(1 for s in results.values() if s == "SUCCESS")
    print(f"\n{success_count}/{total} poses generated successfully")
    print(f"Files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
