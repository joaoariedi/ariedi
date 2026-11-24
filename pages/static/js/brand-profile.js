/* The opening question: load the chosen version of the home page in place.
 *
 * Every answer in the hero is a real link (/engineering, /security, ...), so the page works
 * without this script. With it, a version is fetched only when the visitor asks for it (on
 * hover or focus, to have it ready, or on click), never with the default page: the sections that
 * change with the answer are swapped, sections are added, dropped and ordered as the version has
 * them, the menu entry of a dropped section hides, and the address,
 * the language links and the canonical follow. The hero stays as it is, so its drawing keeps
 * running. Any failure falls back to following the link.
 */
(function () {
	'use strict';

	var VARY = ['section-about', 'section-skills', 'section-history', 'section-work'];
	var wrapper = document.querySelector('.wrapper[data-profile]');
	if (!wrapper || !window.fetch || !window.DOMParser || !window.history.pushState) return;

	var pages = {};   // url -> promise of the parsed page

	function load(url) {
		if (!pages[url]) {
			pages[url] = window.fetch(url, { credentials: 'same-origin' }).then(function (response) {
				if (!response.ok) throw new Error('version ' + url + ' answered ' + response.status);
				return response.text();
			}).then(function (html) {
				return new DOMParser().parseFromString(html, 'text/html');
			});
			pages[url].catch(function () { delete pages[url]; });
		}
		return pages[url];
	}

	function copyInner(selector, doc) {
		var here = document.querySelectorAll(selector), there = doc.querySelectorAll(selector);
		for (var i = 0; i < here.length && i < there.length; i++) here[i].innerHTML = there[i].innerHTML;
	}

	function copyLinks(selector, doc) {
		var here = document.head.querySelectorAll(selector), there = doc.head.querySelectorAll(selector);
		for (var i = 0; i < here.length && i < there.length; i++) here[i].setAttribute('href', there[i].getAttribute('href'));
	}

	// Brings the page to the version in doc; false when doc is not a home page.
	function show(doc) {
		var next = doc.querySelector('.wrapper[data-profile]');
		if (!next) return false;
		var kept = {};
		Array.prototype.forEach.call(next.children, function (incoming) {
			if (!incoming.id) return;
			var current = document.getElementById(incoming.id);
			if (!current || VARY.indexOf(incoming.id) !== -1) {
				var arrived = document.importNode(incoming, true);
				arrived.classList.add('version-arrive');
				if (current) current.parentNode.replaceChild(arrived, current);
				current = arrived;
			}
			wrapper.appendChild(current);   // the version's order
			kept[incoming.id] = true;
		});
		// a section this version does not have (the Services cards belong to the blend)
		Array.prototype.slice.call(wrapper.children).forEach(function (section) {
			if (section.id && !kept[section.id]) wrapper.removeChild(section);
		});
		Array.prototype.forEach.call(document.querySelectorAll('[data-section]'), function (item) {
			item.hidden = !kept[item.getAttribute('data-section')];
		});
		wrapper.setAttribute('data-profile', next.getAttribute('data-profile'));
		copyInner('.need', doc);
		copyInner('.lang-switch', doc);
		copyInner('.sheet-langs', doc);
		copyLinks('link[rel="canonical"], link[rel="alternate"][hreflang]', doc);
		window.dispatchEvent(new CustomEvent('profile:change'));
		return true;
	}

	function go(url, push) {
		return load(url).then(function (doc) {
			if (!show(doc)) throw new Error('not a home page: ' + url);
			if (push) window.history.pushState({ version: true }, '', url);
		}).catch(function () {
			window.location.href = url;
		});
	}

	function answer(target) {
		return target && target.closest ? target.closest('a.need-a') : null;
	}

	document.addEventListener('click', function (e) {
		var link = answer(e.target);
		if (!link || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
		e.preventDefault();
		if (link.getAttribute('aria-current') === 'page') return;
		link.setAttribute('aria-busy', 'true');
		go(link.getAttribute('href'), true);
	});

	// Have the version ready when the visitor shows intent; still nothing with the default page.
	function warm(e) {
		var link = answer(e.target);
		if (link && link.getAttribute('aria-current') !== 'page') load(link.getAttribute('href')).catch(function () {});
	}
	document.addEventListener('pointerover', warm, { passive: true });
	document.addEventListener('focusin', warm);

	window.addEventListener('popstate', function () {
		go(window.location.pathname, false);
	});
})();
