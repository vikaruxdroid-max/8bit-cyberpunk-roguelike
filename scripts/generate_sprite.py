"""Generate a single character sprite pose via ComfyUI API with IP-Adapter."""

import sys
import json
import time
import urllib.request
import urllib.error
import urllib.parse
import uuid
import os

COMFYUI_URL = "http://127.0.0.1:8188"
WORKFLOW_PATH = os.path.join(os.path.dirname(__file__), "workflow_ipadapter.json")
REFERENCE_IMAGE = os.path.join(os.path.dirname(__file__), "..", "assets", "characters", "idle.png")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "characters")


def load_workflow():
    with open(WORKFLOW_PATH, "r") as f:
        return json.load(f)


def upload_reference_image(image_path):
    """Upload idle.png to ComfyUI's input folder so LoadImage node can find it."""
    filename = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        image_data = f.read()

    boundary = uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + image_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    return result.get("name", filename)


def queue_prompt(workflow):
    client_id = str(uuid.uuid4())
    payload = json.dumps({"prompt": workflow, "client_id": client_id}).encode()
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    return result["prompt_id"]


def poll_until_done(prompt_id):
    while True:
        resp = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}")
        history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        print("  ...waiting for generation to complete")
        time.sleep(2)


def download_image(filename, subfolder, output_type, save_path):
    params = urllib.parse.urlencode(
        {"filename": filename, "subfolder": subfolder, "type": output_type}
    )
    resp = urllib.request.urlopen(f"{COMFYUI_URL}/view?{params}")
    image_data = resp.read()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(image_data)


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_sprite.py <pose_name> <prompt_text>")
        sys.exit(1)

    pose_name = sys.argv[1]
    prompt_text = sys.argv[2]

    print(f"[1/8] Loading workflow from {WORKFLOW_PATH}")
    workflow = load_workflow()

    print(f"[2/8] Uploading reference image: idle.png")
    ref_path = os.path.abspath(REFERENCE_IMAGE)
    if not os.path.exists(ref_path):
        print(f"ERROR: Reference image not found at {ref_path}")
        sys.exit(1)
    uploaded_name = upload_reference_image(ref_path)
    # Update LoadImage node (28) to use the uploaded filename
    workflow["28"]["inputs"]["image"] = uploaded_name
    print(f"       Uploaded as: {uploaded_name}")

    print(f"[3/8] Setting prompt for pose: {pose_name}")
    # Node 26 is the Text Multiline feeding the positive CLIP Text Encode
    workflow["26"]["inputs"]["text"] = prompt_text
    # Single image instead of batch
    workflow["5"]["inputs"]["batch_size"] = 1

    print(f"[4/8] Queuing prompt to ComfyUI at {COMFYUI_URL}")
    print(f"       Pipeline: generate -> RMBG-2.0 background removal -> transparent PNG")
    try:
        prompt_id = queue_prompt(workflow)
    except urllib.error.URLError as e:
        print(f"ERROR: Could not connect to ComfyUI at {COMFYUI_URL}: {e}")
        sys.exit(1)
    print(f"       Prompt ID: {prompt_id}")

    print("[5/8] Polling for completion (includes RMBG processing)...")
    history = poll_until_done(prompt_id)

    print("[6/8] Downloading transparent PNG output...")
    outputs = history["outputs"]
    save_node_id = None
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            save_node_id = node_id
            break

    if save_node_id is None:
        print("ERROR: No image output found in generation results")
        sys.exit(1)

    image_info = outputs[save_node_id]["images"][0]
    save_path = os.path.join(os.path.abspath(OUTPUT_DIR), f"{pose_name}.png")

    download_image(
        image_info["filename"],
        image_info.get("subfolder", ""),
        image_info.get("type", "output"),
        save_path,
    )

    print(f"[7/8] Saved: {save_path}")
    print(f"[8/8] Background removed — transparent PNG ready")
    print(f"Done! Generated {pose_name}.png")


if __name__ == "__main__":
    main()
