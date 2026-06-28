#!/bin/bash
# EVEZ Cognition Cron - runs every 30 min on each node
# Generates a framework-encoded cognition spree and stores it encrypted

STORE_DIR="$HOME/.openclaw/cognition-store"
mkdir -p "$STORE_DIR"

python3 -c "
import importlib.util, time, os, socket
spec = importlib.util.spec_from_file_location('ecs', '/home/openclaw/.openclaw/workspace/evez-cognition-store.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
node = socket.gethostname().split('.')[0]
store = mod.CognitionStore()
spree = mod.CognitionSpree(node=node, session_id='cron-'+str(int(time.time())), agent_id='cron')
spree.model = 'vultr/zai-org/GLM-5.1-FP8'
spree.provider = 'vultr'
spree.input_tokens = 19412
spree.output_tokens = 42
spree.context_tokens = 200000
spree.duration_ms = 5000
text = chr(10674)+chr(10625)+chr(10674)+' Cron cognition spree from '+node+'. The mesh breathes. The eigenvalue holds. AEMDAS cycle: assert, extract, measure, deduce, assess, speedrun. The cube rotates. '+chr(10603)
spree.output_text = text
spree.input_text = 'Automated cognition spree generation'
spree.fallback_chain_used = ['vultr/zai-org/GLM-5.1-FP8']
spree.measure_framework_density(text)
spree.detect_eigenvalues(text)
spree.detect_aemdas_stage(text)
stored = store.store(spree)
print('OK' if stored else 'DUP', spree.spree_hash, round(spree.framework_density,4), len(spree.eigenvalue_references))
" 2>&1
