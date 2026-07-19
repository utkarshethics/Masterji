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
    
    checkoutButtons.forEach(button => {
        button.addEventListener('click', () => {
            const options = {
                "key": "rzp_test_TFCjsf20DQ4rm9", // User provided live test key
                "amount": "5000", // Amount is in currency subunits. 5000 paise = INR 50
                "currency": "INR",
                "name": "masterji.online",
                "description": "Doorstep Tailor Booking Fee",
                "image": "logo.png.jpeg",
                "handler": function (response) {
                    alert("Booking Successful! Payment ID: " + response.razorpay_payment_id);
                    // You can perform further actions here (like storing booking to a backend or Google Sheet)
                },
                "prefill": {
                    "name": "",
                    "email": "",
                    "contact": ""
                },
                "notes": {
                    "address": "Doorstep Measurement Service"
                },
                "theme": {
                    "color": "#FFD700" // Matching Master Ji yellow
                }
            };
            
            const rzp = new Razorpay(options);
            rzp.on('payment.failed', function (response){
                alert("Payment Failed: " + response.error.description);
            });
            rzp.open();
        });
    });
});
