"""Experience and focus areas of each version of the home page (see pages/profiles.py).

Adapted from the owner's four resumes: the same jobs, dates and facts as the default page, told
for one need. Where a resume and the site disagree, the site's wording stands (flugel.it as its
own entry, the FAPESP role, the Frons degree still in authorization). Sentences shared by several
versions are defined once, so they are translated once.
"""
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

PRESENT = _('Present')


def span(start, end=None):
    """'2021 - Present', '2021 - 2024' or '2016'."""
    return start if end is None else format_lazy('{} - {}', start, end)


def role(*bullets, title=None, period=None):
    return {'title': title, 'period': period, 'bullets': bullets}


def entry(date, name, small, *roles):
    return {'date': date, 'name': name, 'small': small, 'roles': roles}


def column(title, *entries):
    return {'title': title, 'entries': entries}


# ---- shared sentences ----
LEADS_PLATFORM = _('Lead the engineering team behind the next-generation endpoint management platform, a distributed system designed to securely manage 1M+ devices per enterprise customer.')
REDESIGN = _('Led the ground-up redesign of the endpoint agent platform, replacing a legacy monolith with event-driven microservices in Go on AWS.')
SECURITY_FIRST = _('Designed a security-first architecture: certificate-based device authentication (mTLS), short-lived token issuance and post-quantum cryptography readiness.')
OPERATIONS = _('Own engineering operations end to end: sprint planning, technical roadmaps, stakeholder alignment and incident response.')
EDR = _('Led the technical architecture of the EDR solution: React, Python (FastAPI), Go, PostgreSQL, RabbitMQ, Kafka, Redis, Kubernetes on AWS.')
CICD = _('Built the end-to-end CI/CD pipeline with Terraform, GitHub Actions, Docker, Kubernetes, ArgoCD and Helm.')
INCIDENTS = _('Diagnosed and resolved critical production incidents: Go async code analysis, networking bottlenecks, CPU and memory optimization, OS-level debugging.')
VECTRA = _('Deployed Vectra security appliances across enterprise datacenters, strengthening detection capabilities for key accounts.')
CLOUDWAYS = _('Led the complete rebuild of Cloudways, a hosting company acquired by DigitalOcean, supporting 2M+ WordPress and WooCommerce deployments, delivered on schedule with a zero-downtime migration.')
CLOUDWAYS_BACKEND = _('Architected its service-oriented Python backend on Django, PostgreSQL, FastAPI and Google Cloud (Cloud Run, Cloud Functions, Pub/Sub).')
RETENTION = _('90%+ team retention; mentored 3+ engineers into leadership roles.')
EXTORTION = _('External security advisor to a client during a data-extortion incident.')
PENTEST = _('Pentest vendor selection, rules of engagement and report quality review for client engagements.')
DATA_TEAM = _('Founded the data intelligence team and scaled it from zero to full operation; two analysts promoted to senior roles.')
PLATFORM_5K = _('Built an adaptive learning platform serving 5,000+ students.')
PEARSON = _('Delivered a learning-object migration project for Pearson on time and under budget.')
FAPESP = _('Member of the research team of a FAPESP-funded (PIPE) innovation project: a distributed network of environmental data-collection probes.')
TEACHING = _('MBA professor (Data Analysis and AI for Strategic Decisions); designated faculty for a new Technology degree in Artificial Intelligence, in its authorization process: Computer Architecture and Operating Systems; MLOps, Edge and Model Deployment.')

# ---- shared entries ----
BATUTA = ('Batuta', _('San Francisco, cybersecurity (Remote)'))
MANAGER = {'title': _('Software Engineering Manager'), 'period': span('2026', PRESENT)}
PRINCIPAL = {'title': _('Principal Software Engineer'), 'period': span('2021', '2025')}
FLUGEL_ROLES = format_lazy('{} · {}', _('Principal Software Engineer'), _('Senior Software Engineer'))
SCAFFOLD_ROLES = _('Intelligence Manager · Senior Market Intelligence Analyst · IT consultant')
BOARD = _('Board member and technology advisor')
CLIENTS = 'Lecom · Ikatec · IEV · AltynLabs'
FAPESP_ENTRY = entry('2016', _('São Paulo Research Foundation (FAPESP)'), _('Technology and Innovation Researcher'), role(FAPESP))
FRONS = entry(span('2024', PRESENT), 'Frons Educação', _('Professor, MBA'), role(TEACHING))
ELETRIZE_SHORT = entry(span('2013', '2017'), 'Eletrize', _('Co-founder and COO'), role(PLATFORM_5K, PEARSON))


