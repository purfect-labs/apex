// APEX Pricing Page Interactive Features

class PricingInteractions {
    constructor() {
        this.currentPlan = 'team';
        this.isAnnual = false;
        this.init();
    }
    
    init() {
        this.setupBillingToggle();
        this.setupPricingCalculator();
        this.setupFAQToggles();
        this.setupPlanSelection();
        this.initializeTactileFeedback();
    }
    
    initializeTactileFeedback() {
        // Initialize tactile feedback if not already done
        if (!window.tactileFeedback) {
            // Create a simplified version for the pricing page
            window.tactileFeedback = new TactileFeedback();
        }
    }
    
    setupBillingToggle() {
        const toggle = document.getElementById('annual-toggle');
        const priceAmounts = document.querySelectorAll('.price-amount[data-annual]');
        const annualNotes = document.querySelectorAll('.annual-note');
        
        if (!toggle) return;
        
        toggle.addEventListener('change', () => {
            this.isAnnual = toggle.checked;
            
            // Play toggle sound
            if (window.tactileFeedback) {
                window.tactileFeedback.sounds.click();
            }
            
            // Update body class for CSS styling
            document.body.classList.toggle('billing-annual', this.isAnnual);
            
            // Animate price changes
            priceAmounts.forEach(amount => {
                const monthlyPrice = parseInt(amount.dataset.monthly);
                const annualPrice = parseInt(amount.dataset.annual);
                const targetPrice = this.isAnnual ? annualPrice : monthlyPrice;
                
                this.animatePrice(amount, parseInt(amount.textContent) || monthlyPrice, targetPrice);
            });
            
            // Show/hide annual notes
            annualNotes.forEach(note => {
                if (this.isAnnual) {
                    note.style.opacity = '1';
                    note.style.transform = 'translateY(0)';
                } else {
                    note.style.opacity = '0';
                    note.style.transform = 'translateY(-10px)';
                }
            });
            
            // Update calculator if it exists
            this.updateCalculator();
        });
    }
    
