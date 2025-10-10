from huggingface_hub import snapshot_download

model_repo = "Qwen/Qwen2.5-VL-3B-Instruct"
snapshot_download(
    repo_id=model_repo,
    local_dir="/models",
    allow_patterns=["*.safetensors", "*.json", "*.txt"],
)