#!/usr/bin/env python3
"""
Recover @EVEZ666 tweets from the Wayback Machine.
- Fetches each archived tweet page
- Extracts the "text" field from embedded JSON
- Saves to evez666-tweets-full-archive.md
"""

import json
import re
import time
import urllib.request
import urllib.error
import socket
import os
import sys

CDX_FILE = "/home/openclaw/.openclaw/workspace/cdx_results.json"
OUTPUT_FILE = "/home/openclaw/.openclaw/workspace/evez666-tweets-full-archive.md"

def load_cdx():
    with open(CDX_FILE, "r", encoding="utf-8", errors="replace") as f:
        data = json.load(f)
    # Skip header row
    rows = data[1:]
    entries = []
    for row in rows:
        # [urlkey, timestamp, original, mimetype, statuscode, digest, length]
        urlkey = row[0]
        timestamp = row[1]
        original = row[2]
        # Extract tweet ID from original URL
        m = re.search(r'/status/(\d+)', original)
        if m:
            tweet_id = m.group(1)
        else:
            continue
        entries.append({
            "tweet_id": tweet_id,
            "timestamp": timestamp,
            "original": original,
        })
    return entries

def fetch_page(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                # Try utf-8 first, fall back to latin-1 with errors replaced
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    text = raw.decode("latin-1", errors="replace")
                return text
        except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout, ConnectionError, OSError) as e:
            print(f"    Attempt {attempt+1}/{max_retries} failed: {type(e).__name__}: {e}", flush=True)
            if attempt < max_retries - 1:
                wait = 10 if "refused" in str(e).lower() or "timed out" in str(e).lower() else 5
                print(f"    Waiting {wait}s before retry...", flush=True)
                time.sleep(wait)
            else:
                return None
    return None

