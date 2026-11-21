from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostRedirectMiddleware:
    """301 every request whose host is not settings.CANONICAL_HOST to the canonical https URL.

    Inactive while CANONICAL_HOST is empty. Sits before WhiteNoise so static files are
    redirected too; the ACME challenge path never reaches Django (Heroku's router answers it).

    Example: with CANONICAL_HOST="ariedi.com", GET http://www.ariedi.com/research?x=1
    -> 301 https://ariedi.com/research?x=1
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.canonical_host = settings.CANONICAL_HOST

    def __call__(self, request):
        if self.canonical_host and request.get_host() != self.canonical_host:
            return HttpResponsePermanentRedirect(
                f"https://{self.canonical_host}{request.get_full_path()}"
            )
        return self.get_response(request)
