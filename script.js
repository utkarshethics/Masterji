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

    // Razorpay Integration
    const checkoutButtons = document.querySelectorAll('.btn-checkout');
    const API_URL = "https://v97j2s2fo3.execute-api.us-east-1.amazonaws.com";
    
    checkoutButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const originalText = button.innerText;
            button.innerText = "Processing...";
            button.disabled = true;

            try {
                // 1. Create Order via Backend
                const orderResponse = await fetch(`${API_URL}/create-order`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount: 5000, currency: "INR" }) // 5000 paise = 50 INR
                });

                const orderData = await orderResponse.json();

                if (!orderResponse.ok) {
                    throw new Error(orderData.error || 'Failed to create order');
                }

                // 2. Redirect to Razorpay Payment Link
                if (orderData.url) {
                    window.location.href = orderData.url;
                } else {
                    throw new Error("No payment link URL received.");
                }
                
            } catch (err) {
                console.error(err);
                alert("Error initiating checkout: " + err.message);
                button.innerText = originalText;
                button.disabled = false;
            }
        });
    });
});
