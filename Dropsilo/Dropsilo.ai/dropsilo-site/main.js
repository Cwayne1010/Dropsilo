/* ============================================
   DROPSILO.AI — Site JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  // --- Navbar scroll behavior ---
  const nav = document.querySelector('.nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    });
  }

  // --- Mobile menu toggle ---
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
      toggle.classList.toggle('active');
    });
    // Close on link click
    links.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        links.classList.remove('open');
        toggle.classList.remove('active');
      });
    });
  }

  // --- Scroll-based fade-in animations ---
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px'
  };

  const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        fadeObserver.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.fade-in').forEach(el => {
    fadeObserver.observe(el);
  });

  // --- Smooth scroll for anchor links ---
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // --- Contact form handling ---
  const CONTACT_ENDPOINT = 'https://eliwayne.app.n8n.cloud/webhook/dropsilo-contact';

  const form = document.querySelector('.contact-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('.btn-primary');
      const originalHTML = btn.innerHTML;
      btn.textContent = 'Sending...';
      btn.style.opacity = '0.7';
      btn.disabled = true;

      const data = {
        name: form.querySelector('#name').value,
        email: form.querySelector('#email').value,
        company: form.querySelector('#company').value,
        interest: form.querySelector('#interest').value,
        message: form.querySelector('#message').value,
      };

      try {
        const res = await fetch(CONTACT_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        const text = await res.text();
        const result = text ? JSON.parse(text) : {};

        if (res.ok) {
          btn.textContent = 'Message Sent!';
          btn.style.opacity = '1';
          btn.style.background = '#22c55e';
          form.reset();
          setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.style.background = '';
            btn.disabled = false;
          }, 3000);
        } else {
          btn.textContent = result.message || 'Something went wrong';
          btn.style.opacity = '1';
          btn.style.background = '#ef4444';
          setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.style.background = '';
            btn.disabled = false;
          }, 3000);
        }
      } catch (err) {
        btn.textContent = 'Network error — try again';
        btn.style.opacity = '1';
        btn.style.background = '#ef4444';
        setTimeout(() => {
          btn.innerHTML = originalHTML;
          btn.style.background = '';
          btn.disabled = false;
        }, 3000);
      }
    });
  }

  // --- Active nav link highlighting ---
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
});

/* --- CSS for fade-in animation (injected) --- */
const style = document.createElement('style');
style.textContent = `
  .fade-in {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 0.6s ease, transform 0.6s ease;
  }
  .fade-in.visible {
    opacity: 1;
    transform: translateY(0);
  }
  .fade-in:nth-child(2) { transition-delay: 0.1s; }
  .fade-in:nth-child(3) { transition-delay: 0.2s; }
  .fade-in:nth-child(4) { transition-delay: 0.3s; }
`;
document.head.appendChild(style);
