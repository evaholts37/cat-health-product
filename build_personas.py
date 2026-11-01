"""Render persona and JTBD sections from their Markdown sources."""

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


def render_persona_sections() -> str:
    return f'''
    <section id="персони" class="report-section" aria-labelledby="personas-heading">
      <div class="section-title"><h2 id="personas-heading">Персони</h2><a class="section-back" href="#ресерч">До ресерчу ↑</a></div>
      <p class="section-intro">Поділ за поведінкою. Primary позначено кольором; кожна картка зберігає контекст, jobs, болі, тригери довіри, цитату й джерела з <a href="personas.md">personas.md</a>. Це робочі моделі з якісного ресерчу, а не підтверджені сегменти українського ринку; позначки [?] та «гіпотеза» збережено.</p>
      <div class="persona-stack">{''.join(persona_html)}</div>
      <div class="note">{paragraphs(why_primary)}</div>
    </section>

    <section id="jobs" class="report-section" aria-labelledby="jobs-heading">
      <div class="section-title"><h2 id="jobs-heading">Ієрархія jobs</h2></div>
      <div class="main-job"><span class="eyebrow">MAIN JOB · J0</span><blockquote>{inline(main_quote.group(1))}</blockquote>{paragraphs(main_explanation)}</div>
      <div class="job-group"><h3>Related jobs · J1–J5</h3><div class="job-grid">{job_cards(related_items, 'J')}</div></div>
      <div class="job-group"><h3>Emotional jobs · E1–E2</h3><div class="job-grid">{job_cards(emotional, 'E')}</div></div>
      <div class="job-group"><h3>Social jobs · S1–S2</h3><div class="job-grid">{job_cards(social, 'S')}</div></div>
      <div class="job-group hypothesis-group"><h3>Перевірювані jobs · H1–H4</h3><p class="section-intro">Частину потреб підтверджено окремими свідченнями. Позначка [?] лишається там, де даних про людей або наше рішення бракує.</p><div class="job-grid">{job_cards(hypotheses, 'H')}</div></div>
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
'''
