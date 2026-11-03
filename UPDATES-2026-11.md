# Site updates, November 2026

Brief for the session working in this repository. It lists every change the site at
https://ariedi.herokuapp.com needs to match João's current resume and positioning, with the facts
checked against his career record. Written 03/11/2026 from the vault at
`/home/ariedi/Desktop/ppgmit` (read-only from here; the vault is the source of truth).

**Sources of truth, in order:**
1. `/home/ariedi/Desktop/ppgmit/resume/general/career.md`: every fact, with evidence pointers, the
   positioning sentences, and the brand.
2. `/home/ariedi/Desktop/ppgmit/resume/applications/anthropic-residency/ariedi_anthropic_residency_resume.html`:
   the resume in the Blueprint brand, the wording to reuse.
3. `/home/ariedi/Desktop/ppgmit/resume/linkedin/linkedin_about_20261101.txt`: the About text (English,
   under 2,000 characters), already approved.

**Where the current content lives in this repo** (found 03/11/2026): the hero and About are in
`pages/templates/pages/home.html` and `templates/includes/_header.html`; the look comes from the
theme's `pages/static/css/layout.css` with `pages/static/css/theme-colors/red.css`; projects and
workshops are database models (`projects/`, `workshops/`) edited through the admin or fixtures.

## 1. Identity and positioning

| Now on the site | Change to |
|---|---|
| "John Ariedi" in headers, "João" in places | **João Ariedi** everywhere. The `<title>` too. "John" may survive only in the pronunciation hint, if one is added. |
| "Engineering Leader and Cybersecurity Expert based in Brazil" | **Engineering leader · Builder of AI agent harnesses · Researcher on AI and the competences of technical work** (the resume headline). Keep "based in Brazil, remote" as a sub-line. |
| Taglines: "I architect scalable systems / I lead engineering teams / I build secure software" | Keep three lines, replace with the current positioning: **I lead engineering at scale · I build the harnesses that let AI agents build software · I research what AI does to the people who use it** |
| About: "I bridge product vision and engineering execution… 15 years in tech and 9 years leading… CISSP knowledge" | Replace the whole paragraph with the LinkedIn About (source 3). It carries the thesis: AI moves the bottleneck from execution to judgment; engineering now builds the machine that builds the product. |
| "15+ years in tech" | **16 years** (since 2010), **9+ leading engineering teams**, **the last decade spanning organizational intelligence and cyber defense**. |
| "CISSP knowledge" | **Remove.** He holds no CISSP; the honest line is "Technologist in Cyber Defense (FIAP) with five professional qualifications". Same for any "CISO" wording. |
| Motivation: "I bridge product vision…" | Replace with the thesis sentence: *AI moves the bottleneck of engineering from execution to judgment. Engineering is no longer building the product directly, but building the machine that builds, improves and maintains it.* |

## 2. Services

Keep four cards, retitled and reordered to the stated priority (engineering leadership, board advisory,
consulting, teaching):

1. **Engineering leadership**: teams at scale, 90%+ retention, engineers grown into leaders, test-first
   culture. (keep)
2. **Advisory and board work**: partner and advisor to Brazilian technology companies on strategy,
   architecture governance and AI adoption; co-founder and former COO of an edtech. (new)
