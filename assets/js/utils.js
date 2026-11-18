/** GTA VI Ultimate Guide · utils.js — helpers partagés */
'use strict';
const $  = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
const onReady = fn => (document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn));
const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
const debounce = (fn, wait = 150) => {
  let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), wait); };
};
const formatFR = n => new Intl.NumberFormat('fr-FR').format(n);

/** Stockage local namespacé */
const store = {
  get(key, fallback = null) {
    try { const v = localStorage.getItem('gta6.' + key); return v === null ? fallback : JSON.parse(v); }
    catch { return fallback; }
  },
  set(key, value) { try { localStorage.setItem('gta6.' + key, JSON.stringify(value)); } catch { /* privé */ } },
  remove(key) { try { localStorage.removeItem('gta6.' + key); } catch { /* noop */ } }
};

/** Copie presse-papier avec fallback */
async function copyToClipboard(text) {
  try { await navigator.clipboard.writeText(text); return true; }
  catch {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    let ok = false; try { ok = document.execCommand('copy'); } catch { ok = false; }
    ta.remove(); return ok;
  }
}
window.GTA6 = Object.assign(window.GTA6 || {}, { $, $$, onReady, clamp, debounce, formatFR, store, copyToClipboard });