ENGINEERING = (
    column(
        _('Engineering leadership'),
        entry(span('2021', PRESENT), *BATUTA,
              role(LEADS_PLATFORM, REDESIGN, SECURITY_FIRST,
                   _('Drive delivery with Extreme Programming and test-first discipline; every architectural decision is backed by documented tests.'),
                   OPERATIONS,
                   _('Recruit and mentor engineers who own features end to end, with 90%+ team retention.'),
                   **MANAGER),
              role(EDR,
                   _('Architected high-throughput asynchronous Go and Python backends handling thousands of concurrent connections.'),
                   CICD, INCIDENTS, **PRINCIPAL)),
        entry(span('2021', '2024'), 'flugel.it', FLUGEL_ROLES,
              role(CLOUDWAYS, CLOUDWAYS_BACKEND,
                   _('Designed a microservices architecture for WordPress application orchestration on Kubernetes, enabling horizontal scaling.'),
                   _('Established Python best practices and code review processes adopted across the engineering team.'),
                   _('Mentored 3+ engineers into leadership roles; engineers I recruited advanced to senior roles.'))),
    ),
    column(
        _('Advisory, data and founding'),
        entry(span('2026', PRESENT), _('Advisory and consulting'), CLIENTS,
              role(_('Software Engineering Advisor to Lecom, Ikatec and IEV (acting as fractional CTO at IEV); consultant to AltynLabs, an AI-first lab.'),
                   _('Define AI harnesses to refactor legacy codebases and reduce technical debt; review and validate system architectures; set engineering productivity metrics.'))),
        entry(span('2023', PRESENT), 'xCube', BOARD,
              role(_('Review architecture and stack decisions across the analytics backend, web platform, data layer and self-hosted infrastructure.'))),
        entry(span('2018', '2024'), 'Scaffold Education', SCAFFOLD_ROLES,
              role(DATA_TEAM,
                   _('Engineered data collection, monitoring and integration pipelines across all transactional systems.'))),
        entry(span('2021', '2023'), 'Kodus', _('Data science and software engineering mentor'),
              role(_('Trained the team in data mining, regression and NLP; guided data warehouse design; 4+ mentees launched production data products.'))),
        FRONS, FAPESP_ENTRY, ELETRIZE_SHORT,
    ),
)

SECURITY = (
    column(
        _('Security engineering'),
        entry(span('2021', PRESENT), *BATUTA,
              role(LEADS_PLATFORM, SECURITY_FIRST,
                   _('Own engineering operations end to end, including incident response, compliance, and SOC automation and implementation.'),
                   REDESIGN,
                   _('Maintain 90%+ team retention with a test-first culture where every architectural decision is backed by evidence.'),
                   **MANAGER),
              role(EDR, VECTRA, INCIDENTS, CICD, **PRINCIPAL)),
        entry(_('Security advisory'), 'Safesphere', 'safesphere.com.br',
              role(EXTORTION, PENTEST,
                   _('Advisor and builder of a digital-security service for families.'))),
        entry(span('2021', '2024'), 'flugel.it', FLUGEL_ROLES, role(CLOUDWAYS)),
    ),
    column(
        _('Advisory and earlier'),
        entry(span('2023', PRESENT), 'xCube', BOARD,
              role(_('Advise on security posture and the controls needed before outside users are onboarded: auditable scoring, data protection, observability and access controls.'))),
        entry(span('2026', PRESENT), _('Advisory and consulting'), CLIENTS,
              role(_('Architecture governance and validation, AI harnesses for legacy modernization, engineering metrics.'))),
        entry(span('2018', '2024'), 'Scaffold Education', SCAFFOLD_ROLES,
              role(_('Built data monitoring pipelines and risk indicators (KRIs).'))),
        FRONS, FAPESP_ENTRY, ELETRIZE_SHORT,
    ),
)

