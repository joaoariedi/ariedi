from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib import admin

admin.autodiscover()

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("admin/", admin.site.urls),
    # SEO files
    path("robots.txt", TemplateView.as_view(template_name="seo/robots.txt", content_type="text/plain")),
    path("sitemap.xml", TemplateView.as_view(template_name="seo/sitemap.xml", content_type="application/xml")),
]

# English (the default) at "/", Portuguese at "/pt-br/": prefix_default_language=False keeps
# every existing English URL unchanged and stops LocaleMiddleware from redirecting visitors
# with a pt-BR browser away from the default.
urlpatterns += i18n_patterns(
    path("", include('pages.urls')),
    path("workshops/", include('workshops.urls')),
    prefix_default_language=False,
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
