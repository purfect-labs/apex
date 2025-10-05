// APEX Sales Page Animations - Smooth, professional, engaging

// Smooth scroll for navigation links
document.addEventListener('DOMContentLoaded', () => {
    // Handle navigation smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .testimonial-card, .problem-item, .solution-item').forEach(el => {
        observer.observe(el);
    });
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        .feature-card,
        .testimonial-card,
        .problem-item,
        .solution-item {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
        
        .hero-headline span {
            display: inline-block;
            animation: slideInUp 0.8s ease forwards;
            opacity: 0;
        }
        
        .hero-headline .headline-part:nth-child(1) { animation-delay: 0.1s; }
        .hero-headline .headline-emphasis:nth-child(2) { animation-delay: 0.3s; }
        .hero-headline .headline-part:nth-child(3) { animation-delay: 0.5s; }
        .hero-headline .headline-accent:nth-child(4) { animation-delay: 0.7s; }
        
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .hero-cta {
            animation: fadeInUp 1s ease 0.9s both;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .hero-proof {
            animation: fadeIn 1s ease 1.2s both;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
});