/* Brand decode: words resolve from noise into signal.
 *
 * - Section titles and FIG labels arrive as a brief scramble of glyphs that locks, left to right,
 *   into the real word the first time they enter the view (about 0.4 s, once per element).
 * - The hero's input label re-encodes when you look away: each time the hero leaves the view and
 *   comes back, it decodes into the next phrase in its data-variants (the brand guide's tested
 *   lines), then back to "Stakeholder inputs". Antichamber's rule: the room changes behind you.
 *
 * The real text is never removed: it stays in the element, transparent, under an aria-hidden
 * overlay of the same box, so screen readers read the word and the layout never shifts. Nothing
 * runs with prefers-reduced-motion or Save-Data.
 */
(function () {
	'use strict';

	var GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#/+';
	var DURATION = 420;                    // ms from noise to the locked word
	var REFRESH = 55;                      // ms between glyph changes (calmer than every frame)

	var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
	var saveData = !!(navigator.connection && navigator.connection.saveData);
	if ((reduce && reduce.matches) || saveData || !('IntersectionObserver' in window)) return;

	function noiseFor(text, locked) {
		var out = '';
		for (var i = 0; i < text.length; i++) {
			var ch = text.charAt(i);
			out += (i < locked || ch === ' ' || ch === '·') ? ch : GLYPHS.charAt((Math.random() * GLYPHS.length) | 0);
		}
		return out;
	}

	// Decodes el into text: a transparent copy of the final text holds the box, the overlay shows
	// the noise. Calling it again while it runs is ignored.
	function decode(el, text) {
		if (el.getAttribute('data-decoding')) return;
		el.setAttribute('data-decoding', '1');
		var real = document.createElement('span');
		var noise = document.createElement('span');
		real.className = 'decode-real';
		real.textContent = text;
		noise.className = 'decode-noise';
		noise.setAttribute('aria-hidden', 'true');
		el.textContent = '';
		el.appendChild(real);
		el.appendChild(noise);
		var start = window.performance.now(), shown = -REFRESH;
		function tick(now) {
			var p = (now - start) / DURATION;
			if (p >= 1) {
				el.textContent = text;
				el.removeAttribute('data-decoding');
				return;
			}
			if (now - shown >= REFRESH) {
				noise.textContent = noiseFor(text, Math.floor(p * p * text.length));
				shown = now;
			}
			window.requestAnimationFrame(tick);
		}
		window.requestAnimationFrame(tick);
	}

	// 1. Titles and FIG labels, once each, as they come into view.
	var arrivals = new IntersectionObserver(function (entries) {
		entries.forEach(function (e) {
			if (!e.isIntersecting) return;
			arrivals.unobserve(e.target);
			decode(e.target, e.target.textContent.trim());
		});
	}, { rootMargin: '0px 0px -8% 0px' });
	Array.prototype.forEach.call(document.querySelectorAll('.section .title .title_inner, .fig'), function (el) {
		arrivals.observe(el);
	});

	// 2. The hero's input label, after each look-away.
	var label = document.querySelector('.field-label[data-variants]');
	var hero = label && label.closest('.section');
	if (!hero) return;
	var phrases = [label.textContent.trim()].concat(label.getAttribute('data-variants').split('|').map(function (v) {
		return v.trim();
	}).filter(Boolean));
	var turn = 0, away = false;
	new IntersectionObserver(function (entries) {
		var e = entries[0];
		if (!e.isIntersecting) { away = true; return; }
		if (!away) return;
		away = false;
		turn = (turn + 1) % phrases.length;
		decode(label, phrases[turn]);
	}).observe(hero);
})();