    animatePrice(element, start, end, duration = 500) {
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const currentPrice = Math.round(start + (end - start) * easeOutCubic);
            
            element.textContent = currentPrice;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    setupPricingCalculator() {
        const teamSizeSlider = document.getElementById('team-size');
        const cloudAccountsSlider = document.getElementById('cloud-accounts');
        const environmentsSlider = document.getElementById('environments');
        
        if (!teamSizeSlider) return;
        
        // Setup slider interactions
        [teamSizeSlider, cloudAccountsSlider, environmentsSlider].forEach(slider => {
            if (!slider) return;
            
            slider.addEventListener('input', () => {
                this.updateSliderValue(slider);
                this.updateCalculator();
                
                // Play subtle hover sound on slider change
                if (window.tactileFeedback) {
                    window.tactileFeedback.sounds.hover();
                }
            });
            
            slider.addEventListener('mousedown', () => {
                if (window.tactileFeedback) {
                    window.tactileFeedback.sounds.click();
                }
            });
            
            // Initialize slider values
            this.updateSliderValue(slider);
        });
        
        // Initial calculator update
        this.updateCalculator();
    }
    
    updateSliderValue(slider) {
        const valueElement = document.getElementById(slider.id + '-value');
        if (valueElement) {
            valueElement.textContent = slider.value;
            
            // Add pulse animation to value
            valueElement.style.transform = 'scale(1.1)';
            valueElement.style.background = 'var(--apex-secondary)';
            
            setTimeout(() => {
                valueElement.style.transform = 'scale(1)';
                valueElement.style.background = 'var(--apex-primary)';
            }, 150);
        }
    }
    
    updateCalculator() {
        const teamSize = parseInt(document.getElementById('team-size')?.value || 5);
        const cloudAccounts = parseInt(document.getElementById('cloud-accounts')?.value || 3);
        const environments = parseInt(document.getElementById('environments')?.value || 3);
        
        // Determine recommended tier
        let recommendedTier, tierIcon, basePrice, additionalUserCost = 0;
        
        if (teamSize <= 1 && cloudAccounts <= 3 && environments <= 2) {
            recommendedTier = 'Individual';
            tierIcon = '👨‍💻';
            basePrice = this.isAnnual ? 12 : 15;
        } else if (teamSize <= 25) {
            recommendedTier = 'Team';
            tierIcon = '👥';
            basePrice = this.isAnnual ? 36 : 45;
            
            // Additional users beyond 5
            if (teamSize > 5) {
                const additionalUsers = teamSize - 5;
                additionalUserCost = additionalUsers * (this.isAnnual ? 7 : 9);
            }
        } else {
            recommendedTier = 'Enterprise';
            tierIcon = '🏢';
            basePrice = 'Custom';
        }
        
        // Update UI elements
        const elements = {
            tier: document.getElementById('recommended-tier'),
            icon: document.querySelector('.result-tier .tier-icon'),
            monthlyTotal: document.getElementById('monthly-total'),
            annualTotal: document.getElementById('annual-total'),
            baseCost: document.getElementById('base-cost'),
            additionalUsersCost: document.getElementById('additional-users-cost'),
            additionalUsersRow: document.getElementById('additional-users-row'),
            perUserCost: document.getElementById('per-user-cost'),
            cta: document.getElementById('calculator-cta')
        };
        
        if (elements.tier) elements.tier.textContent = recommendedTier;
        if (elements.icon) elements.icon.textContent = tierIcon;
        
        if (recommendedTier === 'Enterprise') {
            if (elements.monthlyTotal) elements.monthlyTotal.textContent = 'Contact Sales';
            if (elements.annualTotal) elements.annualTotal.textContent = 'Contact Sales';
            if (elements.baseCost) elements.baseCost.textContent = 'Custom pricing';
            if (elements.perUserCost) elements.perUserCost.textContent = 'Volume discounts';
            if (elements.cta) elements.cta.textContent = 'Contact Sales';
        } else {
            const totalMonthly = (this.isAnnual ? basePrice * 12 : basePrice) + 
                               (this.isAnnual ? additionalUserCost * 12 : additionalUserCost);
            const totalAnnual = this.isAnnual ? totalMonthly : totalMonthly * 0.8;
            
            if (elements.monthlyTotal) {
                elements.monthlyTotal.textContent = '$' + (this.isAnnual ? basePrice + additionalUserCost : basePrice + Math.round(additionalUserCost));
            }
            if (elements.annualTotal) {
                elements.annualTotal.textContent = '$' + Math.round(totalAnnual);
            }
            if (elements.baseCost) {
                elements.baseCost.textContent = '$' + basePrice + (this.isAnnual ? '/month' : '/month');
            }
            if (elements.perUserCost) {
                const perUser = Math.round((basePrice + additionalUserCost) / teamSize);
                elements.perUserCost.textContent = '$' + perUser + '/month';
            }
            if (elements.cta) elements.cta.textContent = 'Start Free Trial';
            
            // Show/hide additional users row
            if (elements.additionalUsersRow && elements.additionalUsersCost) {
                if (additionalUserCost > 0) {
                    elements.additionalUsersRow.style.display = 'flex';
                    elements.additionalUsersCost.textContent = '$' + additionalUserCost;
                } else {
                    elements.additionalUsersRow.style.display = 'none';
                }
            }
        }
        
        // Animate the result card
        const resultCard = document.querySelector('.result-card');
        if (resultCard) {
            resultCard.style.transform = 'scale(1.02)';
            resultCard.style.boxShadow = 'var(--shadow-glow-strong)';
            
            setTimeout(() => {
                resultCard.style.transform = 'scale(1)';
                resultCard.style.boxShadow = 'var(--shadow-glow)';
            }, 200);
        }
    }
    
    setupFAQToggles() {
        const faqQuestions = document.querySelectorAll('.faq-question');
        
        faqQuestions.forEach(question => {
            question.addEventListener('click', () => {
                const faqItem = question.closest('.faq-item');
                const isActive = faqItem.classList.contains('active');
                
                // Close all other FAQs
                document.querySelectorAll('.faq-item.active').forEach(item => {
                    if (item !== faqItem) {
                        item.classList.remove('active');
                    }
                });
                
                // Toggle current FAQ
                faqItem.classList.toggle('active');
                
                // Play appropriate sound
                if (window.tactileFeedback) {
                    if (faqItem.classList.contains('active')) {
                        window.tactileFeedback.sounds.notification();
                    } else {
                        window.tactileFeedback.sounds.click();
                    }
                }
                
                // Smooth scroll to FAQ if opening
                if (!isActive && faqItem.classList.contains('active')) {
                    setTimeout(() => {
                        faqItem.scrollIntoView({
                            behavior: 'smooth',
                            block: 'nearest'
                        });
                    }, 100);
                }
            });
        });
    }
    
    setupPlanSelection() {
        const tierCards = document.querySelectorAll('.pricing-card');
        const tierCTAs = document.querySelectorAll('.tier-cta');
        
        // Add hover effects to pricing cards
        tierCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                if (window.tactileFeedback) {
                    window.tactileFeedback.sounds.hover();
                }
            });
            
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.tier-cta')) {
                    const cta = card.querySelector('.tier-cta');
                    if (cta) cta.click();
                }
            });
        });
        
        // Add sound effects to CTA buttons
        tierCTAs.forEach(cta => {
            cta.addEventListener('click', () => {
                if (window.tactileFeedback) {
                    window.tactileFeedback.sounds.deploy();
                }
            });
        });
    }
}

