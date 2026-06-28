#!/bin/bash
# Upload EVEZ corpus to HuggingFace datasets
# Requires: pip3 install huggingface_hub
# Set: export HF_TOKEN=your_token
# Run: bash hf-upload.sh

from huggingface_hub import HfApi
api = HfApi()
api.create_repo(repo_id="EvezArt/evez-corpus", repo_type="dataset", exist_ok=True)
api.upload_folder(
    folder_path="/home/openclaw/.openclaw/workspace/huggingface-dataset",
    repo_id="EvezArt/evez-corpus",
    repo_type="dataset"
)
print("Uploaded to HuggingFace: https://huggingface.co/datasets/EvezArt/evez-corpus")
