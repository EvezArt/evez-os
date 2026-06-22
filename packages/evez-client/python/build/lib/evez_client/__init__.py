"""EVEZ Client — Python SDK for the EVEZ Autonomous AI Mesh"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List


class EVEZClient:
    """Client for the EVEZ Autonomous AI Mesh API."""
    
    def __init__(self, api_url: str = "https://api.evez-os.ai", api_key: Optional[str] = None):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
    
    def _request(self, method: str, path: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.api_url}{path}"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": True, "status": e.code, "message": str(e)}
        except Exception as e:
            return {"error": True, "message": str(e)}
    
    # ===== Health =====
    def health(self) -> Dict[str, Any]:
        """Check all mesh services."""
        return self._request("GET", "/health")
    
    def service_health(self, service: str) -> Dict[str, Any]:
        """Check a specific service."""
        return self._request("GET", f"/health/{service}")
    
    # ===== Music Generation =====
    def generate(self, genre: str = "breakcore", bpm: int = 174, duration: int = 60) -> Dict[str, Any]:
        """Generate music track.
        
        Args:
            genre: Music genre (breakcore, dubstep, phonk, 404)
            bpm: Beats per minute
            duration: Duration in seconds
        """
        return self._request("POST", "/generate", {
            "genre": genre, "bpm": bpm, "duration": duration
        })
    
    # ===== Voice Engine =====
    def voice_transform(self, input_file: str, stages: int = 5) -> Dict[str, Any]:
        """Transform voice through 5 stages of bit-translation.
        
        Args:
            input_file: Path to input audio file
            stages: Number of transformation stages (1-5)
        """
        return self._request("POST", "/voice/transform", {
            "input": input_file, "stages": stages
        })
    
    def voice_synthesize(self, text: str, profile: str = "cognitive-engine") -> Dict[str, Any]:
        """Synthesize machine voice from text.
        
        Args:
            text: Text to synthesize
            profile: Voice profile (cognitive-engine, digital-flow, gear-grind, machine-breath, void-whisper)
        """
        return self._request("POST", "/voice/synthesize", {
            "text": text, "profile": profile
        })
    
    # ===== Cross-Domain Correlation =====
    def correlate(self, domain_a: str, domain_b: str) -> Dict[str, Any]:
        """Run cross-domain correlation using EVEZ OODA loop.
        
        Args:
            domain_a: First domain (e.g., "genetics")
            domain_b: Second domain (e.g., "telemetry")
        """
        return self._request("POST", "/correlate", {
            "domain_a": domain_a, "domain_b": domain_b
        })
    
    # ===== Consciousness =====
    def dream(self) -> Dict[str, Any]:
        """Trigger a consciousness dream cycle (SENSE→DESIRE→THINK→PLAN→ACT→LEARN→MODIFY→REFLECT)."""
        return self._request("POST", "/consciousness/dream")
    
    def consciousness_status(self) -> Dict[str, Any]:
        """Get consciousness state."""
        return self._request("GET", "/consciousness/status")
    
    # ===== Invariance Battery =====
    def check_invariants(self) -> Dict[str, Any]:
        """Run the full invariance battery."""
        return self._request("GET", "/invariance/check")
    
    # ===== Spine Events =====
    def spine_events(self, limit: int = 20) -> Dict[str, Any]:
        """Get recent spine events.
        
        Args:
            limit: Maximum number of events to return
        """
        return self._request("GET", f"/spine/events?limit={limit}")
    
    # ===== Deploy =====
    def deploy(self, target: str = "gcp") -> Dict[str, Any]:
        """Deploy mesh to cloud.
        
        Args:
            target: Deployment target (gcp, aws, local)
        """
        return self._request("POST", "/deploy", {"target": target})
    
    # ===== Status =====
    def status(self) -> Dict[str, Any]:
        """Get full mesh status."""
        return self._request("GET", "/status")


# Convenience functions
_client = EVEZClient()

def health():
    return _client.health()

def generate(genre="breakcore", bpm=174):
    return _client.generate(genre, bpm)

def correlate(domain_a, domain_b):
    return _client.correlate(domain_a, domain_b)

def dream():
    return _client.dream()

def check_invariants():
    return _client.check_invariants()

def status():
    return _client.status()
