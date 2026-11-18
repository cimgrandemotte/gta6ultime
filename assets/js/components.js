/** GTA VI Ultimate Guide · components.js — navbar, back-to-top, audio player, cookies, copies, spoilers, stat bars */
'use strict';
(function () {
  const { $, $$, onReady, store, copyToClipboard, clamp } = window.GTA6;

  /* Navbar : état scroll + burger mobile */
  function initNavbar() {
    const nav = $('.navbar');
    const onScroll = () => nav && nav.classList.toggle('scrolled', window.scrollY > 40);
    onScroll(); window.addEventListener('scroll', onScroll, { passive: true });

    const burger = $('.burger');
    const panel = $('.mobile-panel');
    if (burger && panel) {
      const toggle = open => {
        const isOpen = open ?? !panel.classList.contains('open');
        panel.classList.toggle('open', isOpen);
        burger.setAttribute('aria-expanded', String(isOpen));
        document.body.style.overflow = isOpen ? 'hidden' : '';
      };
      burger.addEventListener('click', () => toggle());
      panel.addEventListener('click', e => { if (e.target.closest('a')) toggle(false); });
      document.addEventListener('keydown', e => { if (e.key === 'Escape') toggle(false); });
    }
  }

  /* Barre de progression globale + back to top avec anneau */
  function initBackToTop() {
    const bar = $('.scroll-progress');
    const btn = $('.back-top');
    const ring = btn ? btn.querySelector('.ring-fg') : null;
    const C = 132;
    const update = () => {
      const doc = document.documentElement;
      const max = doc.scrollHeight - doc.clientHeight;
      const p = max > 0 ? window.scrollY / max : 0;
      if (bar) bar.style.width = (p * 100).toFixed(2) + '%';
      if (btn) btn.classList.toggle('visible', window.scrollY > 480);
      if (ring) ring.style.strokeDashoffset = String(C * (1 - p));
    };
    update(); window.addEventListener('scroll', update, { passive: true });
    btn && btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  /* Audio player flottant — pistes MP3 originales du build */
  const ASSET_ROOT = location.pathname.includes('/pages/') ? '../../' : '';
  const TRACKS = [
    { label: 'Vice City Night — Ambiance', src: `${ASSET_ROOT}assets/audio/ambiances/homepage_ambiance_vicecity_night_01.mp3` },
    { label: 'Leonida — Nature Florida',    src: `${ASSET_ROOT}assets/audio/ambiances/map_leonida_ambiance_01.mp3` },
    { label: 'Engine V8 — Démarrage',      src: `${ASSET_ROOT}assets/audio/ambiances/vehicles_engine_v8_01.mp3` },
    { label: 'Jason Theme — Synthwave',    src: `${ASSET_ROOT}assets/audio/jingles/characters_jason_theme_01.mp3` },
    { label: 'Lucia Theme — Détermination',src: `${ASSET_ROOT}assets/audio/jingles/characters_lucia_theme_01.mp3` },
    { label: 'Quiz — Bonne réponse',       src: `${ASSET_ROOT}assets/audio/jingles/quiz_correct_answer_01.mp3` },
    { label: 'UI — Clic',                  src: `${ASSET_ROOT}assets/audio/ui/homepage_ui_click_01.mp3` },
    { label: 'UI — Survol',                src: `${ASSET_ROOT}assets/audio/ui/homepage_ui_hover_01.mp3` },
    { label: 'UI — Transition',            src: `${ASSET_ROOT}assets/audio/ui/homepage_ui_transition_01.mp3` },
    { label: 'Arme — Équipement',          src: `${ASSET_ROOT}assets/audio/ui/weapons_equip_sound_01.mp3` }
  ];
  function initAudioPlayer() {
    const fab = $('.audio-fab');
    if (!fab) return;
    const audio = new Audio();
    audio.preload = 'none';
    let current = -1;
    const list = $('.audio-panel .tracks', fab);
    const btnToggle = $('.audio-fab-toggle', fab);
    const btnPlay = $('[data-audio-toggle]', fab);
    const btnMute = $('[data-audio-mute]', fab);

    TRACKS.forEach((t, i) => {
      const b = document.createElement('button');
      b.className = 'track'; b.type = 'button';
      b.innerHTML = `<span aria-hidden="true">▸</span><span>${t.label}</span>`;
      b.addEventListener('click', () => playTrack(i));
      list.appendChild(b);
    });
    const trackBtns = $$('.track', list);
    function syncUI() {
      trackBtns.forEach((b, i) => b.classList.toggle('playing', i === current && !audio.paused));
      if (btnPlay) btnPlay.textContent = audio.paused ? '▶' : '❚❚';
    }
    function playTrack(i) {
      if (i === current && !audio.paused) { audio.pause(); syncUI(); return; }
      current = i; audio.src = TRACKS[i].src;
      audio.play().catch(() => {}); syncUI();
    }
    audio.addEventListener('ended', syncUI);
    audio.addEventListener('play', syncUI);
    audio.addEventListener('pause', syncUI);

    btnToggle && btnToggle.addEventListener('click', () => fab.classList.toggle('open'));
    btnPlay && btnPlay.addEventListener('click', () => { if (current === -1) playTrack(0); else audio.paused ? audio.play() : audio.pause(); });
    btnMute && btnMute.addEventListener('click', () => { audio.muted = !audio.muted; btnMute.textContent = audio.muted ? '🔇' : '🔊'; });
  }

  /* Charge YouTube seulement après activation explicite du lecteur. */
  function initVideoGates() {
    $$('[data-youtube-id]').forEach(gate => {
      const button = $('button', gate);
      if (!button) return;
      button.addEventListener('click', () => {
        const id = gate.dataset.youtubeId;
        if (!/^[A-Za-z0-9_-]{11}$/.test(id || '')) return;
        const iframe = document.createElement('iframe');
        iframe.src = `https://www.youtube-nocookie.com/embed/${id}?rel=0&autoplay=1`;
        iframe.title = gate.dataset.videoTitle || 'Vidéo YouTube';
        iframe.loading = 'lazy';
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
        iframe.referrerPolicy = 'strict-origin-when-cross-origin';
        iframe.allowFullscreen = true;
        gate.replaceChildren(iframe);
        gate.classList.add('loaded');
      }, { once: true });
    });
  }

  /* Cookie banner RGPD minimal */
  function initCookieBanner() {
    const el = $('.cookie');
    if (!el) return;
    if (!store.get('cookiesAccepted', false)) el.classList.add('visible');
    const accept = $('[data-cookie-accept]', el);
    accept && accept.addEventListener('click', () => { store.set('cookiesAccepted', true); el.classList.remove('visible'); });
  }

  /* Boutons copier (cheats / codes) */
  function initCopyButtons() {
    $$('[data-copy]').forEach(btn => btn.addEventListener('click', async () => {
      const ok = await copyToClipboard(btn.dataset.copy || btn.textContent.trim());
      const original = btn.dataset.label || btn.textContent;
      btn.textContent = ok ? 'Copié ✓' : 'Erreur';
      btn.classList.toggle('copied', ok);
      setTimeout(() => { btn.textContent = original; btn.classList.remove('copied'); }, 1600);
    }));
  }

  /* Spoilers */
  function initSpoilers() {
    $$('.spoiler-toggle').forEach(btn => btn.addEventListener('click', () => {
      const box = btn.closest('.spoiler-box');
      if (!box) return;
      box.classList.toggle('revealed');
      btn.textContent = box.classList.contains('revealed') ? 'Masquer les spoilers' : 'Révéler les spoilers';
    }));
  }

  /* Stat bars : remplissage à l'entrée dans le viewport */
  function initStatBars() {
    const io = new IntersectionObserver(entries => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        const fill = e.target; io.unobserve(fill);
        fill.style.width = clamp(parseFloat(fill.dataset.value || '0'), 0, 100) + '%';
      }
    }, { threshold: 0.4 });
    $$('.stat-fill[data-value]').forEach(el => io.observe(el));
  }

  onReady(() => {
    initNavbar(); initBackToTop(); initAudioPlayer(); initVideoGates(); initCookieBanner();
    initCopyButtons(); initSpoilers(); initStatBars();
  });
})();
