"""Build the static, source-linked research page from research.md."""

from html import escape
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
source = (ROOT / "research.md").read_text(encoding="utf-8")


def inline(value: str) -> str:
    value = escape(value)
    value = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{escape(match.group(2), quote=True)}">{match.group(1)}</a>',
        value,
    )
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    return value


def render(lines: list[str]) -> str:
    chunks = []
    paragraph = []
    ordered = []
    table = []

    def flush_paragraph() -> None:
        if paragraph:
            chunks.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def flush_ordered() -> None:
        if ordered:
            chunks.append("<ol>" + "".join(f"<li>{inline(item)}</li>" for item in ordered) + "</ol>")
            ordered.clear()

    def flush_table() -> None:
        if not table:
            return
        rows = [row.strip().strip("|").split("|") for row in table]
        rows = [[cell.strip() for cell in row] for row in rows]
        head = "".join(f'<th scope="col">{inline(cell)}</th>' for cell in rows[0])
        body = "".join(
            "<tr>" + "".join(
                f'<th scope="row">{inline(cell)}</th>' if index == 0 else f"<td>{inline(cell)}</td>"
                for index, cell in enumerate(row)
            ) + "</tr>"
            for row in rows[2:]
        )
        chunks.append(f'<div class="table-wrap" tabindex="0" aria-label="Таблиця порівняння"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
        table.clear()

    for raw in lines + [""]:
        line = raw.strip()
        if line.startswith("|"):
            flush_paragraph()
            flush_ordered()
            table.append(line)
            continue
        flush_table()
        if line.startswith("### "):
            flush_paragraph()
            flush_ordered()
            chunks.append(f"<h3>{inline(line[4:])}</h3>")
        elif re.match(r"^\d+\. ", line):
            flush_paragraph()
            ordered.append(re.sub(r"^\d+\. ", "", line))
        elif not line:
            flush_paragraph()
            flush_ordered()
        else:
            flush_ordered()
            paragraph.append(line)
    return "\n".join(chunks)


sections = re.split(r"(?m)^## (.+)$", source)
section_html = {}
for index in range(1, len(sections), 2):
    section_html[sections[index]] = render(sections[index + 1].strip().splitlines())

gallery = """
<div class="evidence-head">
  <h3>Екрани з дослідження</h3>
  <p>Кадри з тестових акаунтів позначені «Власне проходження». Felivo — публічна сторінка. Знімки профілю з email або ім’ям прибрані з публікації.</p>
</div>
<div class="evidence-grid">
  <figure><a href="screens/own/nosik-home-next-actions.png"><img src="screens/own/nosik-home-next-actions.png" alt="Головна Nosik із найближчими справами та назвою препарату" loading="lazy"></a><figcaption><b>Nosik</b><span>Власне проходження · Найближчі дії</span></figcaption></figure>
  <figure><a href="screens/own/pet-health-home.png"><img src="screens/own/pet-health-home.png" alt="Головна Pet Health із лічильниками справ і недавньою активністю" loading="lazy"></a><figcaption><b>Pet Health</b><span>Власне проходження · Стан і швидкі дії</span></figcaption></figure>
  <figure><a href="screens/own/dogcat-calendar.png"><img src="screens/own/dogcat-calendar.png" alt="Календар DogCatApp із фільтром кота" loading="lazy"></a><figcaption><b>DogCatApp</b><span>Власне проходження · Календар</span></figcaption></figure>
  <figure><a href="screens/own/todoist-story-repeat-options.png"><img src="screens/own/todoist-story-repeat-options.png" alt="Окреме меню повторення задачі в Todoist" loading="lazy"></a><figcaption><b>Todoist</b><span>Власне проходження · Повторення</span></figcaption></figure>
  <figure><a href="screens/felivo-detail-public-mobile.png"><img src="screens/felivo-detail-public-mobile.png" alt="Публічна мобільна сторінка Felivo" loading="lazy"></a><figcaption><b>Felivo</b><span>Публічна сторінка · Деталі продукту</span></figcaption></figure>
</div>
"""

parts = []
ids = {"КОНКУРЕНТИ": "конкуренти", "БЕНЧМАРК": "бенчмарк", "ПАТЕРНИ": "патерни", "ВИСНОВКИ": "висновки"}
for number, title in enumerate(ids, 1):
    parts.append(f'<section id="{ids[title]}" class="report-section" aria-labelledby="heading-{ids[title]}"><div class="section-title"><span class="section-number">{number:02d}</span><h2 id="heading-{ids[title]}">{title.capitalize()}</h2></div>{section_html[title]}{gallery if title == "КОНКУРЕНТИ" else ""}</section>')

html = """<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>Дослідження MVP · Здоров’я котів</title>
  <meta name="description" content="Конкуренти, бенчмарк, UX-патерни та гіпотези для MVP застосунку здоров’я котів.">
  <link rel="stylesheet" href="../_nav/nav.css">
  <style>
    :root { --bg: #0d151b; --panel: #14212a; --line: #2a3b44; --text: #e9f0ed; --muted: #aabbbd; --accent: #9fe4ce; --warm: #edc48a; }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { margin: 0; background: var(--bg); color: var(--text); font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }
    body.repo-has-nav { padding-left: 240px; }
    a { color: var(--accent); text-underline-offset: .18em; }
    a:hover { color: #cbf5e5; }
    :focus-visible { outline: 2px solid var(--warm); outline-offset: 3px; }
    #repo-nav { border-color: var(--line); background: #101c24; color: var(--text); }
    #repo-nav .repo-nav-heading { color: var(--text); letter-spacing: -.02em; }
    #repo-nav .repo-nav-branch { color: var(--muted); text-transform: uppercase; letter-spacing: .1em; }
    #repo-nav a { color: var(--muted); }
    #repo-nav a:hover, #repo-nav a:focus-visible { background: #21333d; color: var(--text); }
    #repo-nav a[aria-current="page"] { background: #214238; color: #d7f8e9; }
    .page { max-width: 1450px; margin: auto; padding: 0 clamp(22px, 5vw, 80px) 96px; }
    .masthead { padding: clamp(55px, 8vw, 118px) 0 68px; border-bottom: 1px solid var(--line); }
    h1 { max-width: 900px; margin: 0; font-size: clamp(2.8rem, 6.5vw, 5.6rem); line-height: 1.04; font-weight: 650; letter-spacing: -.065em; }
    .lead { max-width: 720px; margin: 28px 0 0; color: #c6d4d3; font-size: clamp(1.05rem, 1.4vw, 1.28rem); line-height: 1.55; }
    .mast-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 34px; }
    .mast-links a, .jump a { display: inline-flex; align-items: center; min-height: 38px; padding: 6px 13px; border: 1px solid #426658; border-radius: 99px; color: #d8f6e9; text-decoration: none; font-size: .88rem; }
    .mast-links a:hover, .jump a:hover { background: #214238; }
    .provenance { display: flex; flex-wrap: wrap; gap: 14px 22px; margin-top: 35px; color: var(--muted); font-size: .85rem; }
    .provenance span::before { content: ""; display: inline-block; width: 7px; height: 7px; margin-right: 8px; border-radius: 50%; background: var(--warm); vertical-align: 2px; }
    .provenance span:first-child::before { background: var(--accent); }
    .jump { display: flex; flex-wrap: wrap; gap: 10px; margin: 24px 0 0; }
    .jump a { border-color: var(--line); color: var(--muted); }
    .report-section { padding: 78px 0 88px; border-bottom: 1px solid var(--line); scroll-margin-top: 18px; }
    .section-title { display: flex; align-items: baseline; gap: 18px; margin-bottom: 30px; }
    .section-number { color: var(--accent); font: 600 1.04rem/1 ui-monospace, monospace; }
    h2 { margin: 0; font-size: clamp(2rem, 3vw, 3rem); line-height: 1.15; letter-spacing: -.045em; }
    h3 { margin: 58px 0 22px; font-size: 1.38rem; line-height: 1.25; letter-spacing: -.025em; }
    .report-section > p, .report-section > ol { max-width: 75ch; }
    p { margin: 0 0 18px; }
    strong { color: #f3f6f1; font-weight: 680; }
    ol { padding-left: 1.4em; margin: 24px 0 32px; }
    li { padding-left: .35em; margin: 0 0 17px; }
    li::marker { color: var(--warm); font-weight: 700; }
    .table-wrap { width: 100%; margin: 25px 0 42px; overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: #101d25; scrollbar-color: #59726d transparent; }
    table { width: 100%; min-width: 780px; border-collapse: collapse; font-size: .9rem; line-height: 1.55; }
    th, td { padding: 19px 20px; border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
    tr > :last-child { border-right: 0; }
    tbody tr:last-child > * { border-bottom: 0; }
    thead th { background: #1a2b34; color: #d8e9e4; font-size: .8rem; letter-spacing: .02em; }
    tbody th { width: 160px; min-width: 160px; color: var(--warm); font-weight: 700; }
    tbody tr:nth-child(even) { background: #14222a; }
    td { min-width: 245px; color: #c6d3d3; }
    td a, th a { white-space: normal; }
    .evidence-head { display: grid; grid-template-columns: 1fr 2fr; gap: 30px; align-items: baseline; margin-top: 70px; }
    .evidence-head h3 { margin: 0; }
    .evidence-head p { margin: 0; color: var(--muted); }
    .evidence-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; margin-top: 28px; }
    figure { min-width: 0; margin: 0; }
    figure > a { display: flex; align-items: center; justify-content: center; height: 300px; padding: 12px; border: 1px solid var(--line); border-radius: 10px; background: #17242d; }
    figure img { display: block; width: 100%; height: 100%; object-fit: contain; }
    figcaption { padding: 12px 2px 0; font-size: .82rem; line-height: 1.45; }
    figcaption b, figcaption span { display: block; }
    figcaption span { margin-top: 3px; color: var(--muted); }
    .footer { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 16px; padding-top: 36px; color: var(--muted); font-size: .88rem; }
    @media (max-width: 1100px) { .evidence-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
    @media (max-width: 760px) {
      body.repo-has-nav { padding-left: 0; }
      .page { width: 100vw; max-width: 100vw; min-width: 0; }
      #repo-nav { position: static; inset: auto; width: 100vw; display: flex; align-items: center; gap: 24px; overflow: hidden; padding: 12px 18px; border-right: 0; border-bottom: 1px solid var(--line); }
      #repo-nav .repo-nav-heading { flex: 0 0 auto; margin: 0; }
      #repo-nav .repo-nav-branches { display: flex; gap: 12px; flex-wrap: wrap; }
      #repo-nav .repo-nav-branches > li + li { margin: 0; }
      #repo-nav .repo-nav-branch { margin: 0 4px; }
      #repo-nav .repo-nav-pages { display: flex; flex-wrap: wrap; }
      #repo-nav a { padding: 4px 7px; }
      .evidence-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .evidence-head { grid-template-columns: 1fr; gap: 12px; }
      .report-section { padding: 62px 0 72px; }
    }
    @media (max-width: 480px) {
      #repo-nav { display: block; }
      #repo-nav .repo-nav-heading { margin-bottom: 7px; }
      #repo-nav .repo-nav-branches { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
      #repo-nav .repo-nav-branches > li { min-width: 0; }
      #repo-nav .repo-nav-pages { display: block; }
      #repo-nav a { overflow-wrap: anywhere; }
      .evidence-grid { gap: 10px; }
      figure > a { height: 225px; padding: 8px; }
      figcaption { font-size: .76rem; }
      .page { padding-left: 18px; padding-right: 18px; }
      th, td { padding: 14px 15px; }
    }
    @media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
  </style>
  <script src="../_nav/tree.js" defer></script>
  <script id="repo-nav-script" src="../_nav/nav.js" data-root="../" defer></script>
</head>
<body class="research-page">
  <main class="page">
    <header class="masthead">
      <h1>Наступна дія має бути очевидною.</h1>
      <p class="lead">Дослідження досвіду догляду за 1–5 котами: що вже зроблено, який препарат давали востаннє і що потрібно запланувати далі.</p>
      <div class="mast-links"><a href="research.md">Повний звіт у Markdown ↗</a><a href="../Codex.md">Продуктовий бриф ↗</a></div>
      <div class="provenance" aria-label="Типи джерел"><span>Власні тестові проходження</span><span>Публічні сторінки</span><span>Mobbin</span></div>
      <nav class="jump" aria-label="Розділи сторінки"><a href="#конкуренти">Конкуренти</a><a href="#бенчмарк">Бенчмарк</a><a href="#патерни">Патерни</a><a href="#висновки">Висновки</a></nav>
    </header>
    REPORT
    <footer class="footer"><span>Джерела й межі висновків наведені біля кожного спостереження.</span><a href="#конкуренти">Повернутися до початку ↑</a></footer>
  </main>
</body>
</html>
""".replace("    REPORT", "\n".join(parts))

(ROOT / "research.html").write_text(html, encoding="utf-8")
missing = [
    target for target in re.findall(r'(?:href|src)="([^"]+)"', html)
    if not target.startswith(("http://", "https://", "#", "mailto:"))
    and not (ROOT / unquote(urlsplit(target).path)).exists()
]
if missing:
    raise SystemExit(f"Missing local links: {missing}")
print(f"Wrote research.html ({len(html):,} chars)")
