"""Build the review snapshot from sitemap.md and flows.md (Python standard library)."""

import argparse
import hashlib
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def inline(text):
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)


def cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def markdown(text, source="flows.md"):
    """Render the small Markdown subset used in the source explanations."""
    lines = text.strip().splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("|"):
            table = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table.append(cells(lines[i]))
                i += 1
            out.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Таблиця пояснень"><table>')
            out.append("<thead><tr>" + "".join(f'<th scope="col">{inline(c)}</th>' for c in table[0]) + "</tr></thead><tbody>")
            for row in table[2:]:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            out.append("</tbody></table></div>")
            continue
        if line.startswith("- "):
            out.append("<ul>")
            while i < len(lines) and lines[i].strip().startswith("- "):
                out.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("</ul>")
            continue
        if line.startswith("> "):
            out.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        elif line.startswith("#"):
            out.append(f"<h3>{inline(line.lstrip('# '))}</h3>")
        else:
            paragraph = [line]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"[|#>]|- ", lines[i + 1].strip()):
                i += 1
                paragraph.append(lines[i].strip())
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
        i += 1
    return "\n".join(out).replace('href="#', f'href="{source}#')


CSS = """
:root{color-scheme:dark;--bg:#0d151b;--panel:#14212a;--line:#2a3b44;--text:#e9f0ed;--muted:#aabbbd;--accent:#9fe4ce;--warm:#edc48a;--error:#ffb9b2;--repo-nav-width:240px}
*{box-sizing:border-box}html{scroll-padding-top:24px;scrollbar-color:#526b73 var(--bg)}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,sans-serif}::selection{background:#365d55;color:#fff}a{color:var(--accent);text-underline-offset:4px}a:hover{color:#c7f7e8}button,a,summary{touch-action:manipulation}:focus-visible{outline:2px solid var(--warm);outline-offset:4px}button{font:inherit;cursor:pointer;color:var(--text);background:#1b2c36;border:1px solid #4a6069;border-radius:6px;padding:8px 13px;min-height:44px}button:hover:not(:disabled){background:#2a414d}button:disabled{opacity:.45;cursor:default}button:focus-visible{outline-offset:2px}code{font: .88em/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}p,li{overflow-wrap:break-word}h1,h2,h3,h4{line-height:1.18;text-wrap:balance}h1{font-size:clamp(2.3rem,4.5vw,4.5rem);letter-spacing:-.035em;max-width:16ch;margin:0 0 24px;font-weight:650}h2{font-size:clamp(1.7rem,3vw,2.5rem);letter-spacing:-.025em;margin:0 0 18px;font-weight:620}h3{font-size:clamp(1.3rem,2vw,1.65rem);letter-spacing:-.015em;margin:0 0 20px}h4{font-size:1.1rem;margin:28px 0 12px}p{margin:0 0 16px}li+li{margin-top:8px}.muted,.note{color:var(--muted)}.note{font-size:.9rem}.measure{max-width:72ch}.page{max-width:1540px;padding:64px clamp(24px,4vw,64px) 48px;margin:auto;min-width:0}.page>section{padding-top:68px;margin-top:60px;border-top:1px solid var(--line);min-width:0}header .lead{font-size:1.12rem;max-width:65ch;color:var(--muted)}.source-links{display:flex;gap:12px 24px;flex-wrap:wrap;margin-top:24px;font-size:.92rem}.jump-links{display:flex;gap:8px 28px;flex-wrap:wrap;margin-top:32px;padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.jump-links a{padding:6px 0}.skip-link{position:fixed;left:16px;top:-90px;z-index:50;background:var(--panel);padding:12px}.skip-link:focus{top:12px}
#repo-nav{background:#101c24;color:var(--text);border-color:var(--line)}#repo-nav .repo-nav-branch{color:var(--muted)}#repo-nav a{color:var(--muted)}#repo-nav a:hover,#repo-nav a:focus-visible{background:#21333d;color:var(--text)}#repo-nav a[aria-current]{background:#214238;color:#d7f8e9}#repo-nav .repo-nav-pages .repo-nav-pages{border-color:var(--line)}
.site-tree,.site-tree ul{list-style:none;padding:0;margin:0}.site-tree{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px;margin:36px 0}.group-name{font-size:1.05rem;font-weight:650;display:block;margin-bottom:20px}.site-tree ul{border-left:1px solid #49616a;padding-left:18px;margin-left:4px}.site-tree ul>li{position:relative;margin-top:24px}.site-tree ul>li:before{content:"";position:absolute;top:16px;left:-19px;width:13px;border-top:1px solid #49616a}.screen-name{display:block;font-size:1rem;line-height:1.45;font-weight:600;margin:0 0 8px}.screen-file{display:block;color:var(--muted);margin-bottom:8px}.job-tags{display:flex;gap:6px;flex-wrap:wrap}.job-tags a{font-size:.78rem;text-decoration:none;background:#1b3535;color:#bdeddd;padding:2px 7px;border-radius:3px}.job-tags a:hover{background:#2f5149}.screen-type{display:block;font-size:.8rem;color:var(--muted);margin-top:9px}.connections{font-size:.9rem;color:var(--muted);max-width:80ch}
details{margin-top:20px}summary{cursor:pointer;color:var(--accent);padding:12px 0;line-height:1.5}details[open]>summary{margin-bottom:12px}.prose{max-width:75ch}.prose .table-scroll{max-width:100%}.prose>ul{padding-left:22px}.prose blockquote{margin:0 0 24px;padding:0 0 0 20px;border-left:1px solid var(--accent);color:#cbdcd8;font-size:1.05rem}.flow-index{display:flex;flex-wrap:wrap;gap:8px 22px;margin:24px 0 40px}.flow-index a{padding:5px 0}.flow{margin-top:52px;padding-top:44px;border-top:1px solid var(--line);min-width:0;scroll-margin-top:30px}.flow:first-of-type{margin-top:0}.job-id{color:var(--accent);font-weight:500;display:inline-block;margin-right:10px}.diagram{margin-top:24px;background:#101b22;border:1px solid var(--line);border-radius:8px;overflow:hidden}.diagram-toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:12px;border-bottom:1px solid var(--line);background:var(--panel)}.zoom-value{font-size:.85rem;color:var(--muted);min-width:48px;text-align:center;font-variant-numeric:tabular-nums}.diagram-hint{padding:10px 16px 0;font-size:.8rem;color:var(--muted);margin:0}.diagram-viewport{overflow:auto;height:560px;max-height:65vh;overscroll-behavior:contain;scrollbar-gutter:stable;position:relative}.diagram-canvas{width:max-content;min-width:100%;padding:20px}.diagram-canvas svg{display:block;max-width:none!important;height:auto}.render-status{color:var(--muted);padding:32px 20px}.render-status.error{color:var(--error)}.render-status button{display:block;margin-top:16px}.diagram:fullscreen{display:flex;flex-direction:column;width:100%;height:100%;border:0;border-radius:0}.diagram:fullscreen .diagram-viewport{flex:1;max-height:none;height:auto}.diagram-source{white-space:pre;overflow:auto;max-height:360px;padding:20px;border:1px solid var(--line);background:var(--panel);font-size:.8rem;line-height:1.65;margin:0}.diagram-source code{font-size:inherit;overflow-wrap:normal}.diagram-note{margin-top:10px}.flow-explanation{margin-top:14px}.flow-explanation summary{font-weight:550}
.table-scroll{overflow:auto;scrollbar-gutter:stable;border:1px solid var(--line);border-radius:8px;margin:24px 0}table{border-collapse:collapse;width:100%;font-size:.9rem;line-height:1.5}th,td{text-align:left;vertical-align:top;padding:16px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}th:last-child,td:last-child{border-right:0}tbody tr:last-child>*{border-bottom:0}thead th{background:#1b2c36;font-weight:550}tbody th{font-weight:500;background:#101b22}td{color:#cedbd7}#trace-table{min-width:870px;table-layout:fixed}#trace-table th:first-child{width:29%}#trace-table thead a{color:var(--text);text-decoration:none}#trace-table thead code{display:block;color:var(--muted);font-size:.78rem;margin-top:8px}#trace-table td{text-align:center;vertical-align:middle;font:600 1.05rem/1.5 system-ui;color:var(--accent);font-variant-numeric:tabular-nums}#trace-table tbody tr:hover>*{background:#182b32}.orphan-row>*,#trace-table .orphan-col{background:#40272a!important;color:var(--error)!important}.orphan-label{display:block;color:var(--error);font:500 .75rem/1.5 system-ui;margin-top:6px}.orphan-summary{padding:18px 0}.orphan-summary strong{color:var(--accent)}.orphan-summary.has-orphans strong{color:var(--error)}.orphan-summary p{margin:0}.trace-notes{margin-top:18px}footer{margin-top:68px;padding-top:24px;border-top:1px solid var(--line);font-size:.86rem;color:var(--muted)}
@media(max-width:1100px){.site-tree{grid-template-columns:1fr;gap:30px}.site-tree>li{margin:0}.site-tree ul{margin-left:8px}.site-tree .group-name{margin-bottom:12px}}
@media(max-width:760px){body.repo-has-nav{padding-left:0}#repo-nav{position:static;width:100%;padding:18px 24px;border-right:0;border-bottom:1px solid var(--line);overflow:visible}#repo-nav .repo-nav-heading{margin-bottom:12px}#repo-nav .repo-nav-branches{display:flex;flex-wrap:wrap;gap:16px}#repo-nav .repo-nav-branches>li+li{margin-top:0}#repo-nav .repo-nav-branch{margin-left:0}#repo-nav a{padding:6px 0;font-size:.8rem}#repo-nav .repo-nav-pages{max-width:160px}.page{padding:38px 22px}.page>section{margin-top:42px;padding-top:42px}.flow{margin-top:38px;padding-top:32px}.diagram-toolbar{gap:6px;padding:10px}.diagram-toolbar button{font-size:.8rem;padding:8px 10px}.zoom-value{min-width:36px}.diagram-viewport{height:460px;max-height:65vh}.diagram-canvas{padding:12px}h1{max-width:15ch}.jump-links{gap:8px 18px}.table-scroll{margin-left:0;margin-right:0}}
@media print{body.repo-has-nav{padding-left:0}#repo-nav,.jump-links,.diagram-toolbar,.diagram-hint,.skip-link{display:none}.page{padding:0;max-width:none}.diagram-viewport{height:auto;max-height:none;overflow:visible}.diagram-canvas{width:100%;padding:0}.diagram-canvas svg{width:100%!important;height:auto!important}.table-scroll{overflow:visible}#trace-table{min-width:0;font-size:11px}.flow{break-before:page}details:not([open]){display:none}}
"""

