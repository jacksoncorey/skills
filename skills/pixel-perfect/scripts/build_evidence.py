#!/usr/bin/env python3
"""
Build the pixel-parity evidence page (a single self-contained HTML file) from a
manifest. This is the deliverable the reviewer sees: before / Figma / after /
heatmap per screen, measured geometry with per-axis deltas, the accepted
exceptions, and a hunk-by-hunk self-audit. Publish it wherever your team
reviews work and link it from the PR body and the ticket(s) it closes.

    python build_evidence.py --manifest evidence.json --out evidence.html

Manifest shape (see references/evidence-page.md for the rationale):
{
  "title": "Onboarding Reskin",                    # product-style name, no explainer
  "eyebrow": "pixel-perfect evidence · onboarding — second user",
  "headline": "Nine onboarding screens, rebuilt to the approved frames",
  "lede": "…one paragraph: scope, frame size, how it was verified…",
  "tiles": [["Screens","9","S18–S26, 4 stacked PRs"], ["Match @ 2x","98.9–99.3%","…"], …],   # 2–4
  "method": ["…bullet…", …],
  "changes": ["…bullet…", …],
  "exceptions": ["…bullet — each one named AND justified…", …],
  "screens": [
    {"id":"S19","title":"Request to join org","node":"459:58487","figma_url":"https://…",
     "tickets":"TICKET-150 · TICKET-156–160","pr":"PR #459",
     "match":{"1x":99.11,"2x":99.24},
     "images":{"before":"path.png","figma":"path.png","after":"path.png","heatmap":"path.png"},
     "expected":{"Headline":[515,200,482,76.8],"Org card":[509,368,494,80]},   # Figma coords, null = don't compare
     "measured":{"Headline":[515,200,482,76.8],"Org card":[509,368.4,494,80]}}  # from measure_geometry.js
  ],
  "audit": [["file","what changed","traces to"], …],
  "out_of_scope": "…one paragraph…"
}
"""
import argparse, base64, html, io, json
from PIL import Image

CSS = """
:root{--bg:#f4f5f7;--panel:#ffffff;--ink:#15171b;--muted:#646a74;--hair:#dfe2e7;--accent:#2857c9;--ok:#1d7a4b;--warn:#a06a00;--bad:#b83228;--okbg:#e3f3ea;--warnbg:#f7edd6;--badbg:#f8e3e0;--mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;--sans:"IBM Plex Sans",-apple-system,"Segoe UI",sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121417;--panel:#1b1e23;--ink:#eceef1;--muted:#9aa1ab;--hair:#2b3038;--accent:#84a4ee;--ok:#7fcc9d;--warn:#d9ad4f;--bad:#e78b82;--okbg:#1d2f25;--warnbg:#332c19;--badbg:#3a2321}}
:root[data-theme=dark]{--bg:#121417;--panel:#1b1e23;--ink:#eceef1;--muted:#9aa1ab;--hair:#2b3038;--accent:#84a4ee;--ok:#7fcc9d;--warn:#d9ad4f;--bad:#e78b82;--okbg:#1d2f25;--warnbg:#332c19;--badbg:#3a2321}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--sans);padding:40px 28px 96px}
main{max-width:1180px;margin:0 auto}
.eyebrow{font:500 11px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}
h1{font-weight:600;font-size:28px;letter-spacing:-.4px;margin:12px 0 8px;text-wrap:balance}
h2{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:48px 0 12px}
h3{font-size:18px;font-weight:600;margin:0;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
p{max-width:72ch}.lede{color:var(--muted);font-size:15px}
.sid{font:600 12px var(--mono);color:var(--muted);background:var(--panel);border:1px solid var(--hair);border-radius:6px;padding:2px 8px}
.meta{font:12.5px var(--mono);color:var(--muted)}.meta a{color:var(--accent);text-decoration:none}.meta a:hover{text-decoration:underline}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
th{text-align:left;font-weight:600;color:var(--muted);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;padding:8px 10px;border-bottom:1px solid var(--hair)}
td{padding:8px 10px;border-bottom:1px solid var(--hair);vertical-align:top}td.num,th.num{font-family:var(--mono);font-size:12.5px;white-space:nowrap}
.ok,.warn,.bad{font-family:var(--mono);font-size:11.5px;padding:1px 6px;border-radius:4px;margin-left:4px}
.ok{color:var(--ok);background:var(--okbg)}.warn{color:var(--warn);background:var(--warnbg)}.bad{color:var(--bad);background:var(--badbg)}
.screen{background:var(--panel);border:1px solid var(--hair);border-radius:10px;padding:20px 22px 22px;margin:18px 0}
.strip{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0 18px}.strip figure{margin:0}
.strip img{width:100%;display:block;border:1px solid var(--hair);border-radius:6px;background:#fff}
.strip figcaption{font:500 11px/1.3 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:8px}
.summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0 6px}
.tile{background:var(--panel);border:1px solid var(--hair);border-radius:10px;padding:14px 16px}
.tile .k{font:500 11px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.tile .v{font-size:22px;font-weight:600;margin-top:8px;font-variant-numeric:tabular-nums}.tile .s{font-size:12.5px;color:var(--muted);margin-top:4px}
.wrap{overflow-x:auto}ul{padding-left:20px}li{margin:6px 0;max-width:80ch}
code{font:12.5px var(--mono);background:var(--bg);border:1px solid var(--hair);border-radius:4px;padding:1px 5px}
@media (max-width:900px){.strip{grid-template-columns:repeat(2,1fr)}.summary{grid-template-columns:repeat(2,1fr)}}
"""