3. **Consulting and fractional CTO**: architecture governance, engineering org design, AI harnesses for
   legacy modernization, productivity metrics, infrastructure cost efficiency. (new; replaces "Cloud &
   DevOps", whose content moves into Skills)
4. **Teaching and research**: MBA guest professor; research on AI agents and engineering competence,
   paper accepted at MEISTUDIES 2026. (new; replaces "Software Architecture", folded into 1 and 3)

Cybersecurity stays visible as a thread through 1 and 3 and in the Skills block, not as a service card,
unless he wants to sell security consulting explicitly.

## 3. Experience, entry by entry

| Now | Change to |
|---|---|
| Batuta, 2021–Present, two roles, "serving 1M+ endpoints" | Keep the two roles. Wording: *Software Engineering Manager (2026 → now): leads the team behind an endpoint detection and response platform managing 1M+ devices per enterprise customer; event-driven architecture in Go on AWS; mTLS and certificate-based device authentication; post-quantum readiness.* *Principal Software Engineer (2021 → 2025).* Note the second role ends 12/2025, not 2026. |
| missing | **Add flugel.it (2021 → 2024)**, Principal and Senior Software Engineer: *led the full rebuild of Cloudways (DigitalOcean), which runs 2M+ WordPress and WooCommerce installations, migrated with zero downtime; Python (Django, FastAPI, PostgreSQL) on Google Cloud; Kubernetes.* An earlier commit merged it into Batuta; the two were simultaneous and both are real, so show both. |
| missing | **Add Advisory and consulting (2026 → now)**: fractional CTO at IEV; engineering consultant at Lecom and Ikatec; consultant to AltynLabs, an AI-first lab; partner and advisor to Brazilian technology companies. |
| Frons, 2024–Present, "Guest Lecturer (MBA)" | Keep; "Guest professor". Add: *mentored data science and engineering teams at Kodus (2021 → 2023)*. |
| Scaffold, 2018–2024, "Intelligence Manager/IT Consultant… OKRs" | Keep; add the three roles and the line *organizational intelligence: turning information into decision*. |
| "2016: Technology and Innovation Researcher – FAPESP, 10+ locations" | Reframe as **team member of a FAPESP PIPE research project** (distributed network of environmental data probes), within the Eletrize years. The vault does not record "10+ locations"; keep it only if he confirms it. |
| Eletrize, 2013–2017, "5,000+ students… gamification" | Keep co-founder and COO; *adaptive learning platform on item response theory, serving Pearson Brasil*. "5,000+ students" and "gamification" are not in the vault; keep only if he confirms. |
| missing | **Add AEON Fablab, Bauru (2016 → 2018)**, co-founder: digital fabrication lab, Fab Charter member, ten founders from programming, physics, design, carpentry and biology; BruHack 2017 workshop. This is the origin of the research line; it belongs on the site. |

## 4. Education

| Now | Change to |
|---|---|
| "2024–2025: Cybersecurity, Ethical Hacking, Forensics and DevOps – FIAP" | **Tecnólogo em Defesa Cibernética (Cyber Defense), FIAP, 2024 → 2025**, 2,000 h, MEC-recognised. Certifications go to their own line: *Certified Cybersecurity Professional, Information Security Officer, Certified Information Security Manager, Penetration Testing, Certified Forensics Professional (FIAP, 2024 and 2025); AWS Partner accreditations: Technical, Cloud Economics Essentials, Sales (2023).* |
| "2018–2022: Industrial Engineering – UNESP" | Keep ("Production Engineering" is the literal name); mark **coursework**. |
| "2010–2013: Physics Degree – UNESP" | **2010 → 2014**, Physics teaching degree, **coursework**. |
| missing | **Add: UNESP, PPGMIT (Media and Technology), master's application 2026, in selection**; from 16/12/2026 update to the result. |

## 5. New section: Research and publications

Add a section (or a page) with three entries, wording from the resume:

- **2026 · article**: *Democratizando a fabricação digital em Fab Labs: efeitos cognitivos das interfaces
  agênticas no projeto*, with Dorival Campos Rossi (UNESP), 9th International Congress Media Ecology and
  Image Studies (MEISTUDIES). Accepted Aug 2026, full text submitted Oct 2026, presented Nov 2026. One-line
  gloss: the *syntagm transition*, agentic interfaces absorb whole links of the design chain.
- **2026 · paper**: *A cultura organizacional na transformação de organizações tradicionais em
  organizações AI first*, second author of four, XXXIII SIMPEP, Bauru, Nov 2026. The PDF to host is
  `/home/ariedi/Desktop/ppgmit/papers/simpep/sources/simpep_2026_resumo_expandido.pdf` (six pages; the
  byline prints "Joao Carlos Ariedi", which is the paper's own spelling, keep it).
- **2026 → · master's pre-research**: PPGMIT, UNESP Bauru: an LLM-based agentic interface for a
  university Fab Lab's laser cutter, measuring access, artifact quality, knowledge retention and which
  competence profiles become productive.

Links: ORCID 0009-0002-1761-065X (works still to be added there), Lattes 5349307117993807.

## 6. Projects (the `projects` app)

Make **Hefesto** the first and featured project:

- Title: *Hefesto, a development harness for Claude Code*. Link https://github.com/joaoariedi/hefesto.
- Text: *A spec-driven workflow, specialist agents and quality gates enforced by hooks rather than by
  good intentions: the agent cannot skip tests, weaken assertions, commit secrets or run a destructive
  command, because a hook exits non-zero. 27 commands, 7 specialist agents, 16 hooks, deterministic
  workflows with adversarial verification, multi-session orchestration over a shared ledger. MIT,
  v9.1.3.* (numbers from the README of 01/11/2026; re-read the README when publishing.)
- Second link: the presentation *Harness Software Engineering*,
  https://github.com/joaoariedi/hefesto/blob/main/hefesto-sdlc.html.
- Icon: `docs/brand/hefesto-icon-*.svg` in that repository, recolored to the brand below.

Then: **Safesphere** (https://www.safesphere.com.br, digital-security service for families) and
**xCube** (https://xcube.finance, quantitative Forex research and execution framework validated on real
broker execution), with his role stated as he defines it (advisor and builder; not yet in the vault).
The "modern engineering presentation PDF" the last commits updated can stay as a third item or be
replaced by the Hefesto presentation.

## 7. Skills

Replace the percentage bars (Main Skills, Coding Skills) with grouped lists, no numbers; percentages
read as a 2015 template and invite argument. Use the resume's five groups:

- **Engineering**: Go, Python (Django, FastAPI), JavaScript/Node, React · PostgreSQL, Redis · Kafka,
  RabbitMQ · Kubernetes, AWS, Google Cloud, Terraform · event-driven and service-oriented architecture,
  CI/CD, test-first.
- **Security**: EDR architecture, mTLS and PKI, certificate-based device authentication, post-quantum
  readiness, penetration testing, forensics.
- **AI engineering**: Claude Code harness design, spec-driven development, multi-agent orchestration,
  hook-enforced quality gates, agent evaluation.
- **Intelligence**: business and market intelligence, data pipelines, BI, knowledge management, OKRs.
- **Fabrication**: laser cutting, 3D printing, Fab Lab operation.

Knowledge Areas can merge into these; drop duplicates (Protobuf/gRPC appears twice).

## 8. Languages, interests, contacts

- Languages: Portuguese (native), English (bilingual at work), Spanish (reading). **Chinese 15%** is not
  in the record; drop unless he wants it.
- Interests: keep the home lab (2 Proxmox nodes), classical guitar and strategy games; add **digital
  fabrication**. These lines are the human side the research section now explains.
- Contacts: e-mail, LinkedIn, GitHub, ORCID. **Remove the phone and the street address from the public
  page**; the vault keeps those out of anything public by decision.

## 9. Brand: the Blueprint night sheet

The site is a screen, so it takes the dark companion of the Blueprint brand decided on 03/11/2026 (the
light sheet is for paper). Replace the theme's red color file with these tokens; keep the theme's layout
if it serves, but the look must change.

```css
:root {
  --bg: #0A1324;            /* deep navy ground */
  --paper: #101C36;         /* cards and panels */
  --grid: rgba(157,184,240,0.08);   /* faint drafting grid, 18px */
  --ink: #E6EDF8;           /* text */
  --muted: #9DB8F0;         /* labels, secondary text */
  --line: #243B66;          /* rules */
  --blue: #3B82C4;          /* blueprint blue, secondary accent */
  --accent: #FF6A2A;        /* the orange hazard stripe, the only hot color */
  --accent-soft: #2A1A12;
  --link: #7FB0FF;
  --display: "Chakra Petch", "Segoe UI", Arial, sans-serif;   /* title block, headings, caps, tracked */
  --body: "IBM Plex Sans", system-ui, Arial, sans-serif;
  --mono: "IBM Plex Mono", Consolas, monospace;               /* labels, dates, data */
}
```

Gestures, used sparingly: the orange hazard stripe (`repeating-linear-gradient(90deg, #FF6A2A 0 10px,
transparent 10px 16px)`, 3px) under the name and nowhere else on the page; one featured card with a
hard offset shadow (`box-shadow: 3px 3px 0 var(--blue)`); section eyebrows in Chakra Petch caps with a
10px orange square; dates and labels in mono. No glow, no gradients beyond the stripe, no percentages.
Light-sheet tokens, for any printable page: `--bg #EEF2F7, --paper #F8FAFD, --ink #0F2A5F,
--muted #5A6A8C, --line #C5D0E2, --accent #FF6A2A, --link #1D5FB4`.

Fonts from Google Fonts:
`https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap`

## 10. Removals

"John Ariedi"; "15+ years"; "CISSP knowledge"; the percentage bars; the phone and street address;
"Technology and Innovation Researcher – FAPESP" as a standalone role; any "paradigm shift" wording (his
own research argues it is a syntagm transition, not a paradigm shift).

## 11. Checks before deploying

- Every number on the page appears in `career.md` or is confirmed by him: 16 / 9+ / 1M+ / 2M+ / 27 /
  7 / 16 / v9.1.3.
- The name is João Ariedi in the `<title>`, the header, the About and the footer.
- No phone or address in the HTML or the contact form's default text.
- Fonts load (check the network tab: Chakra Petch, Plex Sans, Plex Mono); the page reads at phone
  width without horizontal scroll.
- Lighthouse accessibility: contrast of `--muted` on `--bg` is above 4.5:1 (it is, at 7.6:1); links are
  distinguishable from text.
- Update the `README.md` tagline from "Engineering Leader & Cybersecurity Expert" to the new headline.
