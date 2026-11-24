/* The opening question: bring the chosen version of the home page in place, quietly.
 *
 * Every answer in the dock is a real link (/engineering, /security, ...), so the page works
 * without this script. With it, a version is fetched only when the visitor asks for it (on
 * hover or focus, to have it ready, or on click), never with the default page.
 *
 * The arrival changes only what differs. The fetched page is compared with this one element by
 * element: what is equal is left untouched (the hero and its drawing, the portrait, education,
 * shared jobs and bullets), a text that changed is rewritten where it stands, a list keeps the
 * items both versions share and takes in the new ones. Sections are moved only if their place
 * changed, and the reader stays on the section they were reading. What changed glitches once
 * (short labels decode, see brand-decode.js); nothing is hidden. Any failure follows the link.
 */
(function () {
	'use strict';

	var KEPT = 'section-started';   // the hero is the same on every version, and its drawing is live
	var READING = 0.35;             // share of the viewport height: the line the reader is on
	var SHORT = 48;                 // characters: up to here a changed text decodes, beyond it glitches
	var dock = document.querySelector('.need-dock');
	var wrapper = document.querySelector('.wrapper[data-profile]');
	if (!dock || !wrapper || !window.fetch || !window.DOMParser || !window.history.pushState) return;

	var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
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

	function elements(node) {
		return Array.prototype.slice.call(node.children);
	}

	function hasOwnText(node) {
		for (var child = node.firstChild; child; child = child.nextSibling) {
			if (child.nodeType === 3 && /\S/.test(child.nodeValue)) return true;
		}
		return false;
	}

	function syncAttributes(from, to) {
		Array.prototype.slice.call(to.attributes).forEach(function (a) {
			if (!from.hasAttribute(a.name)) to.removeAttribute(a.name);
		});
		Array.prototype.slice.call(from.attributes).forEach(function (a) {
			if (to.getAttribute(a.name) !== a.value) to.setAttribute(a.name, a.value);
		});
	}

	// Children that pair off one to one: same count and tags, and none merely moved to another place.
	function paired(olds, news) {
		if (olds.length !== news.length) return false;
		for (var i = 0; i < olds.length; i++) if (olds[i].tagName !== news[i].tagName) return false;
		return !news.some(function (n, i) {
			return !olds[i].isEqualNode(n) && olds.some(function (o, j) { return j !== i && o.isEqualNode(n); });
		});
	}

	// A list: keep the items both sides share (untouched), take in the new ones, drop the rest.
	function reconcile(parent, news, changed) {
		var olds = elements(parent), kept = [];
		news.forEach(function (n, i) {
			var node = null;
			for (var k = 0; k < olds.length && !node; k++) {
				if (kept.indexOf(olds[k]) === -1 && olds[k].isEqualNode(n)) node = olds[k];
			}
			if (node) kept.push(node);
			else { node = document.importNode(n, true); changed.push(node); }
			if (parent.children[i] !== node) parent.insertBefore(node, parent.children[i] || null);
		});
		olds.forEach(function (o) {
			if (kept.indexOf(o) === -1 && o.parentNode === parent) parent.removeChild(o);
		});
	}

	// Makes old equal to next, touching only what differs; changed collects what a reader would see change.
	function morph(old, next, changed) {
		if (old.isEqualNode(next)) return;
		syncAttributes(next, old);
		var olds = elements(old), news = elements(next);
		if (!olds.length && !news.length) {
			if (old.textContent !== next.textContent) { old.textContent = next.textContent; changed.push(old); }
		} else if (hasOwnText(old) || hasOwnText(next)) {
			old.innerHTML = next.innerHTML;   // text mixed with markup: one unit
			changed.push(old);
		} else if (paired(olds, news)) {
			olds.forEach(function (o, i) { morph(o, news[i], changed); });
		} else {
			reconcile(old, news, changed);
		}
	}

	// The version's sections in the version's order; a section moves only if its place changed.
	function arrange(next, changed) {
		var wanted = {};
		elements(next).forEach(function (incoming, i) {
			if (!incoming.id) return;
			var current = document.getElementById(incoming.id);
			if (!current) { current = document.importNode(incoming, true); changed.push(current); }
			else if (incoming.id !== KEPT) morph(current, incoming, changed);
			if (wrapper.children[i] !== current) wrapper.insertBefore(current, wrapper.children[i] || null);
			wanted[incoming.id] = true;
		});
		elements(wrapper).forEach(function (section) {
			if (section.id && !wanted[section.id]) wrapper.removeChild(section);
		});
	}

	// The section on the reading line and where it sits, to put the reader back on it. (The first
	// section still showing a sliver under the header is not what they are reading.)
	function place() {
		var line = window.innerHeight * READING, sections = elements(wrapper);
		for (var i = 0; i < sections.length; i++) {
			var box = sections[i].getBoundingClientRect();
			if (sections[i].id && box.top <= line && box.bottom > line) return { id: sections[i].id, top: box.top };
		}
		return null;
	}

	function restore(held) {
		var section = held && document.getElementById(held.id);
		if (!section) return;
		var moved = section.getBoundingClientRect().top - held.top;
		if (Math.abs(moved) > 1) window.scrollBy({ top: moved, left: 0, behavior: 'instant' });
	}

	// An effect must leave no trace: an empty class or style attribute would make the element
	// look different from the same element in the next version, and it would glitch for nothing.
	function tidy(el) {
		['class', 'style'].forEach(function (name) {
			if (el.getAttribute(name) === '') el.removeAttribute(name);
		});
	}

	function glitch(changed) {
		if (reduce && reduce.matches) return;
		var seen = 0;
		changed.forEach(function (el) {
			if (!el.isConnected) return;
			var box = el.getBoundingClientRect();
			if (box.bottom < 0 || box.top > window.innerHeight) return;   // out of sight: nothing to show
			if (!el.children.length && el.textContent.length <= SHORT) {
				el.dispatchEvent(new CustomEvent('signal:decode', { bubbles: true }));
				return;
			}
			el.style.animationDelay = Math.min(seen++, 8) * 30 + 'ms';   // a ripple, not a flash
			el.classList.add('version-glitch');
		});
	}
	document.addEventListener('animationend', function (e) {
		if (e.animationName !== 'version-glitch') return;
		e.target.classList.remove('version-glitch');
		e.target.style.animationDelay = '';
		tidy(e.target);
	});

	function copyHrefs(here, there) {
		for (var i = 0; i < here.length && i < there.length; i++) here[i].setAttribute('href', there[i].getAttribute('href'));
	}

	// The dock, the language links and the head follow the version: attributes only, no rebuilding.
	function follow(doc) {
		var answers = dock.querySelectorAll('a.need-a'), theirs = doc.querySelectorAll('.need-dock a.need-a');
		var changedAnswer = null;
		for (var i = 0; i < answers.length && i < theirs.length; i++) {
			answers[i].removeAttribute('aria-busy');
			if (theirs[i].getAttribute('aria-current')) {
				if (!answers[i].getAttribute('aria-current')) changedAnswer = answers[i];
				answers[i].setAttribute('aria-current', 'page');
				dock.querySelector('.need-status').textContent = answers[i].textContent;
				dock.scrollLeft = answers[i].offsetLeft - (dock.clientWidth - answers[i].offsetWidth) / 2;
			} else {
				answers[i].removeAttribute('aria-current');
			}
		}
		['.lang-switch a', '.sheet-langs a'].forEach(function (selector) {
			copyHrefs(document.querySelectorAll(selector), doc.querySelectorAll(selector));
		});
		var head = 'link[rel="canonical"], link[rel="alternate"][hreflang]';
		copyHrefs(document.head.querySelectorAll(head), doc.head.querySelectorAll(head));
		return changedAnswer;
	}

	// The decision lands: the pulse runs down the orange line now (brand-glow.css), if it is playing.
	function pulse() {
		if (!document.getAnimations) return;
		document.getAnimations().forEach(function (animation) {
			var name = animation.animationName;
			if ((name === 'decision-pulse' || name === 'core-flash') && animation.playState === 'running') {
				animation.currentTime = animation.effect.getComputedTiming().delay;
			}
		});
	}

	// Brings the page to the version in doc; false when doc is not a home page.
	function show(doc) {
		var next = doc.querySelector('.wrapper[data-profile]');
		if (!next) return false;
		document.dispatchEvent(new CustomEvent('signal:settle'));   // a decode still running lands first
		Array.prototype.forEach.call(wrapper.querySelectorAll('.signal-lock, [class=""], [style=""]'), function (el) {
			el.classList.remove('signal-lock');
			tidy(el);
		});
		var held = place(), changed = [];
		arrange(next, changed);
		wrapper.setAttribute('data-profile', next.getAttribute('data-profile'));
		var chosen = follow(doc);
		restore(held);
		if (chosen) changed.push(chosen);   // the answer itself decodes: the choice registered
		glitch(changed);
		pulse();
		window.dispatchEvent(new CustomEvent('profile:change'));
		return true;
	}

	// The last answer asked for wins: a slower, earlier request that lands afterwards is dropped.
	var turn = 0, shown = window.location.pathname;
	function go(url, push) {
		var mine = ++turn;
		return load(url).then(function (doc) {
			if (mine !== turn) return;
			if (!show(doc)) throw new Error('not a home page: ' + url);
			shown = url;
			if (push) window.history.pushState({ version: true }, '', url);
		}).catch(function () {
			if (mine === turn) window.location.href = url;
		});
	}

	function answer(target) {
		return target && target.closest ? target.closest('a.need-a') : null;
	}

	dock.addEventListener('click', function (e) {
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
	dock.addEventListener('pointerover', warm, { passive: true });
	dock.addEventListener('touchstart', warm, { passive: true });
	dock.addEventListener('focusin', warm);

	window.addEventListener('popstate', function () {
		// a fragment link (a menu section, "Back to top") also fires popstate: same page, nothing to do
		if (window.location.pathname !== shown) go(window.location.pathname, false);
	});
})();
