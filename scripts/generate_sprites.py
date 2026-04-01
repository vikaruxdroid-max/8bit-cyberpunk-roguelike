"""
NEON DUNGEON — ComfyUI Sprite Generator
Generates 5 enemy sprites + 1 player sprite via ComfyUI HTTP API.
Re-runnable: skips existing files unless --force is passed.
"""

import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

COMFYUI_URL = "http://127.0.0.1:8188"
GAME_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENEMIES_DIR = os.path.join(GAME_ROOT, "assets", "enemies")
PLAYER_PATH = os.path.join(GAME_ROOT, "assets", "player.png")
WORKFLOWS_DIR = os.path.join(GAME_ROOT, "comfy_workflows")

NEGATIVE_PROMPT = (
    "blurry, realistic, 3d render, photographic, detailed background, "
    "extra limbs, deformed, watermark, text, gradient background, "
    "multiple characters, crowd, nsfw"
)

SPRITES = [
    {
        "filename": "glitch_slime.png",
        "save_path": os.path.join(ENEMIES_DIR, "glitch_slime.png"),
        "workflow_name": "sprite_glitch_slime",
        "positive": (
            "pixel art, chibi sprite, cyberpunk slime monster, glitching neon green body, "
            "digital corruption effects, pixel glitch artifacts, dark background, clean pixel outlines, "
            "full body centered, game enemy sprite, 16-bit JRPG style"
        ),
    },
    {
        "filename": "neon_wraith.png",
        "save_path": os.path.join(ENEMIES_DIR, "neon_wraith.png"),
        "workflow_name": "sprite_neon_wraith",
        "positive": (
            "pixel art, chibi sprite, cyberpunk ghost wraith, translucent neon purple body, "
            "flowing energy tendrils, holographic shimmer, dark background, clean pixel outlines, "
            "full body centered, game enemy sprite, 16-bit JRPG style"
        ),
    },
    {
        "filename": "cyber_beast.png",
        "save_path": os.path.join(ENEMIES_DIR, "cyber_beast.png"),
        "workflow_name": "sprite_cyber_beast",
        "positive": (
            "pixel art, chibi sprite, cyberpunk beast, chrome plated armor, red glowing eyes, "
            "mechanical limbs, neon orange accents, dark background, clean pixel outlines, "
            "full body centered, game enemy sprite, 16-bit JRPG style"
        ),
    },
    {
        "filename": "rogue_drone.png",
        "save_path": os.path.join(ENEMIES_DIR, "rogue_drone.png"),
        "workflow_name": "sprite_rogue_drone",
        "positive": (
            "pixel art, chibi sprite, cyberpunk rogue drone, floating mechanical sphere, "
            "neon blue thrusters, targeting lasers, antenna array, dark background, clean pixel outlines, "
            "full body centered, game enemy sprite, 16-bit JRPG style"
        ),
    },
    {
        "filename": "data_golem.png",
        "save_path": os.path.join(ENEMIES_DIR, "data_golem.png"),
        "workflow_name": "sprite_data_golem",
        "positive": (
            "pixel art, chibi sprite, cyberpunk data golem, blocky geometric body, glowing circuit lines, "
            "cyan data streams, stone and chrome texture, dark background, clean pixel outlines, "
            "full body centered, game enemy sprite, 16-bit JRPG style"
        ),
    },
    {
        "filename": "player.png",
        "save_path": PLAYER_PATH,
        "workflow_name": "sprite_player",
        "positive": (
            "pixel art, chibi sprite, cyberpunk netrunner, purple hair, tactical bodysuit, "
            "neon cyan visor, holographic interface on arm, dark background, clean pixel outlines, "
            "full body centered, game player sprite, 16-bit JRPG style"
        ),
    },
]

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def api_get(path):
    url = f"{COMFYUI_URL}{path}"
    resp = urllib.request.urlopen(url, timeout=10)
    return json.loads(resp.read())


def api_post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{COMFYUI_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())


def api_download(path):
    resp = urllib.request.urlopen(f"{COMFYUI_URL}{path}", timeout=30)
    return resp.read()

