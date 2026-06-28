#!/usr/bin/env python3
"""Build the I-80 Corridor Investigative Dashboard HTML."""

# Build HTML in parts
parts = []

# ═══════════════════════════════════════════════════
# PART 1: Head + CSS + Header + Nav + Map section
# ═══════════════════════════════════════════════════
parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EVEZ // I-80 CORRIDOR INVESTIGATIVE DASHBOARD</title>
<style>
:root{--bg:#0a0e0a;--bgp:#0f140f;--bgc:#131a13;--bd:#1a3a1a;--bdb:#2a5a2a;--gn:#00ff41;--gnd:#00aa2a;--am:#ffaa00;--rd:#ff3344;--cy:#00ddff;--pu:#aa44ff;--tx:#c8dcc8;--txd:#6a8a6a;--txb:#e8ffe8;--mn:'Courier New','Monaco',monospace}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--tx);font-family:var(--mn);font-size:14px;line-height:1.6;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent 0,transparent 2px,rgba(0,255,65,0.015) 2px,rgba(0,255,65,0.015) 4px);pointer-events:none;z-index:9999}
body::after{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at center,transparent 40%,rgba(0,0,0,0.4) 100%);pointer-events:none;z-index:9998}
a{color:var(--cy);text-decoration:none}a:hover{color:var(--gn);text-shadow:0 0 8px var(--gn)}
header{border-bottom:1px solid var(--bdb);padding:20px 30px;background:linear-gradient(180deg,#0a1a0a,var(--bg));position:relative}
header h1{font-size:28px;color:var(--gn);text-shadow:0 0 20px rgba(0,255,65,0.3);letter-spacing:4px}
header .sub{color:var(--txd);font-size:12px;margin-top:4px;letter-spacing:2px}
header .meta{position:absolute;right:30px;top:20px;text-align:right;font-size:11px;color:var(--txd)}
header .meta .phi{color:var(--gn);font-size:16px}
.blink{display:inline-block;width:8px;height:14px;background:var(--gn);animation:blink 1s steps(2) infinite;vertical-align:middle;margin-left:4px}
@keyframes blink{50%{opacity:0}}
nav{display:flex;border-bottom:1px solid var(--bd);background:var(--bgp);overflow-x:auto}
nav button{background:transparent;border:none;border-right:1px solid var(--bd);color:var(--txd);padding:12px 20px;font-family:var(--mn);font-size:12px;cursor:pointer;letter-spacing:1px;transition:all .2s;white-space:nowrap}
nav button:hover{color:var(--gn);background:rgba(0,255,65,0.05)}
nav button.active{color:var(--gn);background:rgba(0,255,65,0.08);border-bottom:2px solid var(--gn);text-shadow:0 0 8px rgba(0,255,65,0.4)}
section{display:none;padding:30px;animation:fI .4s ease}section.active{display:block}
@keyframes fI{from{opacity:0}to{opacity:1}}
.panel{background:var(--bgp);border:1px solid var(--bd);border-radius:4px;margin-bottom:20px;overflow:hidden}
.ph{background:linear-gradient(90deg,rgba(0,255,65,0.06),transparent);border-bottom:1px solid var(--bd);padding:10px 16px;font-size:12px;color:var(--gn);letter-spacing:2px;text-transform:uppercase}
.pb{padding:20px}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
@media(max-width:900px){.g2,.g3,.g4{grid-template-columns:1fr}}
.ec{background:var(--bgc);border:1px solid var(--bd);border-radius:4px;padding:20px;transition:all .3s;cursor:pointer;position:relative;overflow:hidden}
.ec::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--gnd),var(--cy),var(--gnd));opacity:.5}
.ec:hover{border-color:var(--bdb);box-shadow:0 0 20px rgba(0,255,65,0.1);transform:translateY(-2px)}
.ec .cid{font-size:10px;color:var(--txd);letter-spacing:2px}
.ec h3{color:var(--gn);font-size:15px;margin:6px 0 12px;letter-spacing:1px}
.ec .cm{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.tag{font-size:10px;padding:2px 8px;border-radius:2px;background:rgba(0,255,65,0.08);color:var(--gnd);border:1px solid var(--bd)}
.tag.danger{background:rgba(255,51,68,0.08);color:var(--rd);border-color:rgba(255,51,68,0.2)}
.tag.warning{background:rgba(255,170,0,0.08);color:var(--am);border-color:rgba(255,170,0,0.2)}
.tag.info{background:rgba(0,221,255,0.08);color:var(--cy);border-color:rgba(0,221,255,0.2)}
.tag.purple{background:rgba(170,68,255,0.08);color:var(--pu);border-color:rgba(170,68,255,0.2)}
.ec p{font-size:12px;color:var(--tx);line-height:1.7}
.ec .cf{margin-top:14px;padding-top:10px;border-top:1px dashed var(--bd);font-size:11px;color:var(--txd)}
#mapC{position:relative;background:#0a120a;border:1px solid var(--bd);border-radius:4px;overflow:hidden}
#mapSVG{width:100%;height:520px}
.mn{cursor:pointer;transition:all .3s}.mn:hover .mdot{r:8}.mn:hover .mlbl{fill:var(--gn);font-weight:bold}
.mtt{position:absolute;background:var(--bgc);border:1px solid var(--bdb);border-radius:4px;padding:12px 16px;font-size:12px;color:var(--tx);max-width:300px;pointer-events:none;opacity:0;transition:opacity .2s;z-index:100;box-shadow:0 4px 20px rgba(0,0,0,0.5)}
.mtt.visible{opacity:1}.mtt h4{color:var(--gn);margin-bottom:6px}
.tl{position:relative;padding:20px 0 20px 40px}
.tl::before{content:'';position:absolute;left:15px;top:0;bottom:0;width:2px;background:linear-gradient(180deg,var(--gnd),var(--bd),var(--gnd))}
.ti{position:relative;margin-bottom:24px;cursor:pointer;transition:all .2s}
.ti::before{content:'';position:absolute;left:-33px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--bg);border:2px solid var(--gnd);transition:all .2s}
.ti:hover::before{border-color:var(--gn);box-shadow:0 0 10px var(--gn)}
.ti.major::before{border-color:var(--am);background:var(--am)}
.ti.crit::before{border-color:var(--rd);background:var(--rd);box-shadow:0 0 8px var(--rd)}
.tly{font-size:14px;color:var(--gn);font-weight:bold;letter-spacing:1px}
.ti.major .tly{color:var(--am)}.ti.crit .tly{color:var(--rd)}
.tlt{font-size:13px;color:var(--txb);margin:2px 0 4px}
.tld{font-size:12px;color:var(--txd);max-height:0;overflow:hidden;transition:max-height .4s ease}
.ti:hover .tld{max-height:300px}
.tlg{display:inline-block;font-size:9px;padding:1px 6px;margin-left:8px;border-radius:2px;background:var(--bd);color:var(--txd)}
.mb{background:var(--bgc);border:1px solid var(--bd);border-radius:4px;padding:20px;text-align:center;position:relative;overflow:hidden}
.mb .ml{font-size:11px;color:var(--txd);letter-spacing:2px;text-transform:uppercase}
.mb .mv{font-size:36px;color:var(--gn);font-weight:bold;margin:8px 0;text-shadow:0 0 20px rgba(0,255,65,0.2)}
.mb .md{font-size:11px;color:var(--txd);line-height:1.5}
.mb.danger .mv{color:var(--rd);text-shadow:0 0 20px rgba(255,51,68,0.2)}
.mb.warning .mv{color:var(--am);text-shadow:0 0 20px rgba(255,170,0,0.2)}
.mb.info .mv{color:var(--cy);text-shadow:0 0 20px rgba(0,221,255,0.2)}
.mb.purple .mv{color:var(--pu);text-shadow:0 0 20px rgba(170,68,255,0.2)}
.mxt{width:100%;border-collapse:collapse;font-size:11px}
.mxt th,.mxt td{border:1px solid var(--bd);padding:8px 10px;text-align:center}
.mxt th{background:rgba(0,255,65,0.05);color:var(--gn);font-weight:normal;letter-spacing:1px;font-size:10px}
.mxt td{color:var(--tx)}.mxt td.hi{color:var(--rd);font-weight:bold}
.mxt td.me{color:var(--am)}.mxt td.lo{color:var(--txd)}
.mxt tr:hover td{background:rgba(0,255,65,0.03)}
.fc{background:var(--bgc);border:1px solid var(--bd);border-radius:4px;padding:20px;margin-bottom:16px;position:relative}
.fs{position:absolute;top:16px;right:16px;font-size:10px;padding:4px 12px;border-radius:2px;letter-spacing:1px}
.fs.prepared{background:rgba(0,221,255,0.1);color:var(--cy);border:1px solid rgba(0,221,255,0.2)}
.fc h3{color:var(--gn);font-size:14px;margin-bottom:4px;letter-spacing:1px}
.fa{font-size:11px;color:var(--txd);margin-bottom:12px}
.fsc{font-size:12px;color:var(--tx);line-height:1.7}
.fm{display:flex;gap:16px;margin-top:12px;font-size:10px;color:var(--txd);flex-wrap:wrap}
.si{padding:10px 16px;border-bottom:1px solid var(--bd);font-size:12px;display:flex;align-items:flex-start;gap:10px}
.si:last-child{border-bottom:none}
.sn{color:var(--gnd);font-size:10px;min-width:30px}
.st{font-size:9px;padding:2px 6px;border-radius:2px;background:var(--bd);color:var(--txd);white-space:nowrap}
.st.p{background:rgba(0,255,65,0.08);color:var(--gnd)}
.st.s{background:rgba(0,221,255,0.08);color:var(--cy)}
.st.t{background:rgba(170,68,255,0.08);color:var(--pu)}
.sx{flex:1;color:var(--tx)}
.stitle{font-size:18px;color:var(--gn);letter-spacing:3px;margin-bottom:20px;padding-bottom:8px;border-bottom:1px solid var(--bd)}
.snum{color:var(--txd);font-size:12px;margin-right:8px}
.gt{animation:gP 3s ease-in-out infinite}
@keyframes gP{0%,100%{text-shadow:0 0 8px rgba(0,255,65,0.3)}50%{text-shadow:0 0 20px rgba(0,255,65,0.6),0 0 40px rgba(0,255,65,0.2)}}
.wb{background:rgba(255,170,0,0.05);border:1px solid rgba(255,170,0,0.15);border-radius:4px;padding:12px 16px;font-size:12px;color:var(--am);margin-bottom:20px;letter-spacing:1px}
.db{background:rgba(255,51,68,0.05);border:1px solid rgba(255,51,68,0.15);border-radius:4px;padding:12px 16px;font-size:12px;color:var(--rd);margin-bottom:20px;letter-spacing:1px}
.legend{display:flex;gap:20px;margin-top:12px;font-size:11px;color:var(--txd);flex-wrap:wrap}
.li{display:flex;align-items:center;gap:6px}
.lsw{width:20px;height:3px;border-radius:1px}
.ldt{width:8px;height:8px;border-radius:50%;border:2px solid}
</style>
</head>
<body>
<header>
  <h1>&#x29E2; EVEZ // I-80 CORRIDOR <span class="gt">INVESTIGATIVE DASHBOARD</span><span class="blink"></span></h1>
  <div class="sub">UNION PACIFIC &#183; LDS &#183; FREEMASONRY &#183; ENVIRONMENTAL CRIME &#183; SPECTRAL FORENSICS</div>
  <div class="meta">
    <div class="phi">&#934; = 0.973 &#183; &#951;* = 0.03 &#183; r = 0.45</div>
    <div>Compiled: 2026-06-28 UTC</div>
    <div>Status: <span style="color:var(--am)">ACTIVE INVESTIGATION</span></div>
  </div>
