/* Brand HUD (experiment): a small readout of where you are on the page, and a light that
 * follows the pointer across the drafting plane.
 *
 * - Readout (desktop, CSS shows it from 1200 px): section number of the total, the section's
 *   name in the page's language (the menu's word for it, or its title), and how far down the
 *   page you are. Names are read before brand-decode.js scrambles any title.
 * - Cursor light: only with a fine pointer, motion allowed and no Save-Data; it moves with
 *   transform only, once per frame.
 */
(function () {
	'use strict';

	var media = function (q) { return window.matchMedia ? window.matchMedia(q) : null; };
	var reduce = media('(prefers-reduced-motion: reduce)');
	var fine = media('(hover: hover) and (pointer: fine)');
	var saveData = !!(navigator.connection && navigator.connection.saveData);

	// Readout -------------------------------------------------------------------------------
	function sectionName(section) {
		// scripts.js doubles each menu word into two mask spans for its hover; read the first
		var link = document.querySelector('.top-menu a[href$="#' + section.id + '"]');
		var word = link && (link.querySelector('.mask-lnk') || link);
		var title = section.querySelector('.title .title_inner, .hero-title');
		return ((word && word.textContent) || (title && title.textContent) || '').trim();
	}

	var sections = Array.prototype.slice.call(document.querySelectorAll('.section[id^="section-"]'))
		.map(function (el) { return { el: el, name: sectionName(el) }; })
		.filter(function (s) { return s.name; });

	function pad(n) {
		return n < 10 ? '0' + n : String(n);
	}

	var readout = null, shown = '', queued = false;
	function update() {
		queued = false;
		var probe = window.innerHeight * 0.35, current = 0;
		for (var i = 0; i < sections.length; i++) {
			if (sections[i].el.getBoundingClientRect().top <= probe) current = i;
		}
		var max = document.documentElement.scrollHeight - window.innerHeight;
		var pct = max > 0 ? Math.round(window.pageYOffset / max * 100) : 0;
		var text = pad(current + 1) + '/' + pad(sections.length) + '|' + sections[current].name + '|' + pct;
		if (text === shown) return;
		shown = text;
		var parts = text.split('|');
		readout.innerHTML = '';
		var where = document.createElement('b');
		where.textContent = parts[0];
		readout.appendChild(where);
		readout.appendChild(document.createTextNode(' · ' + parts[1] + ' · ' + parts[2] + '%'));
	}

	function queue() {
		if (!queued) { queued = true; window.requestAnimationFrame(update); }
	}

	if (sections.length > 1) {
		readout = document.createElement('div');
		readout.className = 'hud-readout';
		readout.setAttribute('aria-hidden', 'true');
		document.body.appendChild(readout);
		update();
		window.addEventListener('scroll', queue, { passive: true });
		window.addEventListener('resize', queue);
	}

	// Cursor light --------------------------------------------------------------------------
	if (saveData || !fine || !fine.matches || (reduce && reduce.matches)) return;
	var light = document.createElement('div');
	light.className = 'cursor-light';
	light.setAttribute('aria-hidden', 'true');
	document.body.appendChild(light);
	var x = 0, y = 0, moving = false;
	function place() {
		moving = false;
		light.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0)';
	}
	window.addEventListener('pointermove', function (e) {
		x = e.clientX; y = e.clientY;
		light.classList.add('on');
		if (!moving) { moving = true; window.requestAnimationFrame(place); }
	}, { passive: true });
	document.documentElement.addEventListener('pointerleave', function () { light.classList.remove('on'); });
	if (reduce && reduce.addEventListener) {
		reduce.addEventListener('change', function () { if (reduce.matches) light.remove(); });
	}
})();
