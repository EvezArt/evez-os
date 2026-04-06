#!/usr/bin/env python3
"""
EVEZ NLP - Natural language understanding and generation
Text processing, sentiment, entities, translation
"""

import json
import random
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Sentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class EntityType(Enum):
    PERSON = "person"
    ORG = "organization"
    LOCATION = "location"
    DATE = "date"
    NUMBER = "number"
    ACTION = "action"

@dataclass
class Entity:
    text: str
    type: EntityType
    start: int
    end: int
    confidence: float

@dataclass
class Intent:
    name: str
    confidence: float
    slots: Dict[str, str]

class NLPEngine:
    """EVEZ NLP - Language understanding system"""
    
    def __init__(self):
        self.model_name = "EVEZ-NLP-v1"
        self.intent_patterns = {
            "greeting": ["hello", "hi", "hey", "greetings"],
            "query": ["what", "how", "why", "when", "where", "who"],
            "command": ["run", "execute", "start", "stop", "do"],
            "question": ["?", "is it", "can you", "should i"],
            "statement": ["the", "this", "i think", "it is"]
        }
        
    def parse(self, text: str) -> Dict:
        """Parse text into structured data"""
        # Tokenize
        tokens = text.split()
        
        # Detect entities
        entities = self.extract_entities(text)
        
        # Detect intent
        intent = self.detect_intent(text)
        
        # Sentiment analysis
        sentiment = self.analyze_sentiment(text)
        
        # POS tagging (simulated)
        pos_tags = self._pos_tag(tokens)
        
        return {
            "text": text,
            "tokens": tokens,
            "entities": [vars(e) for e in entities],
            "intent": vars(intent),
            "sentiment": sentiment.value,
            "pos_tags": pos_tags,
            "language": "en"
        }
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities"""
        entities = []
        
        # Simple pattern matching
        patterns = {
            EntityType.PERSON: r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b',
            EntityType.LOCATION: r'\b(in|at|from)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b',
            EntityType.DATE: r'\b(\d{1,2}/\d{1,2}/\d{2,4}|\w+\s\d{1,2},?\s\d{4})\b',
            EntityType.NUMBER: r'\b(\d+(?:\.\d+)?)\b'
        }
        
        for etype, pattern in patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(1) if etype != EntityType.LOCATION else match.group(2),
                    type=etype,
                    start=match.start(),
                    end=match.end(),
                    confidence=random.uniform(0.6, 0.95)
                ))
        
        return entities
    
    def detect_intent(self, text: str) -> Intent:
        """Detect user intent"""
        text_lower = text.lower()
        
        for intent_name, keywords in self.intent_patterns.items():
            for kw in keywords:
                if kw in text_lower:
                    return Intent(
                        name=intent_name,
                        confidence=random.uniform(0.7, 0.95),
                        slots={}
                    )
        
        return Intent("statement", 0.6, {})
    
    def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment of text"""
        positive_words = {"good", "great", "excellent", "amazing", "wonderful", "happy", "love"}
        negative_words = {"bad", "terrible", "awful", "poor", "hate", "sad", "angry"}
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        if pos_count > neg_count:
            return Sentiment.POSITIVE
        elif neg_count > pos_count:
            return Sentiment.NEGATIVE
        return Sentiment.NEUTRAL
    
    def _pos_tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Part-of-speech tagging (simplified)"""
        tags = []
        for token in tokens:
            if token.lower() in {"i", "you", "he", "she", "it", "we", "they"}:
                tags.append((token, "PRON"))
            elif token.lower() in {"is", "are", "was", "were", "be", "have", "do"}:
                tags.append((token, "VERB"))
            elif token[-1] in "sxd" and len(token) > 2:
                tags.append((token, "NOUN"))
            else:
                tags.append((token, random.choice(["NOUN", "ADJ", "VERB", "ADV"])))
        return tags
    
    def generate(self, template: str, data: Dict) -> str:
        """Generate text from template"""
        result = template
        for key, value in data.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def summarize(self, text: str, max_sentences: int = 3) -> str:
        """Summarize text"""
        sentences = text.split(". ")
        summary = sentences[:max_sentences]
        return ". ".join(summary) + ("." if summary else "")
    
    def translate(self, text: str, target_lang: str) -> Dict:
        """Translate text (simulated)"""
        translations = {
            "es": {"hello": "hola", "system": "sistema", "status": "estado"},
            "fr": {"hello": "bonjour", "system": "système", "status": "statut"},
            "de": {"hello": "hallo", "system": "system", "status": "status"}
        }
        
        if target_lang in translations:
            words = text.lower().split()
            translated = [translations[target_lang].get(w, w) for w in words]
            return {"original": text, "translated": " ".join(translated), "target_lang": target_lang}
        
        return {"error": "Language not supported"}
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "intents": list(self.intent_patterns.keys())
        }


# Demo
if __name__ == "__main__":
    nlp = NLPEngine()
    print("=== EVEZ NLP ===")
    result = nlp.parse("EVEZ system at location San Francisco is running well")
    print(f"Intent: {result['intent']['name']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Entities: {len(result['entities'])} found")
    print(json.dumps(nlp.get_status(), indent=2))