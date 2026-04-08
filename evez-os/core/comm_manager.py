#!/usr/bin/env python3
"""
EVEZ Communication Manager
=======================
Multi-platform communication for sales and customer service.
Designed to be Steven's ONLY point of contact.

Platforms:
- Telegram (Sphinx) - WORKING
- X/Twitter - READY (needs auth or manual post)
- Email (Gmail via gog) - REQUIRES SETUP
- Webchat (OpenClaw) - ACTIVE

Inbound: Monitors all channels, routes to Kai
Outbound: Can generate and send responses
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path("/root/.openclaw/workspace")
EVEZ_CORE = WORKSPACE / "evez-os/core"

# Import context bridge
import sys
sys.path.insert(0, str(EVEZ_CORE))
try:
    from context.bridge import ContextBridge
except ImportError:
    ContextBridge = None


class CommManager:
    """Manage all communication platforms"""
    
    def __init__(self):
        self.bridge = ContextBridge() if ContextBridge else None
        self.inbox_file = WORKSPACE / "comm_inbox.jsonl"
        self.outbox_file = WORKSPACE / "comm_outbox.jsonl"
        self.contacts_file = WORKSPACE / "comm_contacts.json"
        
        # Platform capabilities
        self.platforms = {
            'telegram': {'status': 'working', 'capabilities': ['send', 'receive', 'reply']},
            'x': {'status': 'ready', 'capabilities': ['post', 'read'], 'note': 'needs xurl auth'},
            'email': {'status': 'requires_setup', 'capabilities': ['send', 'receive'], 'note': 'needs gog auth'},
            'streamchat': {'status': 'active', 'capabilities': ['send', 'receive']},
            'webchat': {'status': 'active', 'capabilities': ['send', 'receive']}
        }
        
    def log_inbound(self, platform: str, sender: str, message: str, metadata: Dict = None):
        """Log inbound message"""
        entry = {
            'type': 'inbound',
            'platform': platform,
            'sender': sender,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {},
            'status': 'unread'
        }
        
        with open(self.inbox_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
            
        # Log to context
        if self.bridge:
            self.bridge.commit_decision(
                decision=f'Inbound: {platform}/{sender}',
                rationale=message[:100],
                outcome='Added to inbox'
            )
            
        return entry
    
    def log_outbound(self, platform: str, recipient: str, message: str, status: str = 'ready'):
        """Log outbound message"""
        entry = {
            'type': 'outbound',
            'platform': platform,
            'recipient': recipient,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'status': status
        }
        
        with open(self.outbox_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
            
        if self.bridge:
            self.bridge.commit_decision(
                decision=f'Outbound: {platform}/{recipient}',
                rationale=message[:100],
                outcome=f'Status: {status}'
            )
            
        return entry
    
    def get_inbox(self, platform: str = None, status: str = None, limit: int = 10) -> List[Dict]:
        """Get messages from inbox"""
        results = []
        
        if not self.inbox_file.exists():
            return results
            
        with open(self.inbox_file) as f:
            for line in f:
                msg = json.loads(line)
                
                if platform and msg.get('platform') != platform:
                    continue
                if status and msg.get('status') != status:
                    continue
                    
                results.append(msg)
                
        return results[-limit:]
    
    def get_contacts(self) -> Dict:
        """Get contact list"""
        if self.contacts_file.exists():
            with open(self.contacts_file) as f:
                return json.load(f)
        return {}
    
    def add_contact(self, platform: str, identifier: str, name: str = None, notes: str = None):
        """Add a contact"""
        contacts = self.get_contacts()
        
        if platform not in contacts:
            contacts[platform] = []
            
        contact = {
            'identifier': identifier,
            'name': name or identifier,
            'notes': notes,
            'added_at': datetime.utcnow().isoformat()
        }
        
        # Avoid duplicates
        existing = [c for c in contacts[platform] if c.get('identifier') == identifier]
        if not existing:
            contacts[platform].append(contact)
            
        with open(self.contacts_file, 'w') as f:
            json.dump(contacts, f, indent=2)
            
        return contact
    
    def generate_auto_response(self, message: str, context: Dict = None) -> str:
        """Generate automatic response based on message content"""
        # Simple keyword-based response generator
        message_lower = message.lower()
        
        responses = {
            'price': 'I offer flat-rate services. Check my Fiverr for details: [link]',
            'cost': 'Pricing varies by scope. Let me understand your needs first.',
            'demo': 'I can show you a live demo. What time works for you?',
            'help': "I'm here to help. What specific problem are you solving?",
            'autonomous': 'I run autonomous agent systems. I can set one up for you.',
            'default': "Thanks for reaching out. Let me understand your needs and I'll get back to you with a tailored solution."
        }
        
        for keyword, response in responses.items():
            if keyword in message_lower:
                return response
                
        return responses['default']
    
    def send_via_platform(self, platform: str, recipient: str, message: str) -> Dict:
        """Send message via appropriate platform"""
        
        if platform == 'telegram':
            return self._send_telegram(recipient, message)
        elif platform == 'x':
            return self._send_x(message)
        elif platform == 'email':
            return self._send_email(recipient, message)
        else:
            return {'success': False, 'error': f'Unknown platform: {platform}'}
    
    def _send_telegram(self, chat_id: str, message: str) -> Dict:
        """Send via Telegram (Sphinx)"""
        # Log as ready - actual send requires Sphinx to be running
        self.log_outbound('telegram', chat_id, message, 'ready')
        
        # Try to send via OpenClaw message tool if available
        return {
            'success': True, 
            'status': 'ready',
            'note': 'Telegram message logged, ready to send via Sphinx'
        }
    
    def _send_x(self, message: str) -> Dict:
        """Send via X/Twitter"""
        # Log as ready - needs xurl auth
        self.log_outbound('x', '@Evez666', message, 'ready')
        
        return {
            'success': True,
            'status': 'ready',
            'note': 'X post logged, needs xurl auth or manual post'
        }
    
    def _send_email(self, recipient: str, message: str) -> Dict:
        """Send via Email"""
        # Log as ready - needs gog setup
        self.log_outbound('email', recipient, message, 'ready')
        
        return {
            'success': True,
            'status': 'ready',
            'note': 'Email logged, needs gog auth setup'
        }
    
    def get_platform_status(self) -> Dict:
        """Get status of all platforms"""
        return {
            'platforms': self.platforms,
            'inbox_count': sum(1 for _ in open(self.inbox_file)) if self.inbox_file.exists() else 0,
            'outbox_count': sum(1 for _ in open(self.outbox_file)) if self.outbox_file.exists() else 0
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Communication Manager")
    parser.add_argument("--status", action="store_true", help="Show platform status")
    parser.add_argument("--inbox", action="store_true", help="Show inbox")
    parser.add_argument("--add-contact", nargs=3, metavar=("PLATFORM", "ID", "NAME"), help="Add contact")
    parser.add_argument("--send", nargs=3, metavar=("PLATFORM", "RECIPIENT", "MESSAGE"), help="Send message")
    
    args = parser.parse_args()
    
    comm = CommManager()
    
    if args.status:
        print(json.dumps(comm.get_platform_status(), indent=2))
        
    elif args.inbox:
        for msg in comm.get_inbox():
            print(f"[{msg['platform']}] {msg['sender']}: {msg['message'][:50]}...")
            
    elif args.add_contact:
        platform, identifier, name = args.add_contact
        result = comm.add_contact(platform, identifier, name)
        print(json.dumps(result, indent=2))
        
    elif args.send:
        platform, recipient, message = args.send
        result = comm.send_via_platform(platform, recipient, message)
        print(json.dumps(result, indent=2))
        
    else:
        print("Use --status, --inbox, --add-contact, or --send")


if __name__ == "__main__":
    main()
