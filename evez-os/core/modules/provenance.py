"""
EVEZ-OS Provenance Tracker
Tags all outputs with EVEZ-ART provenance
"""

import json
from datetime import datetime

class ProvenanceTracker:
    def __init__(self):
        self.session_count = 1
        
    def stamp(self, output, entity_type="trunk"):
        """Add EVEZ-ART provenance stamp to output"""
        stamp = {
            "provenance": "EVEZ-ART",
            "session": self.session_count,
            "entity": entity_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if isinstance(output, dict):
            output["_provenance"] = stamp
        elif isinstance(output, str):
            output = f"{output}\n\n[PROVENANCE: EVEZ-ART | SESSION: {self.session_count} | ENTITY: {entity_type}]"
            
        return output
        
    def next_session(self):
        """Increment session count"""
        self.session_count += 1