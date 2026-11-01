"""Build personas.html from the two source-of-truth Markdown files."""

from html import escape, unescape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
PERSONAS = (ROOT / "personas.md").read_text(encoding="utf-8")
JTBD = (ROOT / "jtbd.md").read_text(encoding="utf-8")


def inline(value: str) -> str:
    value = escape(value)
    value = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{escape(unescape(match.group(2)), quote=True)}">{match.group(1)}</a>',
        value,
    )
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"<code>\[\?\]</code>|\[\?\]", '<span class="unknown">[?]</span>', value)
    return value


def section(source: str, title: str, level: int = 2) -> str:
    hashes = "#" * level
    match = re.search(
        rf"(?ms)^{hashes} {re.escape(title)}\s*\n(.*?)(?=^#{{1,{level}}} |\Z)",
        source,
    )
    if not match:
        raise ValueError(f"Missing Markdown section: {title}")
    return match.group(1).strip()


def paragraphs(value: str) -> str:
    return "\n".join(f"<p>{inline(item)}</p>" for item in re.split(r"\n\s*\n", value.strip()) if item.strip())


persona_names = [
    "Фіксує повторний догляд",
    "Зводить справи кількох улюбленців",
    "Ділить догляд і передає історію",
]
persona_html = []
for number, name in enumerate(persona_names, 1):
    rank = "primary" if number == 1 else "secondary"
    body = section(PERSONAS, f"{number}. {name} — **{rank}**")
    behavior = re.search(r"(?m)^\*\*Поведінка:\*\* (.+)$", body)
    if not behavior:
        raise ValueError(f"Missing behavior for {name}")
    blocks = re.findall(r"(?m)^- \*\*(.+?)\*\* (.+)$", body)
    if len(blocks) != 5:
        raise ValueError(f"Expected five source blocks for {name}, got {len(blocks)}")
    block_html = "\n".join(
        f'<div class="persona-block{(" quote-block" if index == 5 else "")}">'
        f'<h4>{inline(label.rstrip("."))}</h4><p>{inline(content)}</p></div>'
        for index, (label, content) in enumerate(blocks, 1)
    )
    persona_html.append(
        f'<article class="persona-card {rank}" id="persona-{number}">'
        f'<div class="persona-top"><div><span class="eyebrow">ПЕРСОНА {number:02d}</span>'
        f'<h3>{escape(name)}</h3><p class="behavior">{inline(behavior.group(1))}</p></div>'
        f'<span class="rank rank-{rank}">{rank}</span></div>'
        f'<div class="persona-blocks">{block_html}</div></article>'
    )


main = section(JTBD, "Main job продукту")
main_quote = re.search(r"(?m)^> (.+)$", main)
if not main_quote:
    raise ValueError("Missing main job")
main_explanation = main[main_quote.end():].strip()
related = section(JTBD, "Related jobs на шляху до main job")
related_items = re.findall(r"(?m)^([1-5])\. (.+)$", related)
if len(related_items) != 5:
    raise ValueError("Expected five related jobs")


def job_cards(items: list[tuple[str, str]], prefix: str) -> str:
    return "\n".join(
        f'<article class="job-card"><span class="job-id">{prefix}{number}</span>'
        f'<div>{inline(content)}</div></article>'
        for number, content in items
    )


def bullet_items(title: str) -> list[tuple[str, str]]:
    return [(str(index), item) for index, item in enumerate(re.findall(r"(?m)^- (.+)$", section(JTBD, title)), 1)]


emotional = bullet_items("Emotional jobs")
social = bullet_items("Social jobs")
hypotheses = bullet_items("Гіпотези, які не входять до основної ієрархії")
matrix_body = section(JTBD, "JTBD-матриця")
matrix_before_conclusion = matrix_body.split("### Висновок для ядра MVP", 1)[0].strip()
matrix_rows = [line.strip().strip("|") for line in matrix_before_conclusion.splitlines() if line.startswith("|")]
if len(matrix_rows) != 16:
    raise ValueError(f"Expected matrix header, separator and 14 jobs; got {len(matrix_rows)} rows")
matrix_cells = [[cell.strip() for cell in row.split("|")] for row in matrix_rows]
if any(len(row) != 6 for row in matrix_cells):
    raise ValueError("JTBD matrix needs exactly six columns")
matrix_head = "".join(f'<th scope="col">{inline(cell)}</th>' for cell in matrix_cells[0])
matrix_body_html = "\n".join(
    "<tr>" + "".join(
        (f'<th scope="row">{inline(cell)}</th>' if index == 0 else f'<td>{inline(cell)}</td>')
        for index, cell in enumerate(row)
    ) + "</tr>"
    for row in matrix_cells[2:]
)
matrix_intro = matrix_before_conclusion.split("|", 1)[0].strip()
matrix_after_table = matrix_before_conclusion.splitlines()[-1].strip()
matrix_note = matrix_after_table if not matrix_after_table.startswith("|") else ""
matrix_conclusion = matrix_body.split("### Висновок для ядра MVP", 1)[1].strip()
why_primary = section(PERSONAS, "Чому primary — «Фіксує повторний догляд»")


