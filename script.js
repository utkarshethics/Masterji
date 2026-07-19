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

    // Chatbot Widget Logic
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const chatClose = document.getElementById('chat-close');
    const chatSend = document.getElementById('chat-send');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');

    function toggleChat() {
        chatWindow.classList.toggle('open');
    }

    chatBubble.addEventListener('click', toggleChat);
    chatClose.addEventListener('click', toggleChat);

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${sender}`;
        msgDiv.innerText = text;
        
        // Insert before typing indicator
        chatMessages.insertBefore(msgDiv, typingIndicator);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // 1. Add user message
        addMessage(text, 'user');
        chatInput.value = '';
        chatInput.disabled = true;
        chatSend.disabled = true;

        // 2. Show typing indicator
        typingIndicator.style.display = 'block';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            // 3. Send to backend
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();

            // 4. Hide typing indicator & add bot response
            typingIndicator.style.display = 'none';
            
            if (response.ok && data.reply) {
                addMessage(data.reply, 'bot');
            } else {
                addMessage("Sorry, I'm having trouble connecting right now. Please try again later.", 'bot');
            }
        } catch (error) {
            console.error("Chat Error:", error);
            typingIndicator.style.display = 'none';
            addMessage("Sorry, I'm offline at the moment.", 'bot');
        } finally {
            chatInput.disabled = false;
            chatSend.disabled = false;
            chatInput.focus();
        }
    }

    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
