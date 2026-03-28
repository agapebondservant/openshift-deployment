from huggingface_hub import snapshot_download
import os

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
model_repo = "RedHatAI/Llama-4-Maverick-17B-128E-Instruct-quantized.w4a16"

snapshot_download(
    repo_id=model_repo,
    local_dir="/models",
    allow_patterns=["*.safetensors", "*.json", "*.txt", "*.jinja", "*.py", "*.yaml"],
)