HTML = f'''<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>Персони та JTBD · Догляд за котами й собаками</title>
  <meta name="description" content="Поведінкові персони, ієрархія jobs та JTBD-матриця для застосунку догляду за котами й собаками.">
  <link rel="stylesheet" href="_nav/nav.css">
  <style>
    :root {{ --bg:#0d151b; --panel:#14212a; --line:#2a3b44; --text:#e9f0ed; --muted:#aabbbd; --accent:#9fe4ce; --warm:#edc48a; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; background:var(--bg); color:var(--text); font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; }}
    body.repo-has-nav {{ padding-left:240px; }}
    ::selection {{ background:#315c4d; color:#fff; }}
    a {{ color:var(--accent); text-underline-offset:.18em; }}
    a:hover {{ color:#cbf5e5; }}
    :focus-visible {{ outline:2px solid var(--warm); outline-offset:3px; }}
    #repo-nav {{ border-color:var(--line); background:#101c24; color:var(--text); }}
    #repo-nav .repo-nav-heading {{ color:var(--text); letter-spacing:-.02em; }}
    #repo-nav .repo-nav-branch {{ color:var(--muted); text-transform:uppercase; letter-spacing:.1em; }}
    #repo-nav a {{ color:var(--muted); }}
    #repo-nav a:hover,#repo-nav a:focus-visible {{ background:#21333d; color:var(--text); }}
    #repo-nav a[aria-current="page"] {{ background:#214238; color:#d7f8e9; }}
    .page {{ max-width:1450px; margin:auto; padding:0 clamp(22px,5vw,80px) 96px; }}
    .masthead {{ padding:clamp(55px,8vw,118px) 0 68px; border-bottom:1px solid var(--line); }}
    .eyebrow,.job-id {{ color:var(--accent); font:650 .8rem/1.2 ui-monospace,monospace; letter-spacing:.09em; }}
    h1 {{ max-width:920px; margin:14px 0 0; font-size:clamp(2.8rem,6.5vw,5.6rem); line-height:1.04; font-weight:650; letter-spacing:-.04em; }}
    .lead {{ max-width:760px; margin:28px 0 0; color:#c6d4d3; font-size:clamp(1.05rem,1.4vw,1.28rem); line-height:1.55; }}
    .meta {{ max-width:820px; margin:22px 0 0; color:var(--muted); font-size:.92rem; }}
    .links,.jump {{ display:flex; flex-wrap:wrap; gap:10px; }}
    .links {{ margin-top:34px; }}
    .jump {{ margin-top:24px; }}
    .links a,.jump a {{ display:inline-flex; align-items:center; min-height:38px; padding:6px 13px; border:1px solid #426658; border-radius:99px; color:#d8f6e9; text-decoration:none; font-size:.88rem; }}
    .jump a {{ border-color:var(--line); color:var(--muted); }}
    .links a:hover,.jump a:hover {{ background:#214238; color:#fff; }}
    .report-section {{ padding:78px 0 88px; border-bottom:1px solid var(--line); scroll-margin-top:18px; }}
    .section-title {{ display:flex; align-items:baseline; gap:18px; margin-bottom:30px; }}
    h2 {{ margin:0; font-size:clamp(2rem,3vw,3rem); line-height:1.15; letter-spacing:-.04em; }}
    h3 {{ margin:0; font-size:clamp(1.45rem,2vw,1.8rem); line-height:1.25; letter-spacing:-.02em; }}
    h4 {{ margin:0 0 10px; color:var(--warm); font-size:.9rem; text-transform:uppercase; letter-spacing:.06em; }}
    p {{ margin:0 0 18px; }}
    strong {{ color:#f3f6f1; font-weight:680; }}
    .section-intro {{ max-width:75ch; color:var(--muted); }}
    .persona-stack {{ display:grid; gap:22px; }}
    .persona-card {{ overflow:hidden; border:1px solid var(--line); border-radius:12px; background:var(--panel); }}
    .persona-card.primary {{ border-color:#5a9d83; }}
    .persona-top {{ display:flex; justify-content:space-between; align-items:flex-start; gap:24px; padding:28px 30px 24px; border-bottom:1px solid var(--line); }}
    .persona-top h3 {{ margin:10px 0 8px; }}
    .behavior {{ max-width:70ch; margin:0; color:#c6d4d3; }}
    .rank {{ flex:none; padding:5px 11px; border:1px solid var(--line); border-radius:99px; color:var(--muted); font:650 .78rem/1.3 ui-monospace,monospace; text-transform:uppercase; }}
    .rank-primary {{ border-color:#5a9d83; background:#214238; color:#d7f8e9; }}
    .persona-blocks {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); }}
    .persona-block {{ min-width:0; padding:24px 30px; border-bottom:1px solid var(--line); }}
    .persona-block:nth-child(odd) {{ border-right:1px solid var(--line); }}
    .persona-block p {{ margin:0; color:#c6d3d3; }}
    .persona-block.quote-block {{ grid-column:1/-1; border-right:0; border-bottom:0; background:#10202a; }}
    .note {{ max-width:80ch; margin:28px 0 0; color:var(--muted); font-size:.94rem; }}
    .main-job {{ max-width:1030px; padding:28px 32px; border:1px solid #4b806e; border-radius:12px; background:#173127; }}
    .main-job blockquote {{ margin:0 0 18px; font-size:clamp(1.2rem,2vw,1.65rem); line-height:1.45; }}
    .main-job p {{ margin:0; color:#c9ded4; }}
    .job-group {{ margin-top:48px; }}
    .job-group h3 {{ margin-bottom:20px; }}
    .job-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }}
    .job-card {{ display:grid; grid-template-columns:32px 1fr; gap:16px; min-width:0; padding:22px; border:1px solid var(--line); border-radius:10px; background:var(--panel); }}
    .job-card p {{ margin:0; }}
    .job-card strong:first-child {{ color:var(--text); }}
    .job-card .job-id {{ padding-top:4px; }}
    .hypothesis-group {{ padding-top:26px; border-top:1px solid var(--line); }}
    .hypothesis-group .job-id {{ color:var(--warm); }}
    .unknown {{ display:inline-block; padding:0 5px; border:1px solid #9b7650; border-radius:4px; background:#3a2d24; color:#f9d3a0; font:700 .88em/1.45 ui-monospace,monospace; white-space:nowrap; }}
    .legend {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px 12px; max-width:85ch; margin:18px 0 0; color:var(--muted); font-size:.9rem; }}
    .hypothesis-label {{ display:inline-block; padding:2px 8px; border:1px solid #9b7650; border-radius:99px; color:#f9d3a0; font-size:.78rem; font-weight:650; }}
    .table-wrap {{ width:100%; margin:25px 0 32px; padding:10px; overflow:auto; border:1px solid var(--line); border-radius:10px; background:#101d25; scrollbar-color:#59726d transparent; }}
    table {{ width:100%; min-width:1370px; border-collapse:separate; border-spacing:0; font-size:.88rem; line-height:1.5; }}
    caption {{ padding:15px 18px; color:var(--muted); text-align:left; font-size:.85rem; }}
    th,td {{ min-width:0; padding:17px 18px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    tr > :last-child {{ border-right:0; }}
    tbody tr:last-child > * {{ border-bottom:0; }}
    thead th {{ position:sticky; top:0; z-index:2; background:#1a2b34; color:#d8e9e4; font-size:.8rem; }}
    tbody th {{ position:sticky; left:0; z-index:1; width:225px; min-width:225px; background:#122029; color:var(--warm); }}
    tbody tr:nth-child(even) td {{ background:#14222a; }}
    td {{ width:190px; color:#c6d3d3; }}
    td:nth-last-child(2),td:last-child {{ width:280px; }}
    td strong {{ font-variant-numeric:tabular-nums; }}
    .matrix-explainer,.matrix-note {{ max-width:80ch; color:var(--muted); }}
    .matrix-note {{ margin-top:18px; }}
    .mvp {{ max-width:85ch; margin-top:40px; }}
    .mvp h3 {{ margin-bottom:18px; }}
    .footer {{ display:flex; flex-wrap:wrap; justify-content:space-between; gap:16px; padding-top:36px; color:var(--muted); font-size:.88rem; }}
    @media (max-width:980px) {{ .persona-blocks,.job-grid {{ grid-template-columns:1fr; }} .persona-block:nth-child(odd) {{ border-right:0; }} .persona-block.quote-block {{ grid-column:auto; }} }}
    @media (max-width:760px) {{
      body.repo-has-nav {{ padding-left:0; }}
      .page {{ width:100vw; max-width:100vw; min-width:0; }}
      #repo-nav {{ position:static; inset:auto; width:100vw; display:flex; align-items:center; gap:24px; overflow:hidden; padding:12px 18px; border-right:0; border-bottom:1px solid var(--line); }}
      #repo-nav .repo-nav-heading {{ flex:0 0 auto; margin:0; }}
      #repo-nav .repo-nav-branches {{ display:flex; gap:12px; flex-wrap:wrap; }}
      #repo-nav .repo-nav-branches > li + li {{ margin:0; }}
      #repo-nav .repo-nav-branch {{ margin:0 4px; }}
      #repo-nav .repo-nav-pages {{ display:flex; flex-wrap:wrap; }}
      #repo-nav a {{ padding:4px 7px; }}
      .report-section {{ padding:62px 0 72px; }}
    }}
    @media (max-width:480px) {{
      #repo-nav {{ display:block; }}
      #repo-nav .repo-nav-heading {{ margin-bottom:7px; }}
      #repo-nav .repo-nav-branches {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
      #repo-nav .repo-nav-branches > li {{ min-width:0; }}
      #repo-nav .repo-nav-pages {{ display:block; }}
      #repo-nav a {{ overflow-wrap:anywhere; }}
      .page {{ padding-left:18px; padding-right:18px; }}
      .persona-top,.persona-block {{ padding-left:18px; padding-right:18px; }}
      .persona-top {{ display:block; }}
      .rank {{ display:inline-block; margin-top:16px; }}
      .main-job {{ padding:20px; }}
      .job-card {{ padding:18px; }}
    }}
    @media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} }}
  </style>
  <script src="_nav/tree.js" defer></script>
  <script id="repo-nav-script" src="_nav/nav.js" data-root="./" defer></script>
</head>
<body class="personas-page">
  <main class="page">
    <header class="masthead">
      <h1>Люди й задачі догляду</h1>
      <p class="lead">Три поведінкові персони, головна задача продукту та зв’язок jobs із функціями й конкурентами.</p>
      <p class="meta">Це робочі моделі з якісного ресерчу, а не підтверджені сегменти українського ринку. Позначки <span class="unknown">[?]</span> і «гіпотеза» збережено з вихідних документів.</p>
      <div class="links"><a href="personas.md">Персони у Markdown ↗</a><a href="jtbd.md">JTBD у Markdown ↗</a></div>
      <nav class="jump" aria-label="Розділи сторінки"><a href="#персони">Персони</a><a href="#jobs">Ієрархія jobs</a><a href="#матриця">JTBD-матриця</a></nav>
    </header>

    <section id="персони" class="report-section" aria-labelledby="personas-heading">
      <div class="section-title"><h2 id="personas-heading">Персони</h2></div>
      <p class="section-intro">Поділ за поведінкою. Primary позначено кольором; кожна картка зберігає контекст, jobs, болі, тригери довіри, цитату й джерела з <a href="personas.md">personas.md</a>.</p>
      <div class="persona-stack">{''.join(persona_html)}</div>
      <div class="note">{paragraphs(why_primary)}</div>
    </section>

    <section id="jobs" class="report-section" aria-labelledby="jobs-heading">
      <div class="section-title"><h2 id="jobs-heading">Ієрархія jobs</h2></div>
      <div class="main-job"><span class="eyebrow">MAIN JOB · J0</span><blockquote>{inline(main_quote.group(1))}</blockquote>{paragraphs(main_explanation)}</div>
      <div class="job-group"><h3>Related jobs · J1–J5</h3><div class="job-grid">{job_cards(related_items, 'J')}</div></div>
      <div class="job-group"><h3>Emotional jobs · E1–E2</h3><div class="job-grid">{job_cards(emotional, 'E')}</div></div>
      <div class="job-group"><h3>Social jobs · S1–S2</h3><div class="job-grid">{job_cards(social, 'S')}</div></div>
      <div class="job-group hypothesis-group"><h3>Гіпотези · H1–H4</h3><p class="section-intro">Ці jobs не входять до основної ієрархії. Кожен потребує перевірки.</p><div class="job-grid">{job_cards(hypotheses, 'H')}</div></div>
    </section>

    <section id="матриця" class="report-section" aria-labelledby="matrix-heading">
      <div class="section-title"><h2 id="matrix-heading">JTBD-матриця</h2></div>
      <div class="matrix-explainer">{paragraphs(matrix_intro)}</div>
      <p class="legend"><span class="unknown">[?]</span> важливість або стан не встановлено <span class="hypothesis-label">гіпотеза</span> потреба чи рішення без достатнього підтвердження.</p>
      <div class="table-wrap" tabindex="0" role="region" aria-label="JTBD-матриця, прокручується горизонтально">
        <table><caption>Усі 14 jobs із jtbd.md · важливість для трьох персон, функція продукту й конкуренти</caption><thead><tr>{matrix_head}</tr></thead><tbody>{matrix_body_html}</tbody></table>
      </div>
      <div class="matrix-note">{paragraphs(matrix_note)}</div>
      <div class="mvp"><h3>Висновок для ядра MVP</h3>{paragraphs(matrix_conclusion)}</div>
    </section>

    <footer class="footer"><span>Джерела: <a href="personas.md">personas.md</a> і <a href="jtbd.md">jtbd.md</a>.</span><a href="research/research.html">Дослідження ↗</a></footer>
  </main>
</body>
</html>
'''

(ROOT / "personas.html").write_text(HTML, encoding="utf-8")
