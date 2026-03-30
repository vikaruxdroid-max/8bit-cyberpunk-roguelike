

$url = "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors"
$out = "C:\ComfyUI\models\clip_vision\CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"
(New-Object System.Net.WebClient).DownloadFile($url, $out)
Write-Host "Done. Size: $((Get-Item $out).Length) bytes"