def b64(path, width=1000, quality=78):
    im = Image.open(path).convert("RGB")
    r = width / im.width
    im = im.resize((width, round(im.height * r)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def strip(s):
    caps = {"before": "Before · dev", "figma": f"Approved · Figma {s.get('node','')}", "after": "After · this branch", "heatmap": "Diff heatmap · red = differs"}
    figs = []
    for k in ("before", "figma", "after", "heatmap"):
        p = s["images"].get(k)
        if p: figs.append(f'<figure><img src="{b64(p)}" alt="{html.escape(caps[k])}"><figcaption>{html.escape(caps[k])}</figcaption></figure>')
    return f'<div class="strip">{"".join(figs)}</div>'

def parity(s):
    exp, mea = s.get("expected", {}), s.get("measured", {})
    if not exp: return ""
    rows = []
    for name, e in exp.items():
        m = mea.get(name)
        if not m: rows.append(f"<tr><td>{html.escape(name)}</td><td class='num' colspan='4'>— not measured</td></tr>"); continue
        cells = []
        for ev, mv in zip(e, m):
            if ev is None: cells.append(f"{mv:g}")
            else:
                d = mv - ev; cls = "ok" if abs(d) <= 1 else ("warn" if abs(d) <= 2 else "bad")
                cells.append(f'{ev:g} → {mv:g} <span class="{cls}">{d:+.1f}</span>')
        rows.append(f"<tr><td>{html.escape(name)}</td>" + "".join(f"<td class='num'>{c}</td>" for c in cells) + "</tr>")
    return f'<div class="wrap"><table><thead><tr><th>Element</th><th class="num">x (Figma → built)</th><th class="num">y</th><th class="num">w</th><th class="num">h</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

def li(items): return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); m = json.load(open(a.manifest))
    tiles = "".join(f'<div class="tile"><div class="k">{html.escape(k)}</div><div class="v">{html.escape(v)}</div><div class="s">{html.escape(s)}</div></div>' for k, v, s in m.get("tiles", []))
    screens = []
    for s in m["screens"]:
        mt = s.get("match", {}); match = " · ".join(f"match {k} {v}%" for k, v in mt.items())
        link = f'<a href="{s["figma_url"]}">{s.get("node","frame")}</a>' if s.get("figma_url") else s.get("node", "")
        screens.append(f'''<section class="screen" id="{s["id"]}"><h3><span class="sid">{s["id"]}</span>{html.escape(s["title"])}</h3>
<div class="meta">Figma {link} · {html.escape(s.get("tickets",""))} · {html.escape(s.get("pr",""))} · {match}</div>{strip(s)}{parity(s)}</section>''')
    audit = "".join(f"<tr><td><code>{html.escape(f)}</code></td><td>{w}</td><td>{t}</td></tr>" for f, w, t in m.get("audit", []))
    page = f'''<title>{html.escape(m["title"])}</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>
<main>
<div class="eyebrow">{html.escape(m.get("eyebrow",""))}</div>
<h1>{html.escape(m.get("headline", m["title"]))}</h1>
<p class="lede">{m.get("lede","")}</p>
<div class="summary">{tiles}</div>
<h2>Method</h2>{li(m.get("method", []))}
<h2>What was wrong, what changed</h2>{li(m.get("changes", []))}
<h2>Accepted exceptions</h2>{li(m.get("exceptions", []))}
<h2>Per-screen evidence</h2>{"".join(screens)}
<h2>Diff self-audit</h2><div class="wrap"><table><thead><tr><th>File</th><th>What changed</th><th>Traces to</th></tr></thead><tbody>{audit}</tbody></table></div>
{('<p class="lede" style="margin-top:28px">' + m["out_of_scope"] + '</p>') if m.get("out_of_scope") else ""}
</main>'''
    open(a.out, "w").write(page)
    print(f"wrote {a.out} ({len(page)//1024} KB)")

if __name__ == "__main__":
    main()
