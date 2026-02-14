/* ============================================
   pikCarz - Powered by Cubeas
   Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Mobile Menu ─────────────────────── */
  const hamburger   = document.querySelector('.hamburger');
  const mobileMenu  = document.querySelector('.mobile-menu');
  const mobileClose = document.querySelector('.mobile-close');

  hamburger?.addEventListener('click', () => mobileMenu?.classList.add('open'));
  mobileClose?.addEventListener('click', () => mobileMenu?.classList.remove('open'));
  mobileMenu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => mobileMenu.classList.remove('open')));

  /* ── Active Nav Link ─────────────────── */
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });

  /* ── Category Chips ──────────────────── */
  document.querySelectorAll('.cat-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.cat-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
    });
  });

  /* ── Save / Wishlist ─────────────────── */
  document.querySelectorAll('.card-save').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      btn.classList.toggle('saved');
      const svg = btn.querySelector('svg');
      if (btn.classList.contains('saved')) {
        svg.style.fill = '#F05A1A';
        svg.style.stroke = '#F05A1A';
      } else {
        svg.style.fill = 'none';
        svg.style.stroke = 'var(--white)';
      }
    });
  });

  /* ── Contact Form ────────────────────── */
  const form = document.querySelector('.contact-form form');
  form?.addEventListener('submit', e => {
    e.preventDefault();
    const btn = form.querySelector('.form-submit');
    btn.textContent = 'Sending...';
    btn.disabled = true;
    setTimeout(() => {
      btn.textContent = '✓ Message Sent!';
      btn.style.background = '#16A34A';
      form.reset();
      setTimeout(() => {
        btn.textContent = 'Send Message';
        btn.style.background = '';
        btn.disabled = false;
      }, 3000);
    }, 1500);
  });

  /* ── Counter Animation ───────────────── */
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el     = entry.target;
        const target = parseInt(el.dataset.count);
        const suffix = el.dataset.suffix || '';
        let current  = 0;
        const step   = Math.ceil(target / 60);
        const timer  = setInterval(() => {
          current += step;
          if (current >= target) { current = target; clearInterval(timer); }
          el.textContent = current.toLocaleString() + suffix;
        }, 25);
        observer.unobserve(el);
      });
    }, { threshold: 0.5 });
    counters.forEach(c => observer.observe(c));
  }

  /* ── Filter Toggle (mobile) ──────────── */
  const filterToggle = document.getElementById('filter-toggle');
  const filterPanel  = document.querySelector('.filter-panel');
  filterToggle?.addEventListener('click', () => {
    filterPanel?.classList.toggle('open');
    filterToggle.textContent = filterPanel?.classList.contains('open') ? '✕ Close Filters' : '⚙ Filters';
  });

  /* ── Scroll Fade-in ──────────────────── */
  const fadeEls = document.querySelectorAll('.scroll-fade');
  if (fadeEls.length) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('fade-in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    fadeEls.forEach(el => io.observe(el));
  }

});