# ---------------------------------------------------------------------------
# Step 1 — verify ComfyUI is reachable
# ---------------------------------------------------------------------------

def verify_comfyui():
    print("\n[STEP 1] Verifying ComfyUI is reachable...")
    try:
        stats = api_get("/system_stats")
        print(f"  OK — ComfyUI running. Python: {stats.get('system', {}).get('python_version', '?')}")
        return True
    except Exception as e:
        print(f"  FAIL — Cannot connect to ComfyUI at {COMFYUI_URL}: {e}")
        print("  Start ComfyUI and retry.")
        return False

# ---------------------------------------------------------------------------
# Step 2 — find available models
# ---------------------------------------------------------------------------

def find_model(candidates, available):
    """Return the first candidate substring found in the available list."""
    for candidate in candidates:
        for name in available:
            if candidate.lower() in name.lower():
                return name
    return None


def get_models():
    print("\n[STEP 2] Querying available models...")
    info = api_get("/object_info")

    checkpoints = info.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [None])[0] or []
    loras = info.get("LoraLoader", {}).get("input", {}).get("required", {}).get("lora_name", [None])[0] or []

    # Prefer Counterfeit V3.0, fall back to pixelArtDiffusionXL, then first available
    checkpoint = find_model(
        ["counterfeit-v30", "counterfeit_v30", "counterfeit", "pixelartdiffusionxl", "pixelart"],
        checkpoints,
    ) or (checkpoints[0] if checkpoints else None)

    lora = find_model(["pixel-art-xl-v1.1", "pixel_art_xl", "pixel-art-xl", "pixelart"], loras)

    if not checkpoint:
        print("  FAIL — No checkpoint models found.")
        return None, None

    print(f"  Checkpoint : {checkpoint}")
    print(f"  LoRA       : {lora or 'not found — generating without LoRA'}")
    return checkpoint, lora

# ---------------------------------------------------------------------------
# Step 3 — build workflow JSON
# ---------------------------------------------------------------------------

def build_workflow(sprite, checkpoint, lora):
    seed = random.randint(0, 2**32 - 1)

    if lora:
        # With LoRA: checkpoint -> lora_loader -> ksampler/clip
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint},
            },
            "8": {
                "class_type": "LoraLoader",
                "inputs": {
                    "model": ["1", 0],
                    "clip": ["1", 1],
                    "lora_name": lora,
                    "strength_model": 0.85,
                    "strength_clip": 0.85,
                },
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": sprite["positive"], "clip": ["8", 1]},
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": NEGATIVE_PROMPT, "clip": ["8", 1]},
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 512, "height": 512, "batch_size": 1},
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["8", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0],
                    "seed": seed,
                    "steps": 28,
                    "cfg": 7,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                },
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {"images": ["6", 0], "filename_prefix": sprite["workflow_name"]},
            },
        }
    else:
        # Without LoRA
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint},
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": sprite["positive"], "clip": ["1", 1]},
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": NEGATIVE_PROMPT, "clip": ["1", 1]},
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 512, "height": 512, "batch_size": 1},
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0],
                    "seed": seed,
                    "steps": 28,
                    "cfg": 7,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                },
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {"images": ["6", 0], "filename_prefix": sprite["workflow_name"]},
            },
        }

    return workflow

# ---------------------------------------------------------------------------
# Step 4 — submit, poll, save
# ---------------------------------------------------------------------------

def queue_prompt(workflow):
    result = api_post("/prompt", {"prompt": workflow})
    return result["prompt_id"]


def poll_until_done(prompt_id, timeout=120):
    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            raise TimeoutError(f"Generation timed out after {timeout}s")
        try:
            history = api_get(f"/history/{prompt_id}")
        except Exception:
            history = {}
        if prompt_id in history:
            return history[prompt_id]
        print(f"    waiting... ({int(elapsed)}s)")
        time.sleep(2)


