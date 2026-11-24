"""The home page read for one need: "What do you need?" in the hero picks a version.

The default page is the blend (no profile). A version changes emphasis only: the About
paragraphs, the four "What I bring" cards, the order of the sections and the featured work.
Name, headline, dates and facts are the same on every version. Each version has its own URL
(/engineering, /security, /advisory, /ai-agents); the switcher (brand-profile.js) fetches a
version only when the visitor asks for it.
"""
from django.utils.translation import gettext_lazy as _

SECTIONS = ('started', 'about', 'services', 'history', 'research', 'talks', 'work', 'skills',
            'interests', 'motivation')


def _order(*lead):
    """The lead sections first (after the hero, About and the cards), the rest in the usual order."""
    head = ('started', 'about', 'services') + lead
    return head + tuple(s for s in SECTIONS if s not in head)


def section_templates(order=SECTIONS):
    return [f'pages/home/{name}.html' for name in order]


PROFILES = {
    'engineering': {
        'need': _('Scale an engineering team'),
        'about': (
            _('Engineering leader with 16 years in technology and 9+ leading teams. I lead engineering for a US cybersecurity company, where my team builds an endpoint management platform designed for 1M+ devices per enterprise customer.'),
            _('I led its redesign from a monolith to event-driven microservices in Go on AWS, architected the EDR backend, and earlier led the zero-downtime rebuild of Cloudways (2M+ WordPress installations). I run test-first teams with 90%+ retention and build the harnesses that make AI-assisted development reliable.'),
        ),
        'cards': (
            (_('Architecture'), _('Event-driven microservices, high-throughput asynchronous backends, legacy decomposition and zero-downtime migration.')),
            (_('Cloud and delivery'), _('AWS, Google Cloud, Kubernetes and Terraform; CI/CD with GitHub Actions, ArgoCD and Helm.')),
            (_('Teams'), _('Test-first delivery on Extreme Programming, 90%+ retention, engineers grown into leaders.')),
            (_('AI-assisted engineering'), _('Spec-driven development and agent harnesses with quality gates, so AI-written code stays reliable.')),
        ),
        'order': _order('history', 'skills', 'work'),
        'featured': 'hefesto',
    },
    'security': {
        'need': _('Secure a product'),
        'about': (
            _('Security engineering on the defensive side: incident response, compliance, and detection and endpoint products. At a US cybersecurity company I led the architecture of its EDR solution and now lead the team behind an endpoint management platform designed for 1M+ devices per enterprise customer.'),
            _("16 years in technology, 9+ leading engineering teams, with a degree in Cyber Defense. I bring an engineer's toolset to security operations: automation, tested pipelines and security designed into the architecture."),
        ),
        'cards': (
            (_('Incident response'), _('Incident response for a production security platform, with diagnosis down to OS, network and runtime level; external advisor to a client during a data-extortion incident.')),
            (_('Detection and endpoint engineering'), _('EDR architecture, endpoint management at scale, network detection appliances deployed in enterprise datacenters.')),
            (_('Security by design'), _('Certificate-based device authentication (mTLS), PKI, short-lived tokens and post-quantum cryptography readiness.')),
            (_('Compliance and assessment'), _('Auditability, data protection and access-control readiness for due diligence; penetration testing, forensics, pentest vendor selection and report review.')),
        ),
        'order': _order('history', 'work', 'skills'),
        'education_first': True,
        'featured': 'safesphere',
    },
    'advisory': {
        'need': _('Advise my company'),
        'about': (
            _('I lead engineering where scale, security and AI meet, and I advise companies facing the same: Brazilian technology companies as a partner and fractional CTO, and a quantitative trading firm from its board.'),
            _('AI moves the bottleneck from execution to judgment. I help founders and boards decide the order of investments, govern architecture, design the engineering organization and adopt AI without losing accountability.'),
        ),
        'cards': (
            (_('Strategy and roadmaps'), _('Order of investments, phase gates and readiness for institutional due diligence.')),
            (_('Architecture governance'), _('Reviewing and approving core architectures for scalability and business fit; cloud cost efficiency.')),
            (_('Engineering organization'), _('Org design, hiring sequence, interview frameworks and leadership vetting.')),
            (_('AI adoption'), _('AI harnesses for legacy modernization, Agile adapted to AI-assisted delivery, productivity metrics.')),
        ),
        'order': _order('history', 'talks', 'research'),
        'featured': 'xcube',
    },
    'ai-agents': {
        'need': _('Put AI agents into production'),
        'about': (
            _('I embed with a team, find the real problem and ship the production system that solves it. 16 years across software engineering, security, data, business intelligence and management let me talk to the CFO, the security lead and the engineers in their own terms.'),
            _('Today I lead engineering at a US cybersecurity company and work inside Brazilian companies on AI adoption, including harnesses that refactor a legacy codebase. Author of Hefesto, an open-source harness for AI coding agents.'),
        ),
        'cards': (
            (_('AI in production'), _('Agent harnesses, multi-agent orchestration, spec-driven development, agent evaluation and quality gates.')),
            (_('Software'), _('Go, Python and React; event-driven microservices on PostgreSQL, Kafka, RabbitMQ and Redis.')),
            (_('Data and BI'), _('Data pipelines, data warehouses, and OKR, KPI and KRI frameworks.')),
            (_('Into your environment'), _('AWS, Google Cloud, Kubernetes, Terraform and CI/CD, within your access controls and compliance requirements.')),
        ),
        'order': _order('work', 'research', 'history'),
        'featured': 'hefesto',
    },
}
for _slug, _profile in PROFILES.items():
    _profile['slug'] = _slug
