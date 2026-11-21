/* Brand decode: words resolve from noise into signal.
 *
 * - Section titles and FIG labels arrive as a brief scramble of glyphs that locks, left to right,
 *   into the real word the first time they enter the view (about 0.4 s, once per element).
 * - The drawing's labels glitch in once, the first time the hero is seen, one after another in
 *   the order of the flow: the stakeholders' vision on the noise, the divergent intelligence as
 *   the orange decision line lands, the machine it lands on, then products and services.
 * - The hero's input label re-encodes when you look away: each time the hero leaves the view and
 *   comes back, it decodes into the next phrase in its data-variants (the brand guide's tested
 *   lines), then back to "Stakeholder inputs". Antichamber's rule: the room changes behind you.
 *
 * The real text is never removed: it stays in the element, transparent, under an aria-hidden
 * overlay of the same box, so screen readers read the word and the layout never shifts. Nothing
 * runs with prefers-reduced-motion or Save-Data; switching reduced motion on mid-session lands every
 * running decode on its word at once and stops the effect for the rest of the visit.
 */
(function () {
	'use strict';

	var GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#/+';
	var DURATION = 420;                    // ms from noise to the locked word
	var REFRESH = 55;                      // ms between glyph changes (calmer than every frame)

	var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
	var saveData = !!(navigator.connection && navigator.connection.saveData);
	if ((reduce && reduce.matches) || saveData || !('IntersectionObserver' in window)) return;

	var stopped = false;
	var running = [];                      // finishers of the decodes in flight

	function noiseFor(text, locked) {
		var out = '';
		for (var i = 0; i < text.length; i++) {
			var ch = text.charAt(i);
			out += (i < locked || ch === ' ' || ch === '·') ? ch : GLYPHS.charAt((Math.random() * GLYPHS.length) | 0);
		}
		return out;
	}

	// Decodes el into text: a transparent copy of the final text holds the box, the overlay shows
	// the noise. Returns false (and does nothing) while el is still decoding or the effect is stopped.
	function decode(el, text) {
		if (stopped || el.getAttribute('data-decoding')) return false;
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
		var start = window.performance.now(), shown = -REFRESH, done = false;
		function finish() {
			if (done) return;
			done = true;
			el.textContent = text;
			el.removeAttribute('data-decoding');
			running.splice(running.indexOf(finish), 1);
		}
		running.push(finish);
		function tick(now) {
			if (done) return;
			var p = (now - start) / DURATION;
			if (p >= 1) {
				finish();
				return;
			}
			if (now - shown >= REFRESH) {
				noise.textContent = noiseFor(text, Math.floor(p * p * text.length));
				shown = now;
			}
			window.requestAnimationFrame(tick);
		}
		window.requestAnimationFrame(tick);
		return true;
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

	// 2. The drawing's labels, once, in the order of the flow (they show only on desktop).
	// The noise first; the divergent intelligence as the orange decision line lands (~1.2 s);
	// then the machine it lands on, then what comes out.
	var GLITCH_AT = [250, 1150, 1550, 1950], GLITCH_MS = 460;
	var field = document.querySelector('.hero-field');
	var fieldLabels = field ? Array.prototype.slice.call(field.querySelectorAll('.field-label')) : [];
	var glitchTimers = [], firstSight = null;

	function glitchIn(el) {
		el.classList.add('glitching');
		decode(el, el.textContent.trim());
		glitchTimers.push(setTimeout(function () {
			el.classList.remove('glitching');
			el.classList.add('arrived');
		}, GLITCH_MS));
	}

	if (fieldLabels.length && fieldLabels[0].getClientRects().length) {
		field.classList.add('labels-pending');
		firstSight = new IntersectionObserver(function (entries) {
			if (!entries[0].isIntersecting) return;
			firstSight.disconnect();
			fieldLabels.forEach(function (el, i) {
				glitchTimers.push(setTimeout(function () { glitchIn(el); }, GLITCH_AT[Math.min(i, GLITCH_AT.length - 1)]));
			});
		});
		firstSight.observe(field);
	}

	// Reduced motion switched on mid-visit: words land now, nothing decodes or glitches again.
	var lookAway = null;
	function stop() {
		stopped = true;
		arrivals.disconnect();
		if (lookAway) lookAway.disconnect();
		if (firstSight) firstSight.disconnect();
		glitchTimers.forEach(clearTimeout);
		fieldLabels.forEach(function (el) { el.classList.remove('glitching'); });
		if (field) field.classList.remove('labels-pending');
		running.slice().forEach(function (finish) { finish(); });
	}
	if (reduce) {
		var onReduce = function (e) { if (e.matches) stop(); };
		if (reduce.addEventListener) reduce.addEventListener('change', onReduce);
		else if (reduce.addListener) reduce.addListener(onReduce);
	}

	// 3. The hero's input label, after each look-away.
	var label = document.querySelector('.field-label[data-variants]');
	var hero = label && label.closest('.section');
	if (!hero) return;
	var phrases = [label.textContent.trim()].concat(label.getAttribute('data-variants').split('|').map(function (v) {
		return v.trim();
	}).filter(Boolean));
	var turn = 0, away = false;
	lookAway = new IntersectionObserver(function (entries) {
		var e = entries[0];
		if (!e.isIntersecting) { away = true; return; }
		if (!away) return;
		away = false;
		var next = (turn + 1) % phrases.length;
		if (decode(label, phrases[next])) turn = next;   // a skipped decode must not skip a phrase
	});
	lookAway.observe(hero);
})();