def download_and_save(image_info, save_path):
    params = urllib.parse.urlencode({
        "filename": image_info["filename"],
        "subfolder": image_info.get("subfolder", ""),
        "type": image_info.get("type", "output"),
    })
    data = api_download(f"/view?{params}")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(data)
    return len(data)


def generate_sprite(sprite, checkpoint, lora, force=False):
    save_path = sprite["save_path"]
    name = sprite["filename"]

    if os.path.exists(save_path) and not force:
        size = os.path.getsize(save_path)
        print(f"  SKIP {name} — already exists ({size} bytes). Use --force to regenerate.")
        return True

    print(f"  Building workflow...")
    workflow = build_workflow(sprite, checkpoint, lora)

    # Save workflow JSON
    os.makedirs(WORKFLOWS_DIR, exist_ok=True)
    wf_path = os.path.join(WORKFLOWS_DIR, f"{sprite['workflow_name']}.json")
    with open(wf_path, "w") as f:
        json.dump(workflow, f, indent=2)
    print(f"  Workflow saved: {wf_path}")

    print(f"  Submitting to ComfyUI...")
    try:
        prompt_id = queue_prompt(workflow)
    except Exception as e:
        print(f"  ERROR submitting {name}: {e}")
        return False
    print(f"  Prompt ID: {prompt_id}")

    print(f"  Polling for completion (timeout 120s)...")
    try:
        history = poll_until_done(prompt_id, timeout=120)
    except TimeoutError as e:
        print(f"  ERROR: {e}")
        return False

    # Extract image output
    outputs = history.get("outputs", {})
    image_info = None
    for node_output in outputs.values():
        if "images" in node_output:
            image_info = node_output["images"][0]
            break

    if not image_info:
        print(f"  ERROR: No image in generation output for {name}")
        return False

    print(f"  Downloading...")
    try:
        byte_count = download_and_save(image_info, save_path)
    except Exception as e:
        print(f"  ERROR downloading {name}: {e}")
        return False

    print(f"  SAVED {save_path} ({byte_count} bytes)")
    return True

# ---------------------------------------------------------------------------
# Step 5 — verify outputs
# ---------------------------------------------------------------------------

def verify_outputs():
    print("\n[STEP 5] Verifying outputs...")
    all_ok = True
    for sprite in SPRITES:
        path = sprite["save_path"]
        if not os.path.exists(path):
            print(f"  MISSING  {path}")
            all_ok = False
        elif os.path.getsize(path) == 0:
            print(f"  EMPTY    {path}")
            all_ok = False
        else:
            size = os.path.getsize(path)
            # Read dimensions from PNG header (bytes 16-24)
            try:
                with open(path, "rb") as f:
                    f.seek(16)
                    w = int.from_bytes(f.read(4), "big")
                    h = int.from_bytes(f.read(4), "big")
                dims = f"{w}x{h}"
            except Exception:
                dims = "?"
            print(f"  OK  {dims:>9}  {size:>8} bytes  {path}")

    return all_ok

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    force = "--force" in sys.argv
    if force:
        print("--force flag set: will regenerate all sprites.")

    # Step 1
    if not verify_comfyui():
        sys.exit(1)

    # Step 2
    checkpoint, lora = get_models()
    if not checkpoint:
        sys.exit(1)

    # Steps 3 & 4
    print(f"\n[STEP 3+4] Generating {len(SPRITES)} sprites...")
    results = []
    for i, sprite in enumerate(SPRITES, 1):
        print(f"\n  [{i}/{len(SPRITES)}] {sprite['filename']}")
        ok = generate_sprite(sprite, checkpoint, lora, force=force)
        results.append((sprite["filename"], ok))

    # Step 5
    all_ok = verify_outputs()

    # Summary
    print("\n--- Summary ---")
    for name, ok in results:
        status = "OK" if ok else "FAILED"
        print(f"  {status:6}  {name}")

    if not all_ok:
        print("\nSome sprites missing or empty. Check errors above.")
        sys.exit(1)
    else:
        print("\nAll sprites generated successfully.")


if __name__ == "__main__":
    main()
