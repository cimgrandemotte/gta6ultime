/** GTA VI Ultimate Guide · main.js — boot : loading screen, curseur viseur, orchestration */
'use strict';
(function () {
  const { $, onReady } = window.GTA6;

  /* Écran de chargement */
  function initLoadingScreen() {
    const el = $('.loading-screen');
    if (!el) return;
    const done = () => el.classList.add('done');
    if (document.readyState === 'complete') setTimeout(done, 900);
    else window.addEventListener('load', () => setTimeout(done, 900), { once: true });
    setTimeout(done, 4000); // garde-fou
  }

  /* Curseur viseur GTA — uniquement sur pointeur fin + motion OK */
  function initCustomCursor() {
    const fine = window.matchMedia('(pointer: fine)').matches;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!fine || reduced) return;
    const dot = document.createElement('div');
    dot.className = 'gta-cursor';
    dot.setAttribute('aria-hidden', 'true');
    dot.innerHTML = '<svg viewBox="0 0 40 40" width="34" height="34"><circle cx="20" cy="20" r="11" fill="none" stroke="#00D4FF" stroke-width="1.6"/><circle cx="20" cy="20" r="2" fill="#FF2D78"/><line x1="20" y1="0" x2="20" y2="12" stroke="#00D4FF" stroke-width="1.6"/><line x1="20" y1="28" x2="20" y2="40" stroke="#00D4FF" stroke-width="1.6"/><line x1="0" y1="20" x2="12" y2="20" stroke="#00D4FF" stroke-width="1.6"/><line x1="28" y1="20" x2="40" y2="20" stroke="#00D4FF" stroke-width="1.6"/></svg>';
    Object.assign(dot.style, { position: 'fixed', zIndex: 3000, pointerEvents: 'none', left: 0, top: 0, transform: 'translate(-50%,-50%)', mixBlendMode: 'screen' });
    document.body.appendChild(dot);
    let x = -100, y = -100, tx = -100, ty = -100;
    window.addEventListener('mousemove', e => { tx = e.clientX; ty = e.clientY; }, { passive: true });
    (function loop() {
      x += (tx - x) * 0.35; y += (ty - y) * 0.35;
      dot.style.transform = `translate(${x - 17}px, ${y - 17}px)`;
      requestAnimationFrame(loop);
    })();
  }

  onReady(() => { initLoadingScreen(); initCustomCursor(); });
})();
