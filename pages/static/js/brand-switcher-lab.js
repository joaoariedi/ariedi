/* EXPERIMENT ONLY: lets the owner compare four styles of the opening question on the demo.
 * ?switcher=chips|tuner|branches|dock (remembered for the tab) or the lab bar, bottom left.
 * All four use the same links in nav.need, so brand-profile.js loads the versions for each.
 * Delete with brand-switcher-lab.css once a style is chosen. */
(function () {
	'use strict';

	var STYLES = ['chips', 'tuner', 'branches', 'dock'];
	var GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#/+';
	var root = document.documentElement;
	var nav = document.querySelector('.need');
	if (!nav) return;

	function stored() {
		try { return window.sessionStorage.getItem('switcher-lab'); } catch (e) { return null; }
	}
	function store(style) {
		try { window.sessionStorage.setItem('switcher-lab', style); } catch (e) { /* private mode */ }
	}
	var asked = new URLSearchParams(window.location.search).get('switcher');
	var style = STYLES.indexOf(asked) !== -1 ? asked : (STYLES.indexOf(stored()) !== -1 ? stored() : 'chips');

	function links() {
		return Array.prototype.slice.call(nav.querySelectorAll('a.need-a'));
	}
	function currentIndex(list) {
		for (var i = 0; i < list.length; i++) if (list[i].getAttribute('aria-current') === 'page') return i;
		return list.length - 1;
	}

	// ---- tuner ----
	var shown = 0, settle = null, refocus = null;
	function scramble(link) {
		var text = link.getAttribute('data-text') || link.textContent;
		link.setAttribute('data-text', text);
		var start = window.performance.now();
		(function tick(now) {
			var p = Math.min(1, (now - start) / 280), out = '';
			for (var i = 0; i < text.length; i++) {
				out += (i < p * text.length || text.charAt(i) === ' ') ? text.charAt(i) : GLYPHS.charAt((Math.random() * GLYPHS.length) | 0);
			}
			link.textContent = out;
			if (p < 1) window.requestAnimationFrame(tick);
		})(start);
	}
	function show(index, animate) {
		var list = links();
		shown = (index + list.length) % list.length;
		list.forEach(function (link, i) { link.classList.toggle('is-shown', i === shown); });
		var count = nav.querySelector('.need-count');
		if (count) count.textContent = '0' + (shown + 1) + '/0' + list.length;
		if (animate && !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)) scramble(list[shown]);
	}
	function step(direction) {
		show(shown + direction, true);
		window.clearTimeout(settle);
		settle = window.setTimeout(function () {   // settle on an answer, then load it
			var link = links()[shown];
			if (link && link.getAttribute('aria-current') !== 'page') link.click();
		}, 520);
	}
	function stepButton(label, glyph, direction) {
		var button = document.createElement('button');
		button.type = 'button';
		button.className = 'need-step';
		button.setAttribute('aria-label', label);
		button.textContent = glyph;
		button.addEventListener('click', function () { refocus = direction; step(direction); });
		return button;
	}
	function buildTuner() {
		if (nav.querySelector('.need-step')) return;
		var first = nav.querySelector('a.need-a');
		var previous = stepButton('Previous answer', '‹', -1), next = stepButton('Next answer', '›', 1);
		var count = document.createElement('span');
		count.className = 'need-count';
		count.setAttribute('aria-hidden', 'true');
		nav.insertBefore(previous, first);
		nav.appendChild(next);
		nav.appendChild(count);
		show(currentIndex(links()), false);
		if (refocus) (refocus === 1 ? next : previous).focus();
		refocus = null;
	}

	// ---- dock ----
	var dock = document.createElement('nav'), fromDock = false;
	dock.className = 'need-dock';
	dock.setAttribute('aria-label', nav.getAttribute('aria-label'));
	document.body.appendChild(dock);
	dock.addEventListener('click', function () { fromDock = true; }, true);
	function buildDock() {
		dock.innerHTML = nav.innerHTML;
		Array.prototype.forEach.call(dock.querySelectorAll('.need-step, .need-count'), function (el) { el.remove(); });
		Array.prototype.forEach.call(dock.querySelectorAll('.is-shown'), function (el) { el.classList.remove('is-shown'); });
	}
	var hero = document.getElementById('section-started');
	if (hero && 'IntersectionObserver' in window) {
		new IntersectionObserver(function (entries) {
			root.classList.toggle('dock-on', !entries[0].isIntersecting);
		}).observe(hero);
	}

	// ---- the lab bar ----
	var bar = document.createElement('div');
	bar.className = 'lab-bar';
	var title = document.createElement('span');
	title.textContent = 'Experiment · switcher';
	bar.appendChild(title);
	function apply(next) {
		style = next;
		root.setAttribute('data-switcher', style);
		store(style);
		Array.prototype.forEach.call(bar.querySelectorAll('button'), function (button) {
			button.setAttribute('aria-pressed', String(button.getAttribute('data-style') === style));
		});
		window.dispatchEvent(new Event('resize'));   // the hero drawing moves when the question does
	}
	STYLES.forEach(function (name, i) {
		var button = document.createElement('button');
		button.type = 'button';
		button.setAttribute('data-style', name);
		button.textContent = (i + 1) + ' ' + name;
		button.addEventListener('click', function () { apply(name); });
		bar.appendChild(button);
	});
	document.body.appendChild(bar);

	function rebuild() {
		buildTuner();
		buildDock();
	}
	window.addEventListener('profile:change', function () {
		rebuild();
		if (fromDock) {   // the page changed under the reader: bring the new profile into view
			var about = document.getElementById('section-about');
			if (about) window.scrollTo(0, about.getBoundingClientRect().top + window.pageYOffset - 68);
		}
		fromDock = false;
	});
	rebuild();
	apply(style);
})();
