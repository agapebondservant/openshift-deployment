from huggingface_hub import snapshot_download

model_repo = "ibm-granite/granite-4.0-h-tiny"
snapshot_download(
    repo_id=model_repo,
    local_dir="/models",
    allow_patterns=["*.safetensors", "*.json", "*.txt", "*.jinja"],
)