JS = """
const flowElements = [...document.querySelectorAll('.flow')];
let mermaid;
function controls(flow, svg) {
  const wrapper = flow.querySelector('.diagram');
  const viewport = flow.querySelector('.diagram-viewport');
  const box = svg.viewBox.baseVal;
  const original = {width:box.width, height:box.height};
  let scale = 1;
  const buttons = [...flow.querySelectorAll('[data-zoom]')];
  function resize(next, recenter = true) {
    const centerX = (viewport.scrollLeft + viewport.clientWidth/2) / scale;
    const centerY = (viewport.scrollTop + viewport.clientHeight/2) / scale;
    scale = Math.max(.03, Math.min(2, next));
    svg.style.width = `${original.width * scale}px`;
    svg.style.height = `${original.height * scale}px`;
    flow.querySelector('.zoom-value').textContent = `${Math.round(scale*100)}%`;
    flow.querySelector('[data-zoom="out"]').disabled = scale <= .03;
    flow.querySelector('[data-zoom="in"]').disabled = scale >= 2;
    if (recenter) { viewport.scrollLeft = centerX*scale - viewport.clientWidth/2; viewport.scrollTop = centerY*scale - viewport.clientHeight/2; }
  }
  function fit() { resize(Math.min(1, (viewport.clientWidth-44)/original.width), false); viewport.scrollTo(0,0); }
  buttons.forEach(button => {
    button.disabled = false;
    button.addEventListener('click', () => {
      const action = button.dataset.zoom;
      if(action === 'fit') fit();
      else resize(action === 'actual' ? 1 : scale * (action === 'in' ? 1.25 : .8));
    });
  });
  const full = flow.querySelector('[data-fullscreen]');
  if(wrapper.requestFullscreen && document.fullscreenEnabled) {
    full.hidden = false;
    full.disabled = false;
    full.addEventListener('click', async () => {
      try { if(document.fullscreenElement) await document.exitFullscreen(); else await wrapper.requestFullscreen(); }
      catch { full.hidden = true; }
    });
    document.addEventListener('fullscreenchange', () => { full.textContent = document.fullscreenElement === wrapper ? 'Згорнути' : 'На весь екран'; });
  }
  // Keep text readable on first open; center the entry node rather than shrinking the whole graph.
  resize(1, false);
  const entry = svg.querySelector('.node');
  if(entry) {
    const nodeRect = entry.getBoundingClientRect();
    const viewportRect = viewport.getBoundingClientRect();
    viewport.scrollLeft += nodeRect.left - viewportRect.left + nodeRect.width/2 - viewport.clientWidth/2;
    viewport.scrollTop = 0;
  }
}
function showError(flow) {
  const status = flow.querySelector('.render-status');
  status.replaceChildren();
  status.classList.add('error');
  status.setAttribute('role','alert');
  const message = document.createElement('p');
  message.textContent = 'Діаграму не вдалося завантажити. Код доступний нижче; можна повторити завантаження сторінки.';
  const retry = document.createElement('button');
  retry.type = 'button'; retry.textContent = 'Завантажити ще раз';
  retry.addEventListener('click', () => location.reload());
  status.append(message,retry);
}
try {
  mermaid = (await import('https://cdn.jsdelivr.net/npm/mermaid@12.3.0/dist/mermaid.esm.min.mjs')).default;
  mermaid.initialize({startOnLoad:false, theme:'dark', securityLevel:'strict', fontFamily:'system-ui, sans-serif', flowchart:{useMaxWidth:false, htmlLabels:false, nodeSpacing:35, rankSpacing:48}, themeVariables:{darkMode:true, background:'#101b22', primaryColor:'#213d42', primaryTextColor:'#e9f0ed', primaryBorderColor:'#76bba9', lineColor:'#aabbbd', secondaryColor:'#263544', tertiaryColor:'#302e26', edgeLabelBackground:'#14212a', fontSize:'16px'}});
} catch {
  flowElements.forEach(showError);
}
if(mermaid) {
  for(const flow of flowElements) {
    try {
      const source = flow.querySelector('.mermaid-source').textContent;
      const {svg, bindFunctions} = await mermaid.render(`diagram-${flow.id}`, source);
      const canvas = flow.querySelector('.diagram-canvas');
      canvas.innerHTML = svg;
      const rendered = canvas.querySelector('svg');
      rendered.setAttribute('role','img');
      rendered.setAttribute('aria-label', flow.querySelector('h3').textContent.trim());
      if(bindFunctions) bindFunctions(canvas);
      flow.querySelector('.render-status').hidden = true;
      controls(flow, rendered);
      flow.dataset.rendered = 'true';
    } catch { showError(flow); }
  }
}
document.documentElement.dataset.diagramsReady = 'true';
"""


