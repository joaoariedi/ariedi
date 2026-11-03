from django.test import TestCase, override_settings
from django.utils import translation

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

    # LocaleMiddleware leaves the last request's language active on the test thread, so a
    # test that hits /pt-br/ would make the next test's reverse() emit Portuguese URLs.
    # Pin English and use literal paths: English is unprefixed, Portuguese is /pt-br/.
    def setUp(self):
        translation.activate("en")

    def tearDown(self):
        translation.deactivate()

    REMOVED_FROM_HOME = ["John Ariedi", "15+ years", "CISSP", "CISO", "9107", "paradigm shift"]

    def test_home_renders_with_current_identity(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("João Ariedi", body)
        self.assertIn('id="section-research"', body)
        self.assertIn('id="section-work"', body)
        for removed in self.REMOVED_FROM_HOME:
            self.assertNotIn(removed, body, f"{removed!r} must not appear on the home page")

    def test_research_page_lists_meistudies_entry(self):
        response = self.client.get("/research")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('id="meistudies-2026"', body)
        self.assertIn("syntagm transition", body)
        self.assertIn("Why the full text is not published here yet", body)
        self.assertIn('id="simpep-2026"', body)
        self.assertIn("Organizational Maturity Framework", body)

    def test_presentations_page_renders(self):
        response = self.client.get("/presentations")
        self.assertEqual(response.status_code, 200)

    def test_seo_files_render(self):
        self.assertEqual(self.client.get("/robots.txt").status_code, 200)
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertIn("https://ariedi.com/research", sitemap.content.decode())

    def test_portuguese_version_lives_under_pt_br_prefix(self):
        response = self.client.get("/pt-br/")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('<html lang="pt-BR">', body)
        self.assertIn("Olá, eu sou", body)
        self.assertIn("Pesquisa e publicações", body)
        self.assertNotIn("Hello, I'm", body)
        # names are never translated
        self.assertIn("João Ariedi", body)
        self.assertIn("Frons Educação", body)

    def test_english_is_default_and_unprefixed(self):
        body = self.client.get("/").content.decode()
        self.assertIn('<html lang="en">', body)
        self.assertIn("Hello, I'm", body)
        self.assertNotIn("Olá, eu sou", body)
        # the English page must not leak Portuguese prose (names and work titles excepted)
        self.assertNotIn("Um estudo de caso em um", body)

    def test_language_switcher_links_to_the_same_page(self):
        en = self.client.get("/research").content.decode()
        pt = self.client.get("/pt-br/research").content.decode()
        self.assertIn('href="/pt-br/research" hreflang="pt-BR"', en)
        self.assertIn('href="/research" hreflang="en"', pt)
        self.assertIn('hreflang="x-default" href="https://ariedi.com/research"', en)
        self.assertIn("Síntese estendida", pt)
        self.assertIn('id="simpep-2026"', pt)

