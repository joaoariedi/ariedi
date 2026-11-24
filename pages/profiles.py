"""The home page read for one need: "What do you need?" in the hero picks a version.

The default page is the blend (no profile, "Just exploring"). A version follows one of the
owner's four resumes: its profile paragraph, its side column (the focus table, in the Skills
section, moved up beside the profile), its experience (pages/experience.py), the order of the
sections (one order for all versions) and the featured work. Name, headline, dates and facts are
the same on every version.
Each version has its own URL (/engineering, /security, /advisory, /ai-agents); the switcher
(brand-profile.js) fetches a version only when the visitor asks for it.
"""
from django.utils.translation import gettext_lazy as _

from .experience import EXPERIENCE, FOCUS

SECTIONS = ('started', 'about', 'services', 'history', 'research', 'talks', 'work', 'skills',
            'interests', 'motivation')


# Every version has the same order, so choosing another moves nothing: the profile, the resume's
# side column (the Skills section, moved up beside the profile), the experience, then the rest
# as on the blend.
VERSION_ORDER = ('started', 'about', 'skills', 'history', 'services', 'work', 'research', 'talks',
                 'interests', 'motivation')


def section_templates(order=SECTIONS):
    return [f'pages/home/{name}.html' for name in order]


PROFILES = {
    'engineering': {
        'need': _('Scale an engineering team'),
        'about': (
            _('Engineering leader with 16 years in technology and 9+ leading teams. I lead engineering for a US cybersecurity company, where my team builds an endpoint management platform designed for 1M+ devices per enterprise customer.'),
            _('I led its redesign from a monolith to event-driven microservices in Go on AWS, architected the EDR backend, and earlier led the zero-downtime rebuild of Cloudways (2M+ WordPress installations). I run test-first teams with 90%+ retention and build the harnesses that make AI-assisted development reliable.'),
        ),
        'featured': 'hefesto',
    },
    'security': {
        'need': _('Secure a product'),
        'about': (
            _('Security engineering on the defensive side: compliance, incident response, blue team engineering operations, and SOC automation and implementation. At a US cybersecurity company I led the architecture of its EDR solution and now lead the team behind an endpoint management platform designed for 1M+ devices per enterprise customer.'),
            _("16 years in technology, 9+ leading engineering teams, with a degree in Cyber Defense. I bring an engineer's toolset to security operations: automation, tested pipelines and security designed into the architecture."),
        ),
        'featured': 'safesphere',
    },
    'advisory': {
        'need': _('Advise my company'),
        'about': (
            _('I lead engineering where scale, security and AI meet, turning business intent into systems that hold under load and building the teams behind them. 16 years in technology, 9+ leading engineering teams.'),
            _('Today I lead engineering for a US cybersecurity company, advise Brazilian technology companies as a partner and fractional CTO, sit on the board of a quantitative trading firm, and teach in MBA programs. AI moves the bottleneck from execution to judgment: I build the harness and the organization that keep that judgment in the right place.'),
        ),
        'featured': 'xcube',
    },
    'ai-agents': {
        'need': _('Put AI agents into production'),
        'about': (
            _('I embed with a team, find the real problem and ship the production system that solves it. 16 years across software engineering, security, data, business intelligence and management let me talk to the CFO, the security lead and the engineers in their own terms.'),
            _('Today I lead engineering at a US cybersecurity company and work inside Brazilian companies on AI adoption, including harnesses that refactor a legacy codebase. Author of Hefesto, an open-source harness for AI coding agents.'),
        ),
        'featured': 'hefesto',
    },
}
for _slug, _profile in PROFILES.items():
    _profile['slug'] = _slug
    _profile['experience'] = EXPERIENCE[_slug]
    _profile['focus_title'], _profile['focus'] = FOCUS[_slug]
