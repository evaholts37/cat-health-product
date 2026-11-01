"""Build the static, source-linked research page from research.md."""

from html import escape, unescape
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
source = (ROOT / "research.md").read_text(encoding="utf-8")
COMPETITOR_GROUPS = {
    "DogCatApp": "Хард",
    "Nosik": "Хард",
    "Pet Health": "Хард",
    "Todoist": "Софт",
    "Felivo": "Аспіраційні",
}


def inline(value: str) -> str:
    value = escape(value)
    value = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{escape(unescape(match.group(2)), quote=True)}">{match.group(1)}</a>',
        value,
    )
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    return value


def render(lines: list[str]) -> str:
    chunks = []
    paragraph = []
    ordered = []
    unordered = []
    table = []

    def flush_paragraph() -> None:
        if paragraph:
            chunks.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def flush_ordered() -> None:
        if ordered:
            chunks.append("<ol>" + "".join(f"<li>{inline(item)}</li>" for item in ordered) + "</ol>")
            ordered.clear()

    def flush_unordered() -> None:
        if unordered:
            chunks.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in unordered) + "</ul>")
            unordered.clear()

    def flush_table() -> None:
        if not table:
            return
        rows = [row.strip().strip("|").split("|") for row in table]
        rows = [[cell.strip() for cell in row] for row in rows]
        is_conclusions = rows[0][0].startswith("Прогалина")
        is_competitor_matrix = rows[0][0] == "Продукт"
        head = "".join(f'<th scope="col">{inline(cell)}</th>' for cell in rows[0])

        def body_cell(cell: str, index: int) -> str:
            if index == 0 and is_competitor_matrix:
                group = COMPETITOR_GROUPS.get(cell.strip("*"))
                if group:
                    return f'<th scope="row">{inline(cell)}<span class="competitor-group">{group}</span></th>'
            if index == 0 and not is_conclusions:
                return f'<th scope="row">{inline(cell)}</th>'
            return f"<td>{inline(cell)}</td>"

        body = "".join(
            "<tr>" + "".join(body_cell(cell, index) for index, cell in enumerate(row)) + "</tr>"
            for row in rows[2:]
        )
        table_class = ' class="conclusions-table"' if is_conclusions else ""
        chunks.append(f'<div class="table-wrap" tabindex="0" aria-label="Таблиця порівняння"><table{table_class}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
        table.clear()

    for raw in lines + [""]:
        line = raw.strip()
        if line.startswith("|"):
            flush_paragraph()
            flush_ordered()
            flush_unordered()
            table.append(line)
            continue
        flush_table()
        if line.startswith("### "):
            flush_paragraph()
            flush_ordered()
            flush_unordered()
            chunks.append(f"<h3>{inline(line[4:])}</h3>")
        elif re.match(r"^\d+\. ", line):
            flush_paragraph()
            flush_unordered()
            ordered.append(re.sub(r"^\d+\. ", "", line))
        elif line.startswith("- "):
            flush_paragraph()
            flush_ordered()
            unordered.append(line[2:])
        elif not line:
            flush_paragraph()
            flush_ordered()
            flush_unordered()
        else:
            flush_ordered()
            flush_unordered()
            paragraph.append(line)
    return "\n".join(chunks)


sections = re.split(r"(?m)^## (.+)$", source)
section_html = {}
for index in range(1, len(sections), 2):
    section_html[sections[index]] = render(sections[index + 1].strip().splitlines())
section_html["ВИСНОВКИ"] = section_html["ВИСНОВКИ"].replace("<p>", '<p class="section-subtitle">', 1)

gallery = """
<div class="evidence-head" id="екрани-дослідження">
  <h3>Екрани з дослідження</h3>
  <p>Кадри з тестових акаунтів позначені «Власне проходження». Felivo — публічна сторінка. Введені у флоу дані вигадані. Натисніть на скріншот, щоб відкрити його у повному розмірі.</p>
</div>
<div class="evidence-grid">
  <figure><a href="screens/own/nosik-home-next-actions.png"><img src="screens/own/nosik-home-next-actions.png" alt="Головна Nosik із найближчими справами та назвою препарату" loading="lazy"></a><figcaption><b>Nosik</b><span>Власне проходження · Найближчі дії</span></figcaption></figure>
  <figure><a href="screens/own/pet-health-home.png"><img src="screens/own/pet-health-home.png" alt="Головна Pet Health із лічильниками справ і недавньою активністю" loading="lazy"></a><figcaption><b>Pet Health</b><span>Власне проходження · Стан і швидкі дії</span></figcaption></figure>
  <figure><a href="screens/own/dogcat-calendar.png"><img src="screens/own/dogcat-calendar.png" alt="Календар DogCatApp із фільтром кота" loading="lazy"></a><figcaption><b>DogCatApp</b><span>Власне проходження · Календар</span></figcaption></figure>
  <figure><a href="screens/own/todoist-story-repeat-options.png"><img src="screens/own/todoist-story-repeat-options.png" alt="Окреме меню повторення задачі в Todoist" loading="lazy"></a><figcaption><b>Todoist</b><span>Власне проходження · Повторення</span></figcaption></figure>
  <figure><a href="screens/felivo-detail-public-mobile.png"><img src="screens/felivo-detail-public-mobile.png" alt="Публічна мобільна сторінка Felivo" loading="lazy"></a><figcaption><b>Felivo</b><span>Публічна сторінка · Деталі продукту</span></figcaption></figure>
  <figure><a href="screens/own/nosik-completed-cycle-20261101.png"><img src="screens/own/nosik-completed-cycle-20261101.png" alt="Nosik показує запис виконаної обробки й наступний термін через 30 днів" loading="lazy"></a><figcaption><b>Nosik</b><span>1 листопада · Факт і наступний цикл</span></figcaption></figure>
  <figure><a href="screens/own/dogcat-three-pet-calendar-20261101.png"><img src="screens/own/dogcat-three-pet-calendar-20261101.png" alt="DogCatApp: календар і вибір одного з трьох профілів" loading="lazy"></a><figcaption><b>DogCatApp</b><span>1 листопада · Вибір тварини</span></figcaption></figure>
  <figure><a href="screens/own/pet-health-two-pet-activity-20261101.png"><img src="screens/own/pet-health-two-pet-activity-20261101.png" alt="Pet Health: спільні лічильники та дві картки тварин" loading="lazy"></a><figcaption><b>Pet Health</b><span>1 листопада · Дві тварини</span></figcaption></figure>
  <figure><a href="screens/own/pawme-ai-species-selection-20261101.png"><img src="screens/own/pawme-ai-species-selection-20261101.png" alt="PawMe: автоматично вибрано собаку для фото кота; вид можна виправити" loading="lazy"></a><figcaption><b>PawMe</b><span>1 листопада · Ручне виправлення виду</span></figcaption></figure>
</div>
"""

parts = []
sections_to_show = [
    ("КОНКУРЕНТИ", "конкуренти", "Конкуренти"),
    ("БЕНЧМАРК", "бенчмарк", "Бенчмарк"),
    ("ПАТЕРНИ", "патерни", "Патерни"),
    ("ВИСНОВКИ", "висновки", "Висновки"),
    ("ПУБЛІЧНІ ВІДГУКИ КОРИСТУВАЧІВ", "відгуки", "Публічні відгуки"),
    ("ФОРУМИ: ЯК ПАМ’ЯТАЮТЬ ПРО ДОГЛЯД ЗА КОТАМИ", "форуми", "Форуми"),
    ("ПОРІВНЯННЯ ЗІ СВІДЧЕННЯМИ ВЛАСНИКІВ СОБАК", "собаки", "Коти й собаки"),
    ("Доресерч після персон", "доресерч-після-персон", "Доресерч після персон"),
    ("Ручне проходження конкурентів 1 листопада", "ручне-проходження-конкурентів-1-листопада", "Ручне проходження 1 листопада"),
    ("Перевірка гіпотез JTBD у відкритих джерелах", "перевірка-гіпотез-jtbd-у-відкритих-джерелах", "Перевірка гіпотез JTBD"),
]
for number, (title, section_id, label) in enumerate(sections_to_show, 1):
    if title not in section_html:
        raise ValueError(f"Missing research section: {title}")
    parts.append(f'<section id="{section_id}" class="report-section" aria-labelledby="heading-{section_id}"><div class="section-title"><span class="section-number">{number:02d}</span><h2 id="heading-{section_id}">{label}</h2></div>{section_html[title]}{gallery if title == "КОНКУРЕНТИ" else ""}</section>')

html = """<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>Дослідження MVP · Догляд за котами й собаками</title>
  <meta name="description" content="Конкуренти, відгуки, форуми, власні проходження та гіпотези для застосунку догляду за котами й собаками.">
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
    .research-meta { max-width: 820px; margin: 22px 0 0; color: var(--muted); font-size: .92rem; }
    .mast-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 34px; }
    .mast-links a, .jump a { display: inline-flex; align-items: center; min-height: 38px; padding: 6px 13px; border: 1px solid #426658; border-radius: 99px; color: #d8f6e9; text-decoration: none; font-size: .88rem; }
    .mast-links a:hover, .jump a:hover { background: #214238; }
    .provenance { display: flex; flex-wrap: wrap; gap: 14px 22px; margin-top: 35px; color: var(--muted); font-size: .85rem; }
    .provenance span::before { content: ""; display: inline-block; width: 7px; height: 7px; margin-right: 8px; border-radius: 50%; background: var(--warm); vertical-align: 2px; }
    .provenance span:first-child::before { background: var(--accent); }
    .jump { display: flex; flex-wrap: wrap; gap: 10px; margin: 24px 0 0; }
    .jump a { border-color: var(--line); color: var(--muted); }
    .report-section { padding: 78px 0 88px; border-bottom: 1px solid var(--line); scroll-margin-top: 18px; }
    .source-section { padding: 68px 0 56px; border-bottom: 1px solid var(--line); scroll-margin-top: 18px; }
    .source-section > p { max-width: 74ch; color: var(--muted); }
    .source-table { table-layout: fixed; min-width: 760px; }
    .source-table thead th:nth-child(1) { width: 22%; }
    .source-table thead th:nth-child(2) { width: 49%; }
    .source-table thead th:nth-child(3) { width: 29%; }
    .source-table td { min-width: 0; }
    .section-title { display: flex; align-items: baseline; gap: 18px; margin-bottom: 30px; }
    .section-number { color: var(--accent); font: 600 1.04rem/1 ui-monospace, monospace; }
    h2 { margin: 0; font-size: clamp(2rem, 3vw, 3rem); line-height: 1.15; letter-spacing: -.045em; }
    .section-subtitle { max-width: 68ch; margin: 0 0 30px; color: #d3e3df; font-size: clamp(1.08rem, 1.4vw, 1.22rem); line-height: 1.55; }
    h3 { margin: 58px 0 22px; font-size: clamp(1.45rem, 2vw, 1.8rem); line-height: 1.25; letter-spacing: -.025em; }
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
    .competitor-group { display: block; margin-top: 5px; color: var(--muted); font-size: .8rem; font-weight: 400; line-height: 1.35; }
    tbody tr:nth-child(even) { background: #14222a; }
    td { min-width: 245px; color: #c6d3d3; }
    .conclusions-table { table-layout: fixed; min-width: 1040px; }
    .conclusions-table thead th:nth-child(1) { width: 38%; }
    .conclusions-table thead th:nth-child(2) { width: 44%; }
    .conclusions-table thead th:nth-child(3) { width: 18%; }
    .conclusions-table td { min-width: 0; }
    .conclusions-table tbody td:first-child { color: #d6e2df; }
    td a, th a { white-space: normal; }
    .evidence-head { margin-top: 70px; }
    .evidence-head h3 { margin: 0 0 12px; }
    .evidence-head p { max-width: 76ch; margin: 0; color: var(--muted); }
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
      <p class="lead">Дослідження догляду за котами й собаками: що вже зроблено, який препарат давали востаннє і що потрібно запланувати далі.</p>
      <p class="research-meta">Стан матеріалів: <time datetime="2026-11-01">1 листопада 2026 року</time>. Текст — <a href="research.md">research/research.md</a>, продуктовий бриф — <a href="../Codex.md">Codex.md</a>.</p>
      <div class="mast-links"><a href="research.md">Повний звіт у Markdown ↗</a><a href="../Codex.md">Продуктовий бриф ↗</a></div>
      <div class="provenance" aria-label="Типи джерел"><span>Власні тестові проходження</span><span>Публічні сторінки</span><span>Відгуки й форуми</span><span>Mobbin</span></div>
      <nav class="jump" aria-label="Розділи сторінки"><a href="#звідки-дані">Звідки дані</a><a href="#конкуренти">Конкуренти</a><a href="#бенчмарк">Бенчмарк</a><a href="#патерни">Патерни</a><a href="#висновки">Висновки</a><a href="#відгуки">Відгуки</a><a href="#форуми">Форуми</a><a href="#собаки">Коти й собаки</a><a href="#доресерч-після-персон">Доресерч</a><a href="#ручне-проходження-конкурентів-1-листопада">Ручне проходження</a><a href="#перевірка-гіпотез-jtbd-у-відкритих-джерелах">Гіпотези JTBD</a></nav>
    </header>
    <section id="звідки-дані" class="source-section" aria-labelledby="sources-heading">
      <h2 id="sources-heading">Звідки дані</h2>
      <p>Спостереження з тестових акаунтів відокремлено від відкритих джерел і прикладів Mobbin. Продуктовий бриф задає цілі та рішення, але не є доказом про ринок.</p>
      <div class="table-wrap" tabindex="0" aria-label="Походження матеріалів"><table class="source-table"><thead><tr><th scope="col">Позначка</th><th scope="col">Джерело</th><th scope="col">Як використано</th></tr></thead><tbody>
        <tr><th scope="row">Власне проходження</th><td>Записи екрана із тестових акаунтів, надані засновницею; <a href="#екрани-дослідження">опубліковані кадри</a> збережені у <code>screens/own/</code>. Введені дані вигадані. <a href="notes/06-android-flows.md">Флоу 29 жовтня</a>, <a href="notes/09-android-flows-2026-11-01.md">флоу 1 листопада</a>, <a href="notes/07-todoist-own.md">Todoist</a>.</td><td>Перевірені екрани й кроки сценарію. Коди запрошень та системні списки контактів не опубліковано.</td></tr>
        <tr><th scope="row">Публічне</th><td>Сайти, офіційні довідки, сторінки застосунків, відгуки й демо-відео без входу. Джерела перелічено у <a href="notes/03-competitors.md">відборі</a> та <a href="notes/04-matrix.md">матриці</a>; приклад — <a href="screens/felivo-detail-public-mobile.png">публічний кадр Felivo</a>.</td><td>Факти про заявлені функції та доступні без логіну екрани.</td></tr>
        <tr><th scope="row">Відгуки</th><td>Публічні відгуки в App Store та Google Play; <a href="#відгуки">добірка</a> нижче.</td><td>Окремі повідомлення про власний досвід, без вимірювання поширеності.</td></tr>
        <tr><th scope="row">Форуми</th><td>Першоособові дописи про догляд за <a href="notes/cat-care-forums.md">котами</a> і <a href="notes/dog-care-comparison.md">собаками</a>.</td><td>Способи ведення записів та випадки невизначеності, без оцінки частоти.</td></tr>
        <tr><th scope="row">Mobbin</th><td>Екрани сторонніх застосунків, переглянуті через підключення засновниці. <a href="notes/05-benchmark.md">Метод і джерела бенчмарку</a>.</td><td>Приклади UX-механізмів; це не проходження акаунтів у цих застосунках.</td></tr>
        <tr><th scope="row">Бриф</th><td><a href="../Codex.md">Codex.md</a> — цілі, аудиторія та продуктові рішення.</td><td>Основа оцінки й гіпотез, а не факт про конкурентів.</td></tr>
      </tbody></table></div>
    </section>
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
