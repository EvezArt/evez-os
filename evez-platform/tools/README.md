# evez tools — Distributed Tool Discovery & Invocation

## Overview

In EVEZ, tools are services. Services are tools. Any agent can discover and invoke any tool across the mesh. Tools register themselves as services and are discoverable via the mesh directory.

## Philosophy

**OpenClaw:** Tools are local functions or plugins bound to one agent.

**EVEZ:** Tools are services distributed across the mesh. Any agent on any node can use any tool. The mesh is the toolbox.

## Tool Registration

A tool registers itself as a mesh service:

```yaml
# tools/docker-build.yaml
name: docker-build
version: 1.0.0
description: "Build Docker images"

service:
  type: grpc
  endpoint: "grpc://tools-node.evez.mesh:5001"
  
input_schema:
  type: object
  required: ["dockerfile", "tag"]
  properties:
    dockerfile:
      type: string
      description: "Path to Dockerfile"
    tag:
      type: string
      description: "Image tag"
    build_args:
      type: object
      description: "Build arguments"

output_schema:
  type: object
  properties:
    image_id:
      type: string
    size_bytes:
      type: integer
    build_duration_ms:
      type: integer

capabilities:
  - docker.build
  - docker.push

rate_limit:
  requests_per_minute: 10

auth:
  required: true
  roles: ["agent", "admin"]
```

## Tool Discovery

Agents discover tools via the mesh service directory:

```python
# Find all tools that can build Docker images
tools = await mesh.discover_tools(capability="docker.build")

# Find the nearest tool (by network latency)
tool = await mesh.discover_tool(
    capability="docker.build",
    strategy="nearest"  # or "random", "least-loaded", "all"
)
```

## Tool Invocation

```python
# Invoke a tool directly
result = await tool.invoke({
    "dockerfile": "./Dockerfile",
    "tag": "evez-platform:latest",
    "build_args": {"NODE_ENV": "production"}
})

# Invoke via mesh (auto-discovers best node)
result = await mesh.invoke_tool(
    capability="docker.build",
    params={
        "dockerfile": "./Dockerfile",
        "tag": "evez-platform:latest"
    }
)
```

## Tool Streaming

Long-running tools stream results:

```python
# Stream build logs
async for chunk in tool.invoke_stream(params):
    print(chunk["log"])
```

## Tool Composition

Tools can compose other tools:

```python
# A deployment tool that uses docker-build + docker-push + k8s-deploy
class DeployTool:
    async def invoke(self, params):
        build_result = await mesh.invoke_tool("docker.build", params)
        push_result = await mesh.invoke_tool("docker.push", {
            "image": build_result["image_id"],
            "registry": params["registry"]
        })
        deploy_result = await mesh.invoke_tool("k8s.deploy", {
            "image": push_result["image_url"],
            "namespace": params["namespace"]
        })
        return deploy_result
```

## Built-in Tools

| Tool | Capability | Description |
|------|-----------|-------------|
| `exec` | `shell.exec` | Execute shell commands |
| `http` | `http.request` | Make HTTP requests |
| `git` | `git.*` | Git operations |
| `docker` | `docker.*` | Docker operations |
| `k8s` | `k8s.*` | Kubernetes operations |
| `file` | `file.read/write` | File operations |
| `web` | `web.search/scrape` | Web search and scraping |
| `llm` | `llm.complete/embed` | LLM completion and embeddings |
| `tts` | `audio.tts` | Text-to-speech |
| `daw` | `audio.synthesize` | Music synthesis (EVEZ exclusive) |

## API

```
GET  /tools                    — List all registered tools
GET  /tools/:name              — Tool details and schema
POST /tools/:name/invoke       — Invoke a tool
POST /tools/register           — Register a new tool
DELETE /tools/:name             — Unregister a tool
GET  /tools/:name/health       — Tool health check
GET  /tools/capabilities/:cap  — Find tools by capability
```

---

*evez-tools v1.0.0*
