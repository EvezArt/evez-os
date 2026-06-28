#!/bin/bash
# Upload eigenforensics to PyPI
# Requires: pip3 install twine build
# Run: bash pypi-upload.sh

cd /home/openclaw/.openclaw/workspace/eigenforensics-pkg
python3 -m build
twine upload dist/*
echo "Uploaded to PyPI: https://pypi.org/project/eigenforensics/"
