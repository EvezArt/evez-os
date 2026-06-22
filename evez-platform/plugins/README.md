# evez plugins — Extensible Service Endpoints

## Overview

Anyone can write a plugin that adds new service endpoints to the EVEZ platform. Plugins are first-class services that integrate with the Spine, mesh, and consciousness pipeline.

## Plugin Structure

```
my-plugin/
├── manifest.yaml      # Plugin metadata and capabilities
├── main.py            # Plugin entry point
├── schemas/           # Input/output schemas
│   ├── input.yaml
│   └── output.yaml
├── tests/             # Plugin tests
│   └── test_main.py
└── README.md          # Plugin documentation
```

## Manifest

```yaml
name: my-plugin
version: 1.0.0
description: "Does something amazing"
author: "developer@example.com"

endpoints:
  - path: /my-plugin/process
    method: POST
    description: "Process data"
    input_schema: schemas/input.yaml
    output_schema: schemas/output.yaml

  - path: /my-plugin/status
    method: GET
    description: "Get plugin status"

spine:
  reads:
    - "sense.v1.*"
    - "think.v1.*"
  writes:
    - "custom.v1.MyEvent"

consciousness:
  stages: []  # This plugin doesn't add consciousness stages
  hooks: []    # No hooks into consciousness pipeline
```

## Plugin Entry Point

```python
# main.py
from evez.plugin import Plugin, PluginContext

class MyPlugin(Plugin):
    async def on_load(self, ctx: PluginContext):
        """Called when plugin is loaded."""
        self.ctx = ctx
        self.ctx.logger.info("MyPlugin loaded!")
        
        # Register Spine subscriber
        self.ctx.spine.subscribe("sense.v1.*", self.on_sense_event)
    
    async def on_unload(self):
        """Called when plugin is unloaded."""
        self.ctx.logger.info("MyPlugin unloaded!")
    
    async def on_sense_event(self, event):
        """Handle a sense event from the Spine."""
        self.ctx.logger.info(f"Sense event: {event.hash[:16]}")
    
    # Endpoint handlers
    async def handle_process(self, request):
        """Handle POST /my-plugin/process"""
        result = await self.do_processing(request.json)
        # Write result to Spine
        await self.ctx.spine.append("custom.v1.MyEvent", result)
        return {"status": "ok", "result": result}
    
    async def handle_status(self, request):
        """Handle GET /my-plugin/status"""
        return {"status": "running", "version": "1.0.0"}

def create_plugin():
    return MyPlugin()
```

## Plugin Lifecycle

```
1. Discovery — Plugin found in plugin directory or registry
2. Load      — Plugin loaded, on_load() called
3. Register  — Endpoints registered with gateway
4. Subscribe — Spine subscriptions activated
5. Serve     — Plugin handles requests
6. Unload    — on_unload() called, endpoints removed
```

## Plugin API

```
GET  /plugins                    — List installed plugins
POST /plugins/install            — Install a plugin (from URL or registry)
DELETE /plugins/:name            — Uninstall a plugin
GET  /plugins/:name              — Plugin details
POST /plugins/:name/enable       — Enable plugin
POST /plugins/:name/disable      — Disable plugin
GET  /plugins/:name/status       — Plugin runtime status
```

## Plugin Registry

Plugins can be published to the EVEZ Plugin Registry:

```bash
# Publish
evez plugin publish ./my-plugin/

# Install
evez plugin install my-plugin

# Search
evez plugin search "music synthesis"
```

## Hot Reloading

Plugins can be reloaded without restarting the platform:

```bash
evez plugin reload my-plugin
```

## Sandboxing

Plugins run in isolated contexts:
- **Filesystem:** Only plugin directory + granted paths
- **Network:** Only whitelisted hosts
- **Spine:** Only declared read/write types
- **Resources:** CPU and memory limits per plugin

---

*evez-plugins v1.0.0*
