/** GTA VI Ultimate Guide · animations.js — reveals, compteurs, particules d'or */
'use strict';
(function () {
  const { $, $$, onReady, clamp } = window.GTA6;

  /* Reveal au scroll */
  function initReveal() {
    const io = new IntersectionObserver(entries => {
      for (const e of entries) {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
      }
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    $$('.reveal, .reveal-left, .reveal-right').forEach(el => io.observe(el));
  }

  /* Compteurs animés — <span data-count="99" data-suffix="%"> */
  function initCounters() {
    const io = new IntersectionObserver(entries => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        const el = e.target; io.unobserve(el);
        const target = parseFloat(el.dataset.count || '0');
        const suffix = el.dataset.suffix || '';
        const dur = parseFloat(el.dataset.duration || '1.6') * 1000;
        const start = performance.now();
        const decimals = (el.dataset.count || '').includes('.') ? 1 : 0;
        function frame(now) {
          const p = clamp((now - start) / dur, 0, 1);
          const eased = 1 - Math.pow(2, -9 * p);
          const val = target * (p === 1 ? 1 : eased);
          el.textContent = val.toFixed(decimals).replace('.', ',') + suffix;
          if (p < 1) requestAnimationFrame(frame); else el.textContent = target.toFixed(decimals).replace('.', ',') + suffix;
        }
        requestAnimationFrame(frame);
      }
    }, { threshold: 0.6 });
    $$('[data-count]').forEach(el => io.observe(el));
  }

  /* Particules dorées — canvas plein écran derrière le hero */
  function initGoldParticles(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    let W, H, particles = [];
    const DPR = Math.min(2, window.devicePixelRatio || 1);

    function resize() {
      W = canvas.offsetWidth; H = canvas.offsetHeight;
      canvas.width = W * DPR; canvas.height = H * DPR;
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      const n = Math.round((W * H) / 26000);
      particles = Array.from({ length: n }, () => spawn(true));
    }
    function spawn(anywhere) {
      return {
        x: Math.random() * W,
        y: anywhere ? Math.random() * H : H + 10,
        r: Math.random() * 2.1 + 0.6,
        vy: -(Math.random() * 0.35 + 0.12),
        vx: (Math.random() - 0.5) * 0.22,
        phase: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.02 + 0.008
      };
    }
    let raf;
    function loop() {
      ctx.clearRect(0, 0, W, H);
      for (const p of particles) {
        p.y += p.vy; p.x += p.vx + Math.sin(p.phase) * 0.15; p.phase += p.speed;
        if (p.y < -12 || p.x < -12 || p.x > W + 12) Object.assign(p, spawn(false));
        const glow = 0.55 + 0.45 * Math.sin(p.phase * 2);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,215,0,${0.75 * glow})`;
        ctx.shadowColor = 'rgba(255,215,0,.9)';
        ctx.shadowBlur = 8 * glow;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
      raf = requestAnimationFrame(loop);
    }
    resize(); loop();
    window.addEventListener('resize', () => { cancelAnimationFrame(raf); resize(); loop(); }, { passive: true });
  }

  onReady(() => { initReveal(); initCounters(); initGoldParticles('gold-particles'); });
})();