ADVISORY = (
    column(
        _('Advisory and board experience'),
        entry(span('2026', PRESENT), 'Lecom', _('Software Engineering Advisor'),
              role(_('Lead engineering modernization: AI harnesses built to refactor legacy codebases and reduce technical debt.'),
                   _('Adapt legacy engineering workflows and Agile practice to AI-assisted delivery.'),
                   _('Implement metric frameworks to measure developer velocity and baseline organizational output.'))),
        entry(span('2026', PRESENT), 'Ikatec', _('Software Engineering Advisor'),
              role(_('Advise on technical governance, project management and infrastructure cost efficiency.'),
                   _('Audit and validate system designs for scalability while optimizing cloud and operational costs.'),
                   _('Set engineering productivity goals for predictable, high-quality delivery.'))),
        entry(span('2026', PRESENT), 'AltynLabs', _('Consultant to an AI-first lab'),
              role(_('Advise on AI maturity and company-wide AI adoption.'),
                   _('Guide teams in automating their processes and in the secure use of AI.'),
                   _('Define the new skills and competences the current working paradigm requires.'),
                   _("Hire managers, engineers and interns for the company's teams."))),
        entry(span('2023', PRESENT), 'xCube', BOARD,
              role(_('Advise on the technology roadmap for moving from a proprietary desk to a go-to-market company: order of investments, phase gates, readiness for institutional due diligence.'),
                   _('Prioritize the capabilities that build investor trust: reproducible, auditable scoring, data protection, observability and access controls.'),
                   _('Define the first engineering roles, the profiles to look for and the hiring sequence.'))),
        entry(span('2026', PRESENT), 'IEV', _('Software Engineering Advisor, acting as fractional CTO'),
              role(_('Bridge executive vision and engineering strategy to future-proof core technology and organizational growth.'),
                   _('Review, validate and approve core system architectures for long-term scalability and alignment with business objectives.'),
                   _('Advise on engineering org design, interview frameworks and vetting of leadership talent.'),
                   _('Define AI engineering harnesses that automate development workflows.'))),
    ),
    column(
        _('Executive and leadership experience'),
        entry(span('2021', PRESENT), *BATUTA,
              role(LEADS_PLATFORM, REDESIGN, OPERATIONS, RETENTION,
                   title=format_lazy('{} · {}', _('Software Engineering Manager'), _('Principal Software Engineer')))),
        entry(span('2021', '2024'), 'flugel.it', FLUGEL_ROLES, role(CLOUDWAYS)),
        entry(span('2018', '2024'), 'Scaffold Education', SCAFFOLD_ROLES,
              role(DATA_TEAM,
                   _('Built a centralized information pipeline giving every management level actionable insight.'),
                   _('Implemented the performance management framework (OKRs, KPIs, KRIs).'),
                   _('Automated competitive intelligence, delivering weekly market positioning reports to executive leadership.'))),
        entry(span('2013', '2017'), 'Eletrize', _('Co-founder and COO'),
              role(_('Co-founded an edtech serving 5,000+ students with an adaptive learning platform for college entrance exam preparation.'),
                   _('Led strategic planning, product roadmap and administrative operations from inception to growth stage.'),
                   PEARSON)),
        entry(span('2024', PRESENT), 'Frons Educação', _('Professor, MBA'),
              role(_('Professor in the MBA in Strategic Management, Operational Excellence and Agile Methods, teaching Data Analysis and AI for Strategic Decisions.'))),
        entry(span('2016', '2023'), _('Earlier'), None,
              role(_('Mentor, Kodus (2021 - 2023) · Co-founder, AEON Fablab (2016 - 2018) · research team member, FAPESP-funded innovation project (2016).'))),
    ),
)

AI_AGENTS = (
    column(
        _('Customer deployments'),
        entry(span('2026', PRESENT), CLIENTS, _('Embedded engineering advisor · Brazil'),
              role(_('Lecom: define and tune AI harnesses that refactor a legacy codebase and reduce technical debt; set the metrics that measure developer velocity.'),
                   _('Ikatec: audit and validate system designs for scalability while optimizing cloud and operating costs.'),
                   _('IEV: act as fractional CTO; review and approve core architectures and structure the interview framework for engineering hires.'),
                   _('AltynLabs: guide teams in automating their processes with AI and in using it securely.'))),
        entry(span('2021', '2024'), 'Cloudways (DigitalOcean)', _('Delivered through flugel.it'),
              role(CLOUDWAYS,
                   _('Translated technical constraints into roadmap changes with product stakeholders.'),
                   CLOUDWAYS_BACKEND)),
        entry(span('2021', PRESENT), _('Batuta enterprise accounts'), _('In customer environments'),
              role(VECTRA,
                   _('Diagnosed and resolved critical production incidents down to OS, network and runtime level.'))),
        entry(span('2023', PRESENT), 'xCube', BOARD,
              role(_('Shape the technology roadmap for moving from a proprietary desk to a go-to-market company, including readiness for institutional due diligence.'))),
        entry(_('Security advisory'), _('Safesphere clients'), 'safesphere.com.br', role(EXTORTION, PENTEST)),
    ),
    column(
        _('Product engineering'),
        entry(span('2021', PRESENT), *BATUTA,
              role(LEADS_PLATFORM, REDESIGN,
                   _('Architected the EDR solution and built the CI/CD pipeline it ships through.'),
                   RETENTION,
                   title=format_lazy('{} · {}', _('Software Engineering Manager'), _('Principal Software Engineer')))),
        entry(span('2018', '2024'), 'Scaffold Education', SCAFFOLD_ROLES,
              role(_('Built the data intelligence team from zero; engineered data pipelines across all transactional systems and the OKR, KPI and KRI framework management ran on.'))),
        ELETRIZE_SHORT, FRONS,
    ),
)

