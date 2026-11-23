import re
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

    REMOVED_FROM_HOME = ["John Ariedi", "15+ years", "CISSP", "CISO", "9107", "paradigm shift", "Led a FAPESP", "v9.1.3"]

    # The hero headline of the brand design, in both languages.
    HEADLINE_EN = "I build the machine that turns vision into revenue"
    HEADLINE_PT = "Construo a máquina que transforma visão em receita"

    def test_home_renders_with_current_identity(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("João Ariedi", body)
        self.assertIn('id="section-research"', body)
        self.assertIn('id="section-work"', body)
        self.assertIn('id="section-talks"', body)
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
        self.assertIn('id="pucsp-2026"', body)
        self.assertIn("Organizational Maturity Framework", body)

    def test_presentations_page_renders(self):
        response = self.client.get("/presentations")
        self.assertEqual(response.status_code, 200)

    DECKS = {
        "harness-software-engineering": "Harness Software Engineering",
        "organizational-intelligence": "Inteligência Organizacional",
        "agentic-work-transition": "AI Agentic Work Transition",
    }

    def test_presentations_page_links_every_deck(self):
        for prefix in ("", "/pt-br"):
            body = self.client.get(prefix + "/presentations").content.decode()
            for slug in self.DECKS:
                self.assertIn(f'href="{prefix}/presentations/{slug}"', body, prefix)
            self.assertIn(f'href="{prefix}/presentations/pdf/modern-engineering.pdf">', body, prefix)
            self.assertNotIn("<iframe", body, prefix)

    def test_each_deck_opens_in_the_site_language(self):
        """The deck page is the file as written plus one setLang call in the URL's language."""
        for slug, title in self.DECKS.items():
            for prefix, code in (("", "en"), ("/pt-br", "pt")):
                response = self.client.get(f"{prefix}/presentations/{slug}")
                self.assertEqual(response.status_code, 200, slug)
                self.assertTrue(response["Content-Type"].startswith("text/html"), slug)
                body = response.content.decode()
                self.assertIn(f"<title>{title}", body, slug)
                opener = f'setLang("{code}");</script></body>'
                self.assertIn(opener, body, f"{slug} at {prefix or '/'}")
                self.assertEqual(body.count("typeof setLang"), 1, slug)

    def test_decks_carry_canonical_and_hreflang_links(self):
        for slug in self.DECKS:
            for prefix in ("", "/pt-br"):
                head = self.client.get(f"{prefix}/presentations/{slug}").content.decode().split("</head>")[0]
                self.assertIn(f'<link rel="canonical" href="https://ariedi.com{prefix}/presentations/{slug}">', head)
                self.assertIn(f'hreflang="en" href="https://ariedi.com/presentations/{slug}"', head)
                self.assertIn(f'hreflang="pt-BR" href="https://ariedi.com/pt-br/presentations/{slug}"', head)
                self.assertIn(f'hreflang="x-default" href="https://ariedi.com/presentations/{slug}"', head)
                self.assertEqual(head.count('rel="canonical"'), 1, slug)

    def test_every_deck_declares_its_language(self):
        """Screen readers need <html lang>; each deck's setLang keeps it in step with its toggle."""
        for slug in self.DECKS:
            body = self.client.get(f"/presentations/{slug}").content.decode()
            self.assertRegex(body, r"<html[^>]*\blang=\"(en|pt-BR)\"", slug)
            self.assertIn("document.documentElement.lang", body, slug)

    def test_decks_carry_the_site_favicon(self):
        for slug in self.DECKS:
            head = self.client.get(f"/presentations/{slug}").content.decode().split("</head>")[0]
            self.assertIn('<link rel="icon" href="/static/images/favicons/rings.svg" type="image/svg+xml">', head, slug)
            self.assertIn('<link rel="icon" href="/static/images/favicons/fav2.png" type="image/png">', head, slug)
            self.assertIn('<link rel="apple-touch-icon" href="/static/images/favicons/fav2.png">', head, slug)

    def test_every_deck_title_is_in_its_head(self):
        for slug, title in self.DECKS.items():
            head, body = self.client.get(f"/presentations/{slug}").content.decode().split("</head>", 1)
            self.assertIn(f"<title>{title}", head, slug)
            self.assertNotIn("<title", body, slug)

    def test_every_deck_links_back_to_the_site(self):
        cases = (("", "Presentations", "Home"), ("/pt-br", "Apresentações", "Início"))
        for slug in self.DECKS:
            for prefix, presentations, home in cases:
                body = self.client.get(f"{prefix}/presentations/{slug}").content.decode()
                self.assertIn(f'<a href="{prefix}/presentations"><span aria-hidden="true">&larr; </span>{presentations}</a>', body, slug)
                self.assertIn(f'<a href="{prefix}/">{home}</a></nav>', body, slug)
                self.assertEqual(body.count('id="site-return"'), 1, slug)

    def test_menu_is_on_every_page_and_leads_back_to_home_sections(self):
        for prefix in ("", "/pt-br"):
            for path in ("/presentations", "/research"):
                body = self.client.get(prefix + path).content.decode()
                for section in ("services", "history", "research", "work", "skills"):
                    self.assertIn(f'href="{prefix}/#section-{section}"', body, prefix + path)
                # Contact is the footer, on the page you are on
                self.assertIn('<a href="#section-contacts">', body, prefix + path)
                self.assertIn('id="section-contacts"', body, prefix + path)
                self.assertIn(f'href="{prefix}/presentations"', body, prefix + path)
            here = self.client.get(prefix + "/presentations").content.decode()
            self.assertIn(f'href="{prefix}/presentations" aria-current="page"', here, prefix)
            home = self.client.get(prefix + "/").content.decode()
            self.assertIn('href="#section-services"', home, prefix)
            self.assertIn(f'<a href="{prefix}/presentations">', home, prefix)

    def test_every_deck_uses_the_site_palette_and_typefaces(self):
        """The decks share the site's night palette (violet on #150A22) and its typefaces."""
        for slug in self.DECKS:
            body = self.client.get(f"/presentations/{slug}").content.decode()
            self.assertIn("#150A22", body.upper(), slug)
            self.assertIn("family=Chakra+Petch", body, slug)
            self.assertIn("family=IBM+Plex+Sans", body, slug)
            for old in ("#3BDD8F", "#0B0E0C", "59,221,143"):
                self.assertNotIn(old, body.upper().replace(" ", ""), f"{old} left in {slug}")
            for font in ("family=Sora", '"Sora"', "family=Manrope", '"Manrope"'):
                self.assertNotIn(font, body, f"{font} left in {slug}")

    def test_deck_urls_name_only_known_decks(self):
        for path in ("/presentations/unknown-deck", "/presentations/modern-engineering",
                     "/presentations/..%2Fviews.py", "/presentations/organizational-intelligence.html"):
            self.assertEqual(self.client.get(path).status_code, 404, path)

    def test_pdf_route_serves_only_pdfs(self):
        self.assertEqual(self.client.get("/presentations/pdf/modern-engineering.pdf").status_code, 200)
        self.assertEqual(self.client.get("/presentations/pdf/organizational-intelligence.html").status_code, 404)
        self.assertIn("Disallow: /static/presentations/", self.client.get("/robots.txt").content.decode())

    def test_hefesto_card_links_to_the_hosted_presentation(self):
        body = self.client.get("/").content.decode()
        self.assertIn('href="/presentations/harness-software-engineering"', body)
        self.assertNotIn("blob/main/hefesto-sdlc.html", body)

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
        self.assertIn(self.HEADLINE_PT, body)
        self.assertIn("Pesquisa e publicações", body)
        self.assertIn("Palestras e painéis", body)
        self.assertNotIn(self.HEADLINE_EN, body)
        # names are never translated
        self.assertIn("João Ariedi", body)
        self.assertIn("Frons Educação", body)

    def test_english_is_default_and_unprefixed(self):
        body = self.client.get("/").content.decode()
        self.assertIn('<html lang="en">', body)
        self.assertIn(self.HEADLINE_EN, body)
        self.assertNotIn(self.HEADLINE_PT, body)
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

    def test_unused_theme_plugins_are_not_loaded(self):
        """The brand pages use none of the theme's jQuery plugins; loading them cost ~124 KB."""
        # Asset paths, not bare names: "grained-off" is a body class scripts.js reads.
        unused = ("js/swiper", "js/isotope", "js/jarallax", "js/magnific-popup",
                  "js/jquery.validate", "js/simpleParallax", "js/imagesloaded", "js/grained",
                  "css/magnific-popup", "css/animate", "css/jarallax", "css/swiper")
        for path in ("/", "/pt-br/", "/research", "/presentations"):
            body = self.client.get(path).content.decode()
            self.assertIn("js/jquery.min", body, path)
            self.assertIn("js/scripts", body, path)
            for asset in unused:
                self.assertNotIn(asset, body, f"{asset!r} still loaded on {path}")

    def test_hero_field_carries_the_motion_parameters(self):
        """The static drawing is frame zero of brand-motion.js; it needs each line's parameters."""
        body = self.client.get("/").content.decode()
        self.assertIn("js/brand-motion", body)
        for attr in ('data-cx="', 'data-cy="', 'data-xc="', 'data-ymin="', 'data-ymax="'):
            self.assertIn(attr, body)
        # two canvases, wide (tablet, desktop) and narrow (phones): 20 and 14 incoming lines
        self.assertEqual(body.count('class="field field-wide"'), 1)
        self.assertEqual(body.count('class="field field-narrow"'), 1)
        self.assertEqual(body.count('class="field-depth"'), 6)
        self.assertEqual(body.count("data-w="), 34)
        wide = body[body.index('field-wide'):body.index('field-narrow')]
        self.assertEqual(wide.count("data-w="), 20)
        self.assertIn('viewBox="0 0 440 248"', body)
        # each canvas clips to itself: the ids must not collide
        self.assertEqual(body.count('id="field-clip-wide"'), 1)
        self.assertEqual(body.count('id="field-clip-narrow"'), 1)
        # rings, decision line and output lines carry no motion data: they stay still
        self.assertEqual(body.count('class="field-out"'), 2)
        self.assertEqual(body.count('class="decision"'), 2)

    def test_hero_labels_name_the_flow_in_order(self):
        """Each label on its element, in the order the field flows, in the page's language."""
        for prefix, words in (("", ("Stakeholders Vision", "Divergent Intelligence", "The Machine", "Products and Services")),
                              ("/pt-br", ("Visão dos stakeholders", "Inteligência divergente", "A máquina", "Produtos e serviços"))):
            body = self.client.get(prefix + "/").content.decode()
            spots = [body.index(f'aria-hidden="true">{w}</span>') for w in words]
            self.assertEqual(spots, sorted(spots), prefix)
            # the divergent intelligence and the machine share the decision line's right side
            sides = re.findall(r'class="field-label field-label-(?:divergent|machine)" style="(left:[^;]+);', body)
            self.assertEqual(len(set(sides)), 1, prefix)

    def test_signal_layer_is_wired(self):
        """Noise to signal: the decoder is loaded and the hero label carries its look-away phrases."""
        body = self.client.get("/").content.decode()
        self.assertIn("js/brand-decode", body)
        self.assertRegex(body, r'class="field-label field-label-in"[^>]*data-variants="[^"]+\|[^"]+\|[^"]+"')
        pt = self.client.get("/pt-br/").content.decode()
        self.assertIn("A eletricidade é o novo fogo", pt)

    def test_night_sheet_only_no_switcher(self):
        """The brand ships one sheet (night); the experiment's switcher and its ?sheet= script are gone."""
        for path in ("/", "/pt-br/", "/research", "/presentations"):
            body = self.client.get(path).content.decode()
            self.assertIn("brand-tokens.css", body, path)
            for leftover in ("data-sheet", "sheet-switch", "brand-sheet", "localStorage"):
                self.assertNotIn(leftover, body, f"{leftover!r} on {path}")

    def test_certifications_are_grouped_by_field_and_languages_stand_apart(self):
        """Certifications: field title, then the entity, then the list; Languages is its own block."""
        cases = (("/", ("Certifications", "Cybersecurity", "Cloud", "Languages")),
                 ("/pt-br/", ("Certificações", "Cibersegurança", "Nuvem", "Idiomas")))
        for path, (certs, cyber, cloud, langs) in cases:
            body = self.client.get(path).content.decode()
            self.assertIn(f'<h2 class="title_inner">{certs}</h2>', body, path)
            self.assertIn(f'<h2 class="title_inner">{langs}</h2>', body, path)
            self.assertRegex(body, rf"{cyber}<br>\s*<small>FIAP</small>", path)
            self.assertRegex(body, rf"{cloud}<br>\s*<small>Amazon Web Services</small>", path)
            self.assertIn("<li>Penetration Testing</li>", body, path)
            self.assertNotIn("Certifications and languages", body, path)
            self.assertNotIn("Certificações e idiomas", body, path)

    def test_each_language_shows_only_its_own_titles(self):
        """No translation in parentheses: each language carries its own titles, not both."""
        en = self.client.get("/").content.decode() + self.client.get("/research").content.decode()
        for leak in ("Gerente de Engenharia", "Mesa 6", "(anais)", "Simpósio de Engenharia"):
            self.assertNotIn(leak, en, f"Portuguese {leak!r} on the English pages")
        pt = self.client.get("/pt-br/").content.decode() + self.client.get("/pt-br/research").content.decode()
        for leak in ("Software Engineering Manager", "Principal Software Engineer", "Senior Software Engineer",
                     "Technologist in Cyber Defense", "session 6", "Production Engineering Symposium"):
            self.assertNotIn(leak, pt, f"English {leak!r} on the Portuguese pages")




@override_settings(STORAGES=PLAIN_STATIC, ALLOWED_HOSTS=["ariedi.com", "www.ariedi.com", "ariedi.herokuapp.com", "testserver"])
class CanonicalHostRedirectTest(TestCase):
    """The custom-domain cut-over: other hosts 301 to https://ariedi.com, canonical host is served."""

    def setUp(self):
        translation.activate("en")

    def tearDown(self):
        translation.deactivate()

    @override_settings(CANONICAL_HOST="ariedi.com")
    def test_other_hosts_redirect_to_canonical_https_keeping_path_and_query(self):
        for host in ("www.ariedi.com", "ariedi.herokuapp.com"):
            response = self.client.get("/research?x=1", HTTP_HOST=host)
            self.assertEqual(response.status_code, 301, host)
            self.assertEqual(response["Location"], "https://ariedi.com/research?x=1")

    @override_settings(CANONICAL_HOST="ariedi.com")
    def test_canonical_host_is_served(self):
        response = self.client.get("/", HTTP_HOST="ariedi.com")
        self.assertEqual(response.status_code, 200)

    @override_settings(CANONICAL_HOST="")
    def test_no_redirect_while_unset(self):
        response = self.client.get("/", HTTP_HOST="ariedi.herokuapp.com")
        self.assertEqual(response.status_code, 200)

    def test_custom_domain_is_an_allowed_host_by_default(self):
        import core.settings as defaults
        self.assertIn("ariedi.com", defaults.ALLOWED_HOSTS)
        self.assertIn("www.ariedi.com", defaults.ALLOWED_HOSTS)
        self.assertEqual(defaults.SECURE_PROXY_SSL_HEADER, ("HTTP_X_FORWARDED_PROTO", "https"))
        self.assertIn("https://ariedi.com", defaults.CSRF_TRUSTED_ORIGINS)
