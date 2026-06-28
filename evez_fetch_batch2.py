#!/usr/bin/env python3
"""
Recover @EVEZ666 tweets from Wayback Machine — Batch 2+
Processes additional CDX files and appends to the existing archive.
"""

import json
import re
import time
import urllib.request
import urllib.error
import socket
import os
import glob

OUTPUT_FILE = "/home/openclaw/.openclaw/workspace/evez666-tweets-full-archive.md"
CDX_DIR = "/home/openclaw/.openclaw/workspace"

def load_all_cdx():
    """Load all CDX result files."""
    all_entries = []
    seen_ids = set()
    
    files = sorted(glob.glob(os.path.join(CDX_DIR, "cdx_results*.json")))
    # Also include the original
    files.append(os.path.join(CDX_DIR, "cdx_results.json"))
    # Deduplicate files
    files = list(set(files))
    
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            rows = data[1:]  # Skip header
            for row in rows:
                urlkey = row[0]
                timestamp = row[1]
                original = row[2]
                m = re.search(r'/status/(\d+)', original)
                if m:
                    tweet_id = m.group(1)
                    if tweet_id not in seen_ids:
                        seen_ids.add(tweet_id)
                        all_entries.append({
                            "tweet_id": tweet_id,
                            "timestamp": timestamp,
                            "original": original,
                        })
        except Exception as e:
            print(f"Error loading {fpath}: {e}", flush=True)
    
    return all_entries

def fetch_page(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
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

def extract_text_v2(html):
    """Extract the longest 'text' field from JSON embedded in the HTML."""
    if not html:
        return None
    
    pos = 0
    results = []
    while True:
        idx = html.find('"text"', pos)
        if idx == -1:
            break
        rest = html[idx+6:].lstrip()
        if rest.startswith(':'):
            rest = rest[1:].lstrip()
            if rest.startswith('"'):
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
                            try:
                                return chr(cp)
                            except ValueError:
                                return ''
                        text_content = re.sub(r'\\u([0-9a-fA-F]{4})', _safe_chr, text_content)
                        if len(text_content) > 5:
                            results.append(text_content)
                        break
                    i += 1
        pos = idx + 6
    
    if results:
        return max(results, key=len)
    return None

def extract_text_v3(html):
    """Fallback: look for og:description meta tag."""
    if not html:
        return None
    og_match = re.search(r'<meta\s+(?:property|name)=["\']og:description["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if og_match:
        og_text = og_match.group(1)
        if len(og_text) > 10:
            og_text = og_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
            return og_text
    return None

def format_date(timestamp):
    try:
        ts = timestamp[:14]
        return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}:{ts[12:14]}"
    except:
        return timestamp

def main():
    entries = load_all_cdx()
    print(f"Loaded {len(entries)} unique CDX entries from all files", flush=True)
    
    # Group by tweet_id
    tweet_map = {}
    for entry in entries:
        tid = entry["tweet_id"]
        if tid not in tweet_map:
            tweet_map[tid] = []
        tweet_map[tid].append(entry)
    
    print(f"Unique tweet IDs: {len(tweet_map)}", flush=True)
    
    # Load existing recovered tweets
    recovered = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        existing_blocks = re.findall(r'### Tweet (\d+) — ([^\n]+)\n(.*?)(?=\n---\n|\n### Tweet|\Z)', content, re.DOTALL)
        for block in existing_blocks:
            tid = block[0]
            text = block[2].strip()
            recovered[tid] = text
        print(f"Already recovered {len(recovered)} tweets from previous run", flush=True)
    
    # Find new tweets to fetch
    new_tweets = {tid: snaps for tid, snaps in tweet_map.items() if tid not in recovered}
    print(f"New tweets to fetch: {len(new_tweets)}", flush=True)
    
    if not new_tweets:
        print("All tweets already recovered!", flush=True)
        return
    
    total = len(tweet_map)
    done = len(recovered)
    new_total = len(new_tweets)
    new_done = 0
    
    for i, (tweet_id, snapshots) in enumerate(sorted(new_tweets.items())):
        snapshots.sort(key=lambda x: x["timestamp"])
        
        text_found = None
        for snap in snapshots:
            timestamp = snap["timestamp"]
            original = snap["original"]
            url = f"https://web.archive.org/web/{timestamp}if_/{original}"
            
            print(f"[{new_done+1}/{new_total}] Fetching tweet {tweet_id} (ts={timestamp})...", flush=True)
            html = fetch_page(url)
            
            if html:
                text_found = extract_text_v2(html)
                if not text_found or len(text_found) < 10:
                    text_found = extract_text_v3(html)
                if text_found and len(text_found) > 5:
                    break
            
            time.sleep(2)
        
        if text_found:
            recovered[tweet_id] = text_found
            safe_preview = text_found[:80].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            print(f"    ✓ Recovered: {safe_preview}...", flush=True)
        else:
            print(f"    ✗ Failed to extract text for tweet {tweet_id}", flush=True)
            recovered[tweet_id] = f"[Extraction failed - tweet ID {tweet_id}]"
        
        done += 1
        new_done += 1
        
        # Write progress every 10 tweets
        if new_done % 10 == 0 or new_done == new_total:
            print(f"  Writing progress ({done}/{total})...", flush=True)
            with open(OUTPUT_FILE, "w", encoding="utf-8", errors="replace") as f:
                f.write(f"# @EVEZ666 Tweet Archive — Recovered from Wayback Machine\n\n")
                success_count = len([t for t in recovered.values() if not t.startswith('[Extraction failed')])
                f.write(f"Recovered {success_count} of {total} tweets\n\n")
                f.write(f"---\n\n")
                for tid in sorted(recovered.keys()):
                    text = recovered[tid]
                    date_str = "unknown"
                    if tid in tweet_map:
                        date_str = format_date(tweet_map[tid][0]["timestamp"])
                    f.write(f"### Tweet {tid} — {date_str}\n")
                    f.write(f"{text}\n")
                    f.write(f"\n---\n\n")
        
        time.sleep(2)
    
    success_count = len([t for t in recovered.values() if not t.startswith('[Extraction failed')])
    print(f"\nDone! Total recovered: {success_count} tweets out of {total}", flush=True)

if __name__ == "__main__":
    main()
