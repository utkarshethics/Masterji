document.addEventListener('DOMContentLoaded', () => {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    mobileMenuBtn.addEventListener('click', () => {
        mobileMenuBtn.classList.toggle('active');
        navLinks.classList.toggle('active');
    });

    // Close mobile menu on link click
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenuBtn.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });

    // Reveal animations on scroll
    const reveals = document.querySelectorAll('.reveal');

    function reveal() {
        const windowHeight = window.innerHeight;
        const elementVisible = 150;

        reveals.forEach(revealElement => {
            const elementTop = revealElement.getBoundingClientRect().top;

            if (elementTop < windowHeight - elementVisible) {
                revealElement.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', reveal);
    reveal(); // Trigger once on load

    // Book Now → WhatsApp redirect (no payment modal)
    const WHATSAPP_URL = "https://wa.me/919019745931?text=" + encodeURIComponent("Hi Masterji, I'd like to book a doorstep tailor. Please share details.");

    document.querySelectorAll('.btn-checkout').forEach(button => {
        button.addEventListener('click', () => {
            window.open(WHATSAPP_URL, '_blank', 'noopener');
        });
    });

    // Contact Form Modal
    const contactModal = document.getElementById('contact-modal');
    const contactForm = document.getElementById('contact-form');
    const contactSuccess = document.getElementById('contact-success');

    function openContactModal() {
        contactModal.hidden = false;
        document.body.style.overflow = 'hidden';
        contactForm.hidden = false;
        contactSuccess.hidden = true;
        contactForm.reset();
        clearErrors();
    }

    function closeContactModal() {
        contactModal.hidden = true;
        document.body.style.overflow = '';
    }

    function clearErrors() {
        contactForm.querySelectorAll('[aria-invalid="true"]').forEach(el => {
            el.removeAttribute('aria-invalid');
        });
        contactForm.querySelectorAll('.form-error').forEach(el => {
            el.textContent = '';
        });
    }

    function showError(input, message) {
        input.setAttribute('aria-invalid', 'true');
        const errorEl = input.parentElement.querySelector('.form-error');
        if (errorEl) errorEl.textContent = message;
    }

    function validateForm() {
        let valid = true;
        clearErrors();

        const name = contactForm.querySelector('#contact-name');
        if (!name.value.trim()) {
            showError(name, 'Name is required');
            valid = false;
        }

        const email = contactForm.querySelector('#contact-email');
        const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.value.trim() || !emailRe.test(email.value)) {
            showError(email, 'Valid email is required');
            valid = false;
        }

        const message = contactForm.querySelector('#contact-message');
        if (!message.value.trim()) {
            showError(message, 'Message is required');
            valid = false;
        }

        return valid;
    }

    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;

        // Simulate API call (replace with real endpoint)
        await new Promise(r => setTimeout(r, 1000));

        contactForm.hidden = true;
        contactSuccess.hidden = false;
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });

    document.addEventListener('click', (event) => {
        if (event.target.closest('[data-close-contact]')) {
            closeContactModal();
        }
        if (event.target.closest('[data-open-contact]')) {
            event.preventDefault();
            openContactModal();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !contactModal.hidden) {
            closeContactModal();
        }
    });

});
