from django.test import TestCase, override_settings
from django.urls import reverse

# Production uses WhiteNoise's manifest storage, which needs `collectstatic` to have run;
# the test runner has no manifest, so {% static %} would raise. Plain storage keeps the
# templates renderable without changing what the tests assert.
PLAIN_STATIC = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=PLAIN_STATIC)
class PublicPagesSmokeTest(TestCase):
    """Every public page renders, and the content brief's removals stay removed."""

    REMOVED_FROM_HOME = ["John Ariedi", "15+ years", "CISSP", "CISO", "9107", "paradigm shift"]

    def test_home_renders_with_current_identity(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("João Ariedi", body)
        self.assertIn('id="section-research"', body)
        self.assertIn('id="section-work"', body)
        for removed in self.REMOVED_FROM_HOME:
            self.assertNotIn(removed, body, f"{removed!r} must not appear on the home page")

    def test_research_page_lists_meistudies_entry(self):
        response = self.client.get(reverse("research"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('id="meistudies-2026"', body)
        self.assertIn("syntagm transition", body)
        self.assertIn("Why the full text is not published here yet", body)
        self.assertIn('id="simpep-2026"', body)
        self.assertIn("Organizational Maturity Framework", body)

    def test_presentations_page_renders(self):
        response = self.client.get(reverse("presentations"))
        self.assertEqual(response.status_code, 200)

    def test_seo_files_render(self):
        self.assertEqual(self.client.get("/robots.txt").status_code, 200)
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertIn("https://ariedi.com/research", sitemap.content.decode())