# ---- the resume's side column: what each version leads with ----
FOCUS = {
    'engineering': (_('Core skills'), (
        (_('Languages and frameworks'), 'Go · Python (FastAPI, Django) · JavaScript · React'),
        (_('Architecture'), _('Event-driven microservices · High-throughput async backends · Legacy decomposition · Zero-downtime migration')),
        (_('Data and messaging'), 'PostgreSQL · Redis · Kafka · RabbitMQ · Pub/Sub'),
        (_('Cloud and delivery'), 'AWS · Google Cloud (Cloud Run, Cloud Functions) · Kubernetes · Docker · Terraform · GitHub Actions · ArgoCD · Helm'),
        (_('Security by design'), _('mTLS · Certificate-based device authentication · Short-lived tokens · Post-quantum readiness')),
        (_('Engineering practice'), _('Extreme Programming · Test-first delivery · Spec-driven development · AI agent harnesses')),
    )),
    'security': (_('Focus areas'), (
        (_('Incident response'), _('Incident response for a production security platform; critical incidents diagnosed down to OS, network and runtime level; external advisor during a client data-extortion incident.')),
        (_('Blue team engineering operations'), _('EDR architecture, endpoint management at scale, network detection (Vectra) deployed in enterprise datacenters.')),
        (_('SOC automation and implementation'), _('Day to day across detection and response, log analytics, case management and response automation, cloud posture, code security and AI-driven security testing.')),
        (_('Compliance'), _('Day-to-day compliance work, including cloud compliance checks; auditability, data protection and access-control readiness for due diligence.')),
        (_('Security by design'), _('Certificate-based device authentication (mTLS), PKI, short-lived tokens, post-quantum cryptography readiness.')),
        (_('Assessment'), _('Penetration testing, digital forensics, pentest vendor selection and report review.')),
        (_('Engineering base'), 'Go · Python · Kubernetes · AWS · Google Cloud · Terraform · GitHub Actions · ArgoCD · Kafka · RabbitMQ'),
    )),
    'advisory': (_('What I bring'), (
        (_('Strategy and roadmaps'), _('Order of investments, phase gates, readiness for institutional due diligence.')),
        (_('Architecture governance'), _('Reviewing and approving core architectures for scalability and business fit; cloud cost efficiency.')),
        (_('Engineering organization'), _('Org design, hiring sequence, interview frameworks, leadership vetting; 90%+ retention in my own teams.')),
        (_('AI adoption'), _('AI harnesses for legacy modernization, Agile adapted to AI-assisted delivery, productivity metrics.')),
        (_('Security posture'), _('Security by design, data protection, access controls, incident response.')),
        (_('Performance management'), _('OKRs, KPIs, KRIs and the data pipelines behind them.')),
    )),
    'ai-agents': (_('What I deploy'), (
        (_('AI in production'), _('Agent harnesses · Multi-agent orchestration · Spec-driven development · Agent evaluation · Quality gates')),
        (_('Software'), _('Go · Python (FastAPI, Django) · React · Event-driven microservices · PostgreSQL · Kafka · RabbitMQ · Redis')),
        (_('Data and BI'), _('Data pipelines · Data warehouses · OKR, KPI and KRI frameworks')),
        (_("Into the customer's environment"), _('AWS · Google Cloud · Kubernetes · Terraform · CI/CD · mTLS · Access controls · Compliance requirements')),
        (_('Domains I speak'), _('Cybersecurity · Quantitative finance · Education · Enterprise software')),
    )),
}

EXPERIENCE = {'engineering': ENGINEERING, 'security': SECURITY, 'advisory': ADVISORY, 'ai-agents': AI_AGENTS}
