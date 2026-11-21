import logging
import os
from functools import lru_cache

from django.conf import settings
from django.core.mail import send_mail
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation
from django.utils.html import escape
from django.utils.translation import gettext
from django.views.decorators.gzip import gzip_page
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View

from category.models import Category
from projects.models import Project

logger = logging.getLogger(__name__)

PRESENTATIONS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'static', 'presentations'
)

# Standalone HTML presentations, served at /presentations/<slug>. Only these slugs resolve, so a
# request can never name another file. Each deck carries its own language toggle (setLang); the
# page opens in the site's language: English at /presentations/..., Portuguese under /pt-br/.
DECKS = {
    'harness-software-engineering': 'harness-software-engineering.html',
    'organizational-intelligence': 'organizational-intelligence.html',
    'agentic-work-transition': 'agentic-work-transition.html',
}
DECK_LANGUAGE = {'pt-br': 'pt'}   # site language -> the decks' own code; anything else is 'en'
SITE_ORIGIN = 'https://ariedi.com'


class Home(TemplateView):

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.filter(active=True)
        context['categories'] = Category.objects.all()
        return context


class Presentations(TemplateView):

    template_name = "pages/presentations.html"


class Research(TemplateView):

    template_name = "pages/research.html"


@lru_cache(maxsize=None)
def read_deck(filename):
    with open(os.path.join(PRESENTATIONS_DIR, filename), encoding='utf-8') as deck:
        return deck.read()


def open_deck_in(html, deck_language):
    """Appends a call to the deck's own setLang before </body>, after the deck's script defines it.

    >>> open_deck_in('<body><script>function setLang(l){}</script></body>', 'pt')
    '<body><script>function setLang(l){}</script><script>if (typeof setLang === "function") setLang("pt");</script></body>'
    """
    opener = '<script>if (typeof setLang === "function") setLang("%s");</script>' % deck_language
    return insert_before(html, '</body>', opener)


def deck_links(slug, path):
    """The <head> links the site's other pages carry (_header.html): canonical, en, pt-BR, x-default."""
    def url_in(language):
        with translation.override(language):
            return SITE_ORIGIN + reverse('presentation_deck', args=[slug])
    return ('<link rel="canonical" href="%s%s">' % (SITE_ORIGIN, path)
            + '<link rel="alternate" hreflang="en" href="%s">' % url_in('en')
            + '<link rel="alternate" hreflang="pt-BR" href="%s">' % url_in('pt-br')
            + '<link rel="alternate" hreflang="x-default" href="%s">' % url_in('en'))


def deck_icons():
    """The site's favicon links (_header.html): the rings SVG, with the PNG as fallback and touch icon."""
    png, svg = static('images/favicons/fav2.png'), static('images/favicons/rings.svg')
    return ('<link rel="icon" href="%s" type="image/png">' % png
            + '<link rel="icon" href="%s" type="image/svg+xml">' % svg
            + '<link rel="apple-touch-icon" href="%s">' % png)


# The way back to the site from inside a deck: a small fixed pill in the brand's colours, bottom
# right, where none of the decks keeps anything (their navigation is a left rail on desktop and a
# sticky top bar on phones). Each link is 44 px tall.
RETURN_PILL_STYLE = (
    '#site-return{position:fixed;right:16px;bottom:16px;z-index:2147483000;display:flex;'
    'align-items:center;gap:10px;padding:0 14px;background:rgba(21,8,38,.94);'
    'border:1px solid #4A2A6B;border-radius:2px;box-shadow:0 6px 20px rgba(0,0,0,.35);'
    "font:500 12px/1 'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;"
    'letter-spacing:.06em;text-transform:uppercase}'
    '#site-return a{display:inline-block;padding:16px 0;color:#F1E9FB;text-decoration:none}'
    '#site-return a:hover,#site-return a:focus-visible{color:#B56BE8;text-decoration:underline}'
    '#site-return span{color:#CDB4F0}'
    '@media print{#site-return{display:none}}'
)


def deck_return_links():
    """The fixed pill back to the Presentations list and the home page, in the current language."""
    return ('<style>%s</style><nav id="site-return" aria-label="%s">'
            '<a href="%s">&larr; %s</a><span aria-hidden="true">&middot;</span><a href="%s">%s</a></nav>'
            % (RETURN_PILL_STYLE, 'ariedi.com',
               reverse('presentations'), escape(gettext('Presentations')),
               reverse('home'), escape(gettext('Home'))))


def insert_before(html, closing_tag, snippet):
    """Puts snippet just before the last closing_tag, or at the end when the tag is missing."""
    end = html.rfind(closing_tag)
    return html + snippet if end == -1 else html[:end] + snippet + html[end:]


@gzip_page   # a deck is 150-270 KB of HTML and holds no secrets, so compression is safe (no BREACH)
def serve_deck(request, slug):
    filename = DECKS.get(slug)
    if filename is None:
        raise Http404
    deck_language = DECK_LANGUAGE.get(request.LANGUAGE_CODE, 'en')
    # request.path is one of the allow-listed deck URLs, so it is safe to echo into the canonical
    html = insert_before(read_deck(filename), '</head>', deck_links(slug, request.path) + deck_icons())
    html = insert_before(html, '</body>', deck_return_links())
    return HttpResponse(open_deck_in(html, deck_language))


def serve_presentation(request, filename):
    filepath = os.path.join(PRESENTATIONS_DIR, filename)
    # PDFs only: the HTML decks share the folder and have their own route (serve_deck)
    if not filename.endswith('.pdf') or not os.path.isfile(filepath) or '..' in filename:
        raise Http404
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')


class SendMessage(View):
    def post(self, *args, **kwargs):
        try:
            name = self.request.POST.get('name', '')
            email = self.request.POST.get('email', '')
            message = self.request.POST.get('message', '')

            if not all([name, email, message]):
                return JsonResponse(
                    {'msg': 'Please fill in all fields.'},
                    status=400
                )

            subject = f"Msg from {name}, form in ariedi.com"
            full_message = f"From: {name} <{email}>\n\n{message}"

            # Check if email is configured
            if settings.EMAIL_HOST:
                send_mail(
                    subject,
                    full_message,
                    settings.EMAIL_HOST_USER or 'noreply@ariedi.com',
                    ['joaoariedi@gmail.com'],
                    fail_silently=False
                )
                return JsonResponse({'msg': 'Thanks! Your message was sent successfully.'})
            else:
                # Log the message if email is not configured
                logger.info(f"Contact form submission: {subject}\n{full_message}")
                return JsonResponse({'msg': 'Thanks! Your message was received.'})

        except Exception as e:
            logger.error(f"Error sending contact form: {e}")
            return JsonResponse(
                {'msg': 'Sorry, there was an error. Please try again or email me directly.'},
                status=500
            )
