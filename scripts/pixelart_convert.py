"""Convert any image to pixel art style via ComfyUI img2img."""

import sys
import json
import time
import urllib.request
import urllib.error
import urllib.parse
import uuid
import os

COMFYUI_URL = "http://127.0.0.1:8188"
WORKFLOW_PATH = os.path.join(os.path.dirname(__file__), "workflow_pixelart.json")


def upload_image(image_path):
    filename = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Detect content type
    ext = os.path.splitext(filename)[1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            ".webp": "image/webp"}.get(ext.lstrip("."), "image/png")

    boundary = uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + image_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
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
    return json.loads(resp.read())["prompt_id"]


def poll_until_done(prompt_id):
    while True:
        resp = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}")
        history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        print("  ...waiting")
        time.sleep(2)


def download_image(filename, subfolder, output_type, save_path):
    params = urllib.parse.urlencode(
        {"filename": filename, "subfolder": subfolder, "type": output_type}
    )
    resp = urllib.request.urlopen(f"{COMFYUI_URL}/view?{params}")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(resp.read())


def main():
    if len(sys.argv) < 2:
        print("Usage: python pixelart_convert.py <image_path> [denoise] [output_path]")
        print("  denoise: 0.0-1.0, default 0.70 (higher = more stylized)")
        print("  output_path: default <input_name>_pixel.png next to input")
        sys.exit(1)

    input_path = os.path.abspath(sys.argv[1])
    denoise = float(sys.argv[2]) if len(sys.argv) > 2 else 0.70
    if len(sys.argv) > 3:
        output_path = os.path.abspath(sys.argv[3])
    else:
        base, ext = os.path.splitext(input_path)
        output_path = base + "_pixel.png"

    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    print(f"[1/6] Loading workflow: {os.path.basename(WORKFLOW_PATH)}")
    with open(WORKFLOW_PATH) as f:
        workflow = json.load(f)

    print(f"[2/6] Uploading image: {os.path.basename(input_path)}")
    try:
        uploaded_name = upload_image(input_path)
    except urllib.error.URLError as e:
        print(f"ERROR: Could not connect to ComfyUI at {COMFYUI_URL}: {e}")
        sys.exit(1)
    print(f"       Uploaded as: {uploaded_name}")

    print(f"[3/6] Configuring workflow (denoise={denoise})")
    workflow["14"]["inputs"]["image"] = uploaded_name
    workflow["3"]["inputs"]["denoise"] = denoise
    workflow["3"]["inputs"]["seed"] = int.from_bytes(os.urandom(4), "big")

    print(f"[4/6] Queuing prompt to ComfyUI")
    prompt_id = queue_prompt(workflow)
    print(f"       Prompt ID: {prompt_id}")

    print("[5/6] Waiting for generation...")
    history = poll_until_done(prompt_id)

    print("[6/6] Downloading result...")
    outputs = history["outputs"]
    image_info = None
    for node_output in outputs.values():
        if "images" in node_output:
            image_info = node_output["images"][0]
            break

    if not image_info:
        print("ERROR: No image output found")
        sys.exit(1)

    download_image(
        image_info["filename"],
        image_info.get("subfolder", ""),
        image_info.get("type", "output"),
        output_path,
    )

    print(f"Done! Saved to: {output_path}")


if __name__ == "__main__":
    main()