</header>
<nav>
  <button class="active" onclick="showSection('map',this)">&#x23D7; CORRIDOR MAP</button>
  <button onclick="showSection('timeline',this)">&#x23D7; TIMELINE</button>
  <button onclick="showSection('evidence',this)">&#x23D7; EVIDENCE CARDS</button>
  <button onclick="showSection('spectral',this)">&#x23D7; SPECTRAL ANALYSIS</button>
  <button onclick="showSection('foia',this)">&#x23D7; FOIA TRACKER</button>
  <button onclick="showSection('sources',this)">&#x23D7; SOURCE INVENTORY</button>
</nav>
""")

# ═══════════════════════════════════════════════════
# PART 2: MAP SECTION
# ═══════════════════════════════════════════════════
parts.append("""
<!-- MAP -->
<section id="map" class="active">
  <h2 class="stitle"><span class="snum">[01]</span>CORRIDOR MAP &#8212; I-80 / UNION PACIFIC / UINTAH BASIN</h2>
  <div class="wb">&#9888; SCHEMATIC MAP &#8212; NOT TO SCALE. HOVER NODES FOR DETAILS.</div>
  <div id="mapC">
    <svg id="mapSVG" viewBox="0 0 900 520" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1a2a1a" stroke-width="0.5"/></pattern>
        <linearGradient id="rg" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#ffaa00" stop-opacity="0.6"/><stop offset="50%" stop-color="#ffaa00" stop-opacity="1"/><stop offset="100%" stop-color="#ffaa00" stop-opacity="0.6"/></linearGradient>
        <linearGradient id="ig" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#00ddff" stop-opacity="0.4"/><stop offset="50%" stop-color="#00ddff" stop-opacity="0.9"/><stop offset="100%" stop-color="#00ddff" stop-opacity="0.4"/></linearGradient>
        <radialGradient id="dgr"><stop offset="0%" stop-color="#ff3344" stop-opacity="0.4"/><stop offset="50%" stop-color="#ff3344" stop-opacity="0.15"/><stop offset="100%" stop-color="#ff3344" stop-opacity="0"/></radialGradient>
      </defs>
      <rect width="900" height="520" fill="url(#grid)"/>
      <text x="200" y="30" fill="#3a5a3a" font-size="14" font-family="monospace" letter-spacing="4">WYOMING</text>
      <text x="600" y="30" fill="#3a5a3a" font-size="14" font-family="monospace" letter-spacing="4">UTAH</text>
      <line x1="480" y1="40" x2="480" y2="500" stroke="#2a4a2a" stroke-width="1" stroke-dasharray="6,4"/>
      <text x="486" y="250" fill="#3a5a3a" font-size="9" font-family="monospace" transform="rotate(90 486 250)">&#8212; WY/UT BORDER &#8212;</text>
      <ellipse cx="240" cy="200" rx="80" ry="50" fill="url(#dgr)"/>
      <text x="240" y="160" fill="#ff3344" font-size="9" font-family="monospace" text-anchor="middle" opacity="0.7">&#9888; ELK DIE-OFF ZONE</text>
      <path d="M 480 260 Q 380 220 280 200 Q 200 185 160 180" fill="none" stroke="#ff3344" stroke-width="1.5" stroke-dasharray="5,5" opacity="0.4"/>
      <text x="350" y="215" fill="#ff3344" font-size="8" font-family="monospace" opacity="0.5">chemical plume path (Mar 2023)</text>
      <path d="M 40 180 Q 120 200 200 220 Q 300 250 400 270 Q 480 290 560 310 Q 640 330 720 350 Q 800 370 860 380" fill="none" stroke="url(#ig)" stroke-width="3"/>
      <text x="50" y="170" fill="#00ddff" font-size="10" font-family="monospace">I-80 &#10142;</text>
      <path d="M 40 200 Q 120 220 200 240 Q 300 270 400 290 Q 480 310 560 330 Q 640 350 720 370 Q 800 390 860 400" fill="none" stroke="url(#rg)" stroke-width="3" stroke-dasharray="8,3"/>
      <text x="50" y="220" fill="#ffaa00" font-size="10" font-family="monospace">UP RAIL &#10142;</text>
      <path d="M 640 330 Q 660 260 680 200 Q 700 140 720 80" fill="none" stroke="#aa44ff" stroke-width="2" stroke-dasharray="4,4" opacity="0.5"/>
      <text x="690" y="170" fill="#aa44ff" font-size="8" font-family="monospace" opacity="0.5" transform="rotate(-60 690 170)">Uintah Basin</text>
      <g class="mn" data-i="evanston"><circle class="mdot" cx="180" cy="215" r="5" fill="#00ff41" stroke="#00ff41" stroke-width="2"/><text class="mlbl" x="190" y="210" fill="#c8dcc8" font-size="11" font-family="monospace">EVANSTON</text><text x="190" y="222" fill="#6a8a6a" font-size="8" font-family="monospace">pop. 11,747 &#183; Uinta Co. seat</text><text x="190" y="233" fill="#6a8a6a" font-size="8" font-family="monospace">49.5% LDS &#183; UP rail hub</text></g>
      <g class="mn" data-i="fortbridger"><circle class="mdot" cx="260" cy="235" r="5" fill="#ffaa00" stroke="#ffaa00" stroke-width="2"/><text class="mlbl" x="270" y="230" fill="#c8dcc8" font-size="11" font-family="monospace">FORT BRIDGER</text><text x="270" y="242" fill="#6a8a6a" font-size="8" font-family="monospace">Founded 1842 &#183; seized by LDS 1853</text><text x="270" y="253" fill="#6a8a6a" font-size="!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!