def extract_text(html):
    """Extract the first 'text' field from the JSON embedded in the HTML."""
    if not html:
        return None
    
    # Try multiple patterns to find "text": "..."
    # Pattern 1: Standard JSON "text": "value"
    # The text field in Twitter's embedded JSON can be quite large
    patterns = [
        # Match "text": "..." where ... can contain escaped quotes
        r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            # Skip empty or very short metadata texts
            # Decode unicode escapes safely (avoid surrogates)
            def _safe_decode(s):
                def repl(m):
                    cp = int(m.group(1), 16)
                    if 0xD800 <= cp <= 0xDFFF:
                        return ''
                    try:
                        return chr(cp)
                    except ValueError:
                        return ''
                s = re.sub(r'\\u([0-9a-fA-F]{4})', repl, s)
                s = s.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                return s
            decoded = _safe_decode(match)
            if len(decoded) > 5:
                return decoded
    
    return None

def extract_text_v2(html):
    """Alternative extraction: find text field more carefully."""
    if not html:
        return None
    
    # Find all positions of "text": in the HTML
    pos = 0
    results = []
    while True:
        idx = html.find('"text"', pos)
        if idx == -1:
            break
        # Check if it's followed by : and "
        rest = html[idx+6:].lstrip()
        if rest.startswith(':'):
            rest = rest[1:].lstrip()
            if rest.startswith('"'):
                # Find the closing quote (handle escaped quotes)
                i = 1
                while i < len(rest):
                    if rest[i] == '\\':
                        i += 2
                        continue
                    if rest[i] == '"':
                        text_content = rest[1:i]
                        # Unescape
                        text_content = text_content.replace('\\n', '\n')
                        text_content = text_content.replace('\\t', '\t')
                        text_content = text_content.replace('\\"', '"')
                        text_content = text_content.replace('\\\\', '\\')
                        text_content = text_content.replace('\\u2019', "'")
                        text_content = text_content.replace('\\u2014', "—")
                        text_content = text_content.replace('\\u2026', "…")
                        text_content = text_content.replace('\\u2013', "–")
                        text_content = text_content.replace('\\u201c', '"')
                        text_content = text_content.replace('\\u201d', '"')
                        text_content = text_content.replace('\\u00a0', ' ')
                        # Generic unicode escape - skip surrogates
                        def _safe_chr(m):
                            cp = int(m.group(1), 16)
                            if 0xD800 <= cp <= 0xDFFF:
                                return ''
                            return chr(cp)
                        text_content = re.sub(r'\\u([0-9a-fA-F]{4})', _safe_chr, text_content)
                        if len(text_content) > 5:
                            results.append(text_content)
                        break
                    i += 1
        pos = idx + 6
    
    if results:
        # Return the longest result (most likely the tweet text, not metadata)
        return max(results, key=len)
    return None

def extract_text_v3(html):
    """Yet another approach: look for the tweet text near specific markers."""
    if not html:
        return None
    
    # Twitter/X embeds JSON in a <script> tag
    # Look for full_text or text in the embedded JSON
    # Also try looking for the og:description meta tag as fallback
    og_match = re.search(r'<meta\s+(?:property|name)=["\']og:description["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if og_match:
        og_text = og_match.group(1)
        if len(og_text) > 10:
            # HTML decode
            og_text = og_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
            return og_text
    
    return None

def format_date(timestamp):
    """Convert YYYYMMDDHHMMSS to readable date."""
    try:
        ts = timestamp[:14]
        year = ts[0:4]
        month = ts[4:6]
        day = ts[6:8]
        hour = ts[8:10]
        minute = ts[10:12]
        second = ts[12:14]
        return f"{year}-{month}-{day} {hour}:{minute}:{second}"
    except:
        return timestamp

def main():
    entries = load_cdx()
    print(f"Loaded {len(entries)} CDX entries", flush=True)
    
    # Group by tweet_id - keep all timestamps for each tweet
    tweet_map = {}
    for entry in entries:
        tid = entry["tweet_id"]
        if tid not in tweet_map:
            tweet_map[tid] = []
        tweet_map[tid].append(entry)
    
    print(f"Unique tweet IDs: {len(tweet_map)}", flush=True)
    
    # Check for existing progress
    recovered = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        # Parse existing tweets
        existing_blocks = re.findall(r'### Tweet (\d+) — ([^\n]+)\n(.*?)(?=\n---\n|\n### Tweet|\Z)', content, re.DOTALL)
        for block in existing_blocks:
            tid = block[0]
            text = block[2].strip()
            recovered[tid] = text
        print(f"Already recovered {len(recovered)} tweets from previous run", flush=True)
    
    total = len(tweet_map)
    done = len(recovered)
    
    for i, (tweet_id, snapshots) in enumerate(sorted(tweet_map.items())):
        if tweet_id in recovered:
            print(f"[{i+1}/{total}] Tweet {tweet_id} already recovered, skipping", flush=True)
            continue
        
        # Sort snapshots by timestamp, try each
        snapshots.sort(key=lambda x: x["timestamp"])
        
        text_found = None
        for snap in snapshots:
            timestamp = snap["timestamp"]
            original = snap["original"]
            url = f"https://web.archive.org/web/{timestamp}if_/{original}"
            
            print(f"[{i+1}/{total}] Fetching tweet {tweet_id} (ts={timestamp})...", flush=True)
            html = fetch_page(url)
            
            if html:
                # Try extraction methods in order
                text_found = extract_text_v2(html)
                if not text_found or len(text_found) < 10:
                    text_found = extract_text(html)
                if not text_found or len(text_found) < 10:
                    text_found = extract_text_v3(html)
                
                if text_found and len(text_found) > 5:
                    break
            
            # Wait between snapshot attempts
            time.sleep(2)
        
        if text_found:
            recovered[tweet_id] = text_found
            safe_preview = text_found[:80].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            print(f"    ✓ Recovered: {safe_preview}...", flush=True)
        else:
            print(f"    ✗ Failed to extract text for tweet {tweet_id}", flush=True)
            recovered[tweet_id] = f"[Extraction failed - tweet ID {tweet_id}]"
        
        done += 1
        
        # Write progress every 10 tweets
        if done % 10 == 0 or done == total:
            print(f"  Writing progress ({done}/{total})...", flush=True)
            with open(OUTPUT_FILE, "w", encoding="utf-8", errors="replace") as f:
                f.write(f"# @EVEZ666 Tweet Archive — Recovered from Wayback Machine\n\n")
                f.write(f"Recovered {len([t for t in recovered.values() if not t.startswith('[Extraction failed')])} of {total} tweets\n\n")
                f.write(f"---\n\n")
                for tid in sorted(recovered.keys()):
                    text = recovered[tid]
                    # Find the date from the first available snapshot
                    date_str = "unknown"
                    if tid in tweet_map:
                        date_str = format_date(tweet_map[tid][0]["timestamp"])
                    f.write(f"### Tweet {tid} — {date_str}\n")
                    f.write(f"{text}\n")
                    f.write(f"\n---\n\n")
        
        # Rate limiting
        time.sleep(2)
    
    print(f"\nDone! Recovered {len([t for t in recovered.values() if not t.startswith('[Extraction failed')])} tweets out of {total}", flush=True)

if __name__ == "__main__":
    main()