def build():
    sitemap = (ROOT / "sitemap.md").read_text(encoding="utf-8-sig")
    flows = (ROOT / "flows.md").read_text(encoding="utf-8-sig")
    registry = re.search(r"\| група \| екран \| файл \| job \|\n[^\n]+\n((?:\|[^\n]+\n)+)", sitemap)
    if not registry:
        raise ValueError("Screen registry not found")
    screens = []
    for line in registry[1].splitlines():
        group, screen, filename, jobs = cells(line)
        screens.append(dict(group=re.search(r"\*\*(.+?)\*\*", group)[1], name=re.search(r"\*\*(.+?)\*\*", screen)[1], file=re.search(r"`([^`]+)`", filename)[1]))
    trace = sitemap.split("## Трасування", 1)[1]
    matrix = re.search(r"(\| Job із JTBD[^\n]+)\n[^\n]+\n((?:\|[^\n]+\n)+)", trace)
    headers = cells(matrix[1])[1:]
    files = [re.search(r"`([^`]+)`", h)[1] for h in headers]
    if files != [screen["file"] for screen in screens]:
        raise ValueError("Matrix columns must match the screen registry")
    rows = [cells(line) for line in matrix[2].splitlines()]
    if any(len(row) != len(screens)+1 or any(c not in ("", "x") for c in row[1:]) for row in rows):
        raise ValueError("Invalid trace matrix")
    orphan_cols = [not any(row[c+1] == "x" for row in rows) for c in range(len(screens))]
    orphan_rows = [not any(c == "x" for c in row[1:]) for row in rows]
    for index, screen in enumerate(screens):
        screen["jobs"] = [re.search(r"J\d+", row[0])[0] for row in rows if row[index+1] == "x"]
        screen["orphan"] = orphan_cols[index]

    sections = re.split(r"^## ", flows, flags=re.M)
    jobs = []
    intro = []
    ending = []
    for section in sections[1:]:
        heading, _, body = section.partition("\n")
        graph = re.search(r"```mermaid\n(.*?)\n```", body, flags=re.S)
        if graph:
            job = "J0" if heading.startswith("MAIN JOB") else re.match(r"J\d+", heading)[0]
            before, after = body[:graph.start()].strip(), body[graph.end():].strip()
            title = heading.split(" · ", 1)[1]
            jobs.append(dict(id=job, title=title, before=before, after=after, graph=graph[1]))
        elif heading.startswith("Як читати"):
            intro.append(body)
        else:
            ending.append(f"### {heading}\n{body}")
    if [j["id"] for j in jobs] != [re.search(r"J\d+", row[0])[0] for row in rows]:
        raise ValueError("Flows and matrix must contain the same jobs in the same order")

    def screen_node(screen, children=""):
        tags = "".join(f'<a href="#flow-{job}" aria-label="{job}: перейти до flow">{job}</a>' for job in screen["jobs"])
        warning = '<span class="orphan-label">СИРОТА — немає job</span>' if screen["orphan"] else ""
        kind = {"care.html":"Глобальний · головний", "action.html":"Контекстний", "action-edit.html":"Глобальний · створення / редагування", "pet.html":"Глобальний · одна тварина", "pet-edit.html":"Глибокий · створення / редагування"}[screen["file"]]
        return f'<li id="screen-{screen["file"].removesuffix(".html")}"><span class="screen-name">{html.escape(screen["name"])}</span><code class="screen-file">{screen["file"]}</code><div class="job-tags">{tags}</div>{warning}<span class="screen-type">{kind}</span>{children}</li>'

    by_file = {screen["file"]: screen for screen in screens}
    tree = []
    # Navigation parentage comes from «Тип кожного екрана та входи»; shared routes stay cross-links.
    parents = {"Догляд":("care.html","action.html"), "Запис дії":("action-edit.html",), "Тварини":("pet.html","pet-edit.html")}
    for group, members in parents.items():
        child = "<ul>"+screen_node(by_file[members[1]])+"</ul>" if len(members)>1 else ""
        tree.append(f'<li><span class="group-name">{group}</span><ul>{screen_node(by_file[members[0]], child)}</ul></li>')

    table = ['<table id="trace-table"><caption class="sr-only">Пряма участь екранів у закритті jobs ядра MVP</caption><thead><tr><th scope="col">Job із JTBD</th>']
    for screen in screens:
        warning = '<span class="orphan-label">СИРОТА</span>' if screen["orphan"] else ""
        cls = ' class="orphan-col"' if screen["orphan"] else ""
        table.append(f'<th scope="col"{cls}><a href="#screen-{screen["file"].removesuffix(".html")}">{html.escape(screen["name"])}</a><code>{screen["file"]}</code>{warning}</th>')
    table.append("</tr></thead><tbody>")
    for i, row in enumerate(rows):
        job = re.search(r"J\d+", row[0])[0]
        cls = ' class="orphan-row"' if orphan_rows[i] else ""
        warning = '<span class="orphan-label">СИРОТА — немає екрана</span>' if orphan_rows[i] else ""
        table.append(f'<tr{cls}><th scope="row"><a href="#flow-{job}">{inline(row[0])}</a>{warning}</th>')
        for c, value in enumerate(row[1:]):
            cls = ' class="orphan-col"' if orphan_cols[c] else ""
            table.append(f'<td{cls}>{value}</td>')
        table.append("</tr>")
    table.append("</tbody></table>")
    missing_screens = [screen["name"] for screen in screens if screen["orphan"]]
    missing_jobs = [re.search(r"J\d+", row[0])[0] for i,row in enumerate(rows) if orphan_rows[i]]
    has_orphans = bool(missing_screens or missing_jobs)
    orphan_summary = f'<div class="orphan-summary{" has-orphans" if has_orphans else ""}"><p><strong>{"Знайдено сиріт" if has_orphans else "Сиріт у поточному MVP немає."}</strong></p><p>Екрани-сироти: {html.escape(", ".join(missing_screens)) if missing_screens else "немає"}. Jobs-сироти: {", ".join(missing_jobs) if missing_jobs else "немає"}.</p></div>'
    flow_html = []
    for job in jobs:
        key = job["id"]
        label = "MAIN JOB · J0" if key == "J0" else key
        flow_html.append(f'''<article class="flow" id="flow-{key}" aria-labelledby="title-{key}">
<h3 id="title-{key}"><span class="job-id">{label}</span>{html.escape(job["title"])}</h3>
<div class="prose">{markdown(job["before"])}</div>
<div class="diagram" aria-label="Діаграма {key}">
<div class="diagram-toolbar" role="group" aria-label="Масштаб діаграми {key}">
<button type="button" data-zoom="out" aria-label="Зменшити діаграму {key}" disabled>−</button>
<output class="zoom-value" aria-label="Масштаб {key}">—</output>
<button type="button" data-zoom="in" aria-label="Збільшити діаграму {key}" disabled>+</button>
<button type="button" data-zoom="fit" disabled>За шириною</button>
<button type="button" data-zoom="actual" disabled>100%</button>
<button type="button" data-fullscreen hidden disabled>На весь екран</button>
</div>
<p class="diagram-hint" id="hint-{key}">Прокручуйте діаграму в обидва боки. Масштаб можна змінити кнопками.</p>
<div class="diagram-viewport" tabindex="0" role="region" aria-label="Маршрут {key}" aria-describedby="hint-{key}">
<p class="render-status" role="status">Завантажуємо діаграму…</p><div class="diagram-canvas"></div>
</div></div>
<noscript><p>Увімкніть JavaScript, щоб побачити діаграму. Її Mermaid-код доступний нижче.</p></noscript>
<details class="flow-explanation" open><summary>Розвилки, стани та межі {key}</summary><div class="prose">{markdown(job["after"])}</div></details>
<details><summary>Mermaid-код {key}</summary><pre class="diagram-source"><code class="mermaid-source">{html.escape(job["graph"])}</code></pre></details>
</article>''')
    source_hash = hashlib.sha256((sitemap + "\n" + flows).encode()).hexdigest()
    flow_index = "".join(f'<a href="#flow-{j["id"]}" title="{html.escape(j["title"],quote=True)}">{"MAIN JOB" if j["id"]=="J0" else j["id"]}</a>' for j in jobs)
    return f'''<!doctype html>
<!-- Generated by build_ia.py. Sources SHA-256: {source_hash} -->
<html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Знімок інформаційної архітектури: дерево п’яти екранів, сім user flows та матриця трасування MVP.">
<title>Структура продукту — догляд за котами й собаками</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%2314212a'/%3E%3Cpath d='M8 8h16M16 8v10M8 24v-6h16v6' fill='none' stroke='%239fe4ce' stroke-width='2'/%3E%3C/svg%3E">
<link rel="stylesheet" href="_nav/nav.css"><style>{CSS}
.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap;border:0}}
</style><script src="_nav/tree.js" defer></script><script id="repo-nav-script" src="_nav/nav.js" data-root="./" defer></script></head>
<body><a class="skip-link" href="#content">До вмісту</a><main id="content" class="page">
<header><h1>Структура продукту</h1><p class="lead">П’ять екранів. Сім jobs. Одна карта того, як власник тварини переходить від потреби до результату.</p>
<p class="note measure">Знімок IA для перегляду: структура, маршрути й покриття ядра MVP. Це проєктна специфікація; екрани застосунку ще не реалізовані.</p>
<div class="source-links"><a href="sitemap.md">Джерело: sitemap.md</a><a href="flows.md">Джерело: flows.md</a><a href="research/research.html#персони">Персони та JTBD</a></div>
<nav class="jump-links" aria-label="Розділи цієї сторінки"><a href="#sitemap">Дерево екранів</a><a href="#flows">User flows</a><a href="#trace">Трасування</a></nav></header>
<section id="sitemap" aria-labelledby="sitemap-title"><h2 id="sitemap-title">Дерево екранів</h2>
<p class="measure muted">Три входи глобальної навігації: «Догляд», «Запис дії» та «Тварини». Під кожним екраном — файл майбутнього вайрфрейму й jobs за чинною матрицею; натисніть job, щоб відкрити його flow.</p>
<ul class="site-tree">{"".join(tree)}</ul>
<p class="connections">Спільні переходи: <a href="#screen-action">Дія</a> → <a href="#screen-action-edit">Запис дії</a>; <a href="#screen-pet">Тварина</a> → <a href="#screen-action">Дія</a>. «Додати тварину» з головного або редактора веде в <a href="#screen-pet-edit">Дані тварини</a> з поверненням до початкового контексту.</p>
<p class="note measure">Імена файлів позначають заплановані екрани, тому не ведуть на ще не створені сторінки. Стани й режими не збільшують кількості екранів.</p>
<details><summary>Навігація, перемикач тварин і глибина маршрутів</summary><div class="prose">{markdown(sitemap.split('## Навігація',1)[1].split('## Трасування',1)[0], 'sitemap.md')}</div></details></section>
<section id="flows" aria-labelledby="flows-title"><h2 id="flows-title">User flows</h2>
<p class="measure muted">MAIN JOB та J1–J6: повні маршрути з джерела, включно з empty, loading, error, успіхом і тупиками. Розвилки та стани описані під кожною діаграмою.</p>
<nav class="flow-index" aria-label="Перейти до job">{flow_index}</nav>
<details><summary>Позначення, спільні стани редакторів і погоджені правила</summary><div class="prose">{markdown(''.join(intro))}</div></details>
{"".join(flow_html)}
<details><summary>Погоджені рішення та межі перевірки</summary><div class="prose">{markdown(''.join(ending))}</div></details></section>
<section id="trace" aria-labelledby="trace-title"><h2 id="trace-title">Матриця трасування</h2>
<p class="measure muted">Активний MVP: J0–J6 × усі п’ять екранів. <code>x</code> — екран безпосередньо допомагає закрити job. Порожня клітинка означає відсутність такої участі.</p>
<div class="table-scroll" tabindex="0" role="region" aria-label="Матриця job — екран">{"".join(table)}</div>
{orphan_summary}
<p class="note measure">Порожній рядок або колонка — дефект: їх підсвічено червоним і позначено «СИРОТА». Окремі порожні клітинки нормальні. E1/E2 — критерії якості; S1/S2 відкладено в <a href="backlog.md">backlog</a>.</p>
<details class="trace-notes"><summary>Підстави позначок і критерії якості</summary><div class="prose">{markdown(trace.split('### Підстави позначок',1)[1].split('### ЕКРАНИ-СИРОТИ',1)[0], 'sitemap.md')}</div></details></section>
<footer><p>Знімок побудовано з <a href="sitemap.md">sitemap.md</a> та <a href="flows.md">flows.md</a>. Дослідницькі гіпотези й технічні межі збережені у джерелах.</p><a href="#content">На початок сторінки</a></footer>
</main><script type="module">{JS}</script></body></html>
'''


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if ia.html is stale")
    args = parser.parse_args()
    rendered = build()
    target = ROOT / "ia.html"
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != rendered:
            raise SystemExit("ia.html is stale; run python -B build_ia.py")
        print("ia.html is current")
    else:
        target.write_text(rendered, encoding="utf-8", newline="\n")
        print("Built ia.html")
