import logging
import os
from functools import lru_cache

from django.conf import settings
from django.core.mail import send_mail
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
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
    end = html.rfind('</body>')
    return html + opener if end == -1 else html[:end] + opener + html[end:]


@gzip_page   # a deck is 150-270 KB of HTML and holds no secrets, so compression is safe (no BREACH)
def serve_deck(request, slug):
    filename = DECKS.get(slug)
    if filename is None:
        raise Http404
    deck_language = DECK_LANGUAGE.get(request.LANGUAGE_CODE, 'en')
    return HttpResponse(open_deck_in(read_deck(filename), deck_language))


@xframe_options_sameorigin
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