// Plan Selection Functions
function selectPlan(planType) {
    console.log('Selected plan:', planType);
    
    // Play success sound
    if (window.tactileFeedback) {
        setTimeout(() => {
            window.tactileFeedback.sounds.success();
        }, 200);
    }
    
    // Trigger trial modal (from main demo script)
    if (typeof startTrial === 'function') {
        setTimeout(() => {
            startTrial();
        }, 500);
    }
}

function selectCalculatedPlan() {
    const recommendedTier = document.getElementById('recommended-tier')?.textContent || 'Team';
    selectPlan(recommendedTier.toLowerCase());
}

function contactSales() {
    // Play notification sound
    if (window.tactileFeedback) {
        window.tactileFeedback.sounds.notification();
    }
    
    // Create contact sales modal
    const modal = document.createElement('div');
    modal.className = 'trial-modal';
    modal.innerHTML = `
        <div class="trial-overlay"></div>
        <div class="trial-content">
            <div class="trial-header">
                <h3>💬 Contact Sales</h3>
                <button class="trial-close" onclick="this.closest('.trial-modal').remove()">&times;</button>
            </div>
            
            <div class="trial-body">
                <p class="trial-description">
                    Get a personalized demo and discuss enterprise pricing for your team.
                </p>
                
                <form class="trial-form" onsubmit="submitContactForm(event)">
                    <div class="form-row">
                        <input type="text" placeholder="Company Name" required>
                        <input type="text" placeholder="Your Name" required>
                    </div>
                    <div class="form-row">
                        <input type="email" placeholder="Work Email" required>
                        <input type="tel" placeholder="Phone Number" required>
                    </div>
                    <div class="form-row">
                        <select required>
                            <option value="">Team Size</option>
                            <option value="10-25">10-25 users</option>
                            <option value="25-100">25-100 users</option>
                            <option value="100-500">100-500 users</option>
                            <option value="500+">500+ users</option>
                        </select>
                        <select required>
                            <option value="">Timeline</option>
                            <option value="immediate">Immediate</option>
                            <option value="1-3-months">1-3 months</option>
                            <option value="3-6-months">3-6 months</option>
                            <option value="6-months+">6+ months</option>
                        </select>
                    </div>
                    <textarea placeholder="Tell us about your cloud infrastructure and requirements..." rows="4"></textarea>
                    
                    <button type="submit" class="cta-primary">
                        <span class="cta-icon">🚀</span>
                        Schedule Demo
                    </button>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Animate modal in
    setTimeout(() => {
        modal.classList.add('active');
    }, 10);
}

function submitContactForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<span class="cta-icon">⏳</span> Scheduling...';
    submitBtn.disabled = true;
    
    // Play processing sound
    if (window.tactileFeedback) {
        window.tactileFeedback.sounds.processing();
    }
    
    setTimeout(() => {
        submitBtn.innerHTML = '<span class="cta-icon">✅</span> Demo Scheduled!';
        submitBtn.style.background = 'var(--apex-success)';
        
        // Play success sound
        if (window.tactileFeedback) {
            window.tactileFeedback.sounds.success();
        }
        
        setTimeout(() => {
            const modal = form.closest('.trial-modal');
            modal.remove();
            
            // Show confirmation notification
            showNotification(
                '📅 Demo Scheduled!',
                'Check your email for calendar invite and preparation materials.'
            );
        }, 2000);
    }, 1500);
}

function toggleFaq(element) {
    // This function is called from HTML onclick
    const faqItem = element.closest('.faq-item');
    const isActive = faqItem.classList.contains('active');
    
    // Close all other FAQs
    document.querySelectorAll('.faq-item.active').forEach(item => {
        if (item !== faqItem) {
            item.classList.remove('active');
        }
    });
    
    // Toggle current FAQ
    faqItem.classList.toggle('active');
    
    // Play sound effect
    if (window.tactileFeedback) {
        if (faqItem.classList.contains('active')) {
            window.tactileFeedback.sounds.notification();
        } else {
            window.tactileFeedback.sounds.click();
        }
    }
}

function showNotification(title, message) {
    const notification = document.createElement('div');
    notification.className = 'notification-toast';
    notification.innerHTML = `
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
            <button onclick="this.parentNode.parentNode.remove()" class="toast-close">×</button>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--apex-gray-dark);
        border: 1px solid var(--apex-success);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        box-shadow: var(--shadow-glow);
        z-index: 10001;
        max-width: 350px;
        animation: slideInRight 0.5s ease-out;
    `;
    
    // Add toast styles if not exists
    if (!document.querySelector('#toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .toast-content {
                display: flex;
                flex-direction: column;
                gap: var(--space-sm);
                position: relative;
            }
            
            .toast-title {
                color: var(--apex-white);
                font-weight: 600;
                font-size: var(--font-size-lg);
            }
            
            .toast-message {
                color: var(--apex-white-muted);
                font-size: var(--font-size-sm);
                line-height: 1.4;
            }
            
            .toast-close {
                position: absolute;
                top: -5px;
                right: -5px;
                background: none;
                border: none;
                color: var(--apex-white-muted);
                font-size: var(--font-size-lg);
                cursor: pointer;
                width: 24px;
                height: 24px;
            }
            
            .toast-close:hover {
                color: var(--apex-primary);
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Play notification sound
    if (window.tactileFeedback) {
        window.tactileFeedback.sounds.notification();
    }
    
    // Auto remove after 6 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideInRight 0.5s ease-out reverse';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 500);
        }
    }, 6000);
}

// Initialize pricing interactions when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PricingInteractions();
    
    // Add scroll animations to pricing cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '-50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe pricing cards for scroll animations
    document.querySelectorAll('.pricing-card, .calculator-inputs, .result-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });
});

// Add ambient sound on page load
window.addEventListener('load', () => {
    setTimeout(() => {
        if (window.tactileFeedback && window.tactileFeedback.sounds.ambient) {
            window.tactileFeedback.sounds.ambient();
        }
    }, 1000);
});