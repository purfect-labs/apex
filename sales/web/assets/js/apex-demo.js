// APEX Interactive Demo - Make it HAWT and engaging!

// Terminal Demo Animation
class TerminalDemo {
    constructor() {
        this.commands = [
            { cmd: 'apex env switch staging', output: '🔄 Switched to staging environment\n📍 AWS: kenect-staging | GCP: kenect-service-staging | K8s: staging-cluster' },
            { cmd: 'apex teams status --aggregate', output: '👥 Cross-team Infrastructure Status\n\n🔧 Platform Team (5 active):\n├── CI/CD Pipeline: ✅ Healthy\n├── Monitoring Stack: ⚠️  High memory usage\n└── Secret Management: ✅ Synced\n\n💳 Payments Team (3 active):\n├── payment-service: ✅ 3 replicas running\n├── fraud-detection: ✅ Processing 1.2K req/s\n└── billing-service: 🔄 Deploying v2.1.3' },
            { cmd: 'apex ownership scan --repo microservices', output: '🔍 Code Ownership Analysis\n\n📦 service/payment/\n├── Primary: @payments-team (87% commits)\n├── Secondary: @platform-team (13% commits)\n└── Last modified: 2h ago by sarah.chen\n\n🎯 Coherence Score: 94% (Excellent)' },
            { cmd: 'apex deploy stack --env prod --dry-run', output: '🧪 Deployment Preview (staging → prod)\n\n📊 Impact Analysis:\n├── 🔄 3 services will be updated\n├── ⚡ 1 new migration required\n├── 🔐 2 secrets need rotation\n└── ⏱️  Estimated downtime: 0s (blue-green)\n\n🚀 Ready to deploy with --confirm flag' },
            { cmd: 'apex coherence check --all-envs', output: '🔍 Environment Coherence Analysis\n\n📋 Configuration Drift:\n✅ dev ↔ staging: 0 differences\n⚠️  staging ↔ prod: 3 drift points\n  ├── redis.maxmemory: 2gb vs 8gb\n  ├── logging.level: debug vs info\n  └── replicas.payment-service: 2 vs 5\n\n💡 Sync recommendations available' },
            { cmd: 'apex insights --teams --last-sprint', output: '📈 Cross-Team Sprint Insights\n\n🏆 Team Performance:\n🥇 Payments Team\n  ├── 94% story completion\n  ├── 0.8 bugs per story\n  └── 2.1 day avg cycle time\n\n🔄 Deployment Metrics:\n├── 23 deployments across all teams\n├── 98.3% success rate\n└── 0 rollbacks required' },
            { cmd: 'apex db tunnel prod --service users --read-only', output: '🔐 Establishing secure production tunnel\n\n🛡️  Security Verification:\n✅ MFA token verified\n✅ Production access approved\n⚠️  READ-ONLY mode enforced\n\n✅ Connected via SSM Session Manager' }
        ];
        
        this.currentIndex = 0;
        this.typingSpeed = 80;
        this.pauseTime = 3000;
        
        this.init();
    }
    
    init() {
        this.startDemo();
    }
    
    async startDemo() {
        while (true) {
            await this.typeCommand();
            await this.showOutput();
            await this.pause();
            this.nextCommand();
        }
    }
    
    async typeCommand() {
        const command = this.commands[this.currentIndex].cmd;
        const cmdElement = document.getElementById('typing-demo');
        
        cmdElement.textContent = '';
        
        for (let i = 0; i < command.length; i++) {
            cmdElement.textContent += command[i];
            
            // Add terminal typing sound
            if (window.tactileFeedback && Math.random() > 0.7) {
                window.tactileFeedback.sounds.terminal();
            }
            
            await this.sleep(this.typingSpeed);
        }
    }
    
    async showOutput() {
        const output = this.commands[this.currentIndex].output;
        const outputElement = document.getElementById('terminal-output');
        
        await this.sleep(500);
        outputElement.innerHTML = output.replace(/\n/g, '<br>');
    }
    
    async pause() {
        await this.sleep(this.pauseTime);
    }
    
    nextCommand() {
        this.currentIndex = (this.currentIndex + 1) % this.commands.length;
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Interactive Stats Counter
class StatsCounter {
    constructor() {
        this.stats = [
            { element: '.stat-number', targets: [2847, 47, 12] },
        ];
        this.init();
    }
    
    init() {
        this.observeStats();
    }
    
    observeStats() {
        const statsSection = document.querySelector('.hero-proof');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateStats();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        if (statsSection) {
            observer.observe(statsSection);
        }
    }
    
    animateStats() {
        const statNumbers = document.querySelectorAll('.stat-number');
        const targets = [2847, 47, 12];
        
        statNumbers.forEach((stat, index) => {
            this.countUp(stat, 0, targets[index], 2000);
        });
    }
    
    countUp(element, start, end, duration) {
        let current = start;
        const increment = end > start ? 1 : -1;
        const stepTime = Math.abs(Math.floor(duration / (end - start)));
        
        const timer = setInterval(() => {
            current += increment;
            
            if (end.toString().includes('K')) {
                element.textContent = '$' + current + 'K';
            } else if (end.toString().includes('%')) {
                element.textContent = current + '%';
            } else {
                element.textContent = current.toLocaleString();
            }
            
            if (current === end) {
                clearInterval(timer);
            }
        }, stepTime);
    }
}

// Tab Switcher for Preview
class TabSwitcher {
    constructor() {
        this.tabs = document.querySelectorAll('.tab');
        this.content = document.querySelector('.preview-content');
        this.tabData = {
            aws: {
                title: 'production-cluster',
                type: 'EKS Cluster • us-west-2',
                status: 'online'
            },
            gcp: {
                title: 'staging-gke-cluster',
                type: 'GKE Cluster • us-central1',
                status: 'online'
            },
            k8s: {
                title: 'api-deployment',
                type: 'Deployment • 12/12 pods',
                status: 'online'
            }
        };
        
        this.init();
    }
    
    init() {
        this.tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Auto-rotate tabs
        this.autoRotate();
    }
    
    switchTab(tabId) {
        // Update active tab
        this.tabs.forEach(tab => tab.classList.remove('active'));
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
        
        // Update content
        const data = this.tabData[tabId];
        if (data) {
            this.updatePreviewContent(data);
        }
    }
    
    updatePreviewContent(data) {
        const nameElement = document.querySelector('.resource-name');
        const typeElement = document.querySelector('.resource-type');
        
        if (nameElement) nameElement.textContent = data.title;
        if (typeElement) typeElement.textContent = data.type;
    }
    
    autoRotate() {
        const tabIds = ['aws', 'gcp', 'k8s'];
        let currentIndex = 0;
        
        setInterval(() => {
            currentIndex = (currentIndex + 1) % tabIds.length;
            this.switchTab(tabIds[currentIndex]);
        }, 4000);
    }
}

// Scroll Animations
class ScrollAnimations {
    constructor() {
        this.init();
    }
    
    init() {
        this.observeElements();
        this.updateNavOnScroll();
    }
    
    observeElements() {
        const elements = document.querySelectorAll('.feature-card, .testimonial-card, .problem-item, .solution-item');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        elements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }
    
    updateNavOnScroll() {
        const nav = document.querySelector('.apex-nav');
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                nav.style.background = 'rgba(10, 10, 10, 0.95)';
            } else {
                nav.style.background = 'rgba(10, 10, 10, 0.9)';
            }
        });
    }
}

// Interactive Functions for CTAs
function startTrial() {
    // Create trial signup modal
    const modal = document.createElement('div');
    modal.className = 'trial-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeTrial()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>🚀 Start Your APEX Free Trial</h3>
                    <button onclick="closeTrial()" class="close-btn">×</button>
                </div>
                <div class="modal-body">
                    <p>Get 14 days of full APEX access. No credit card required.</p>
                    <form class="trial-form">
                        <div class="form-group">
                            <label>Work Email</label>
                            <input type="email" placeholder="you@company.com" required>
                        </div>
                        <div class="form-group">
                            <label>What's your main cloud provider?</label>
                            <select required>
                                <option value="">Choose one...</option>
                                <option value="aws">AWS</option>
                                <option value="gcp">Google Cloud</option>
                                <option value="azure">Azure</option>
                                <option value="multi">Multiple clouds</option>
                            </select>
                        </div>
                        <button type="submit" class="btn-primary">
                            <span class="cta-icon">⚡</span>
                            Download APEX + Get Trial License
                        </button>
                    </form>
                    <div class="trial-features">
                        <div class="feature">✅ All features included</div>
                        <div class="feature">✅ Unlimited cloud accounts</div>
                        <div class="feature">✅ No credit card required</div>
                        <div class="feature">✅ Cancel anytime</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal styles
    const styles = `
        <style>
            .trial-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(10px);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.3s ease;
            }
            
            .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
            }
            
            .modal-content {
                background: var(--apex-gray-dark);
                border: 1px solid var(--apex-primary);
                border-radius: var(--radius-xl);
                padding: var(--space-2xl);
                max-width: 500px;
                width: 90%;
                position: relative;
                animation: slideUp 0.3s ease;
                box-shadow: var(--shadow-glow);
            }
            
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: var(--space-lg);
                padding-bottom: var(--space-lg);
                border-bottom: 1px solid var(--apex-gray);
            }
            
            .modal-header h3 {
                color: var(--apex-white);
                margin: 0;
            }
            
            .close-btn {
                background: none;
                border: none;
                color: var(--apex-white-muted);
                font-size: var(--font-size-2xl);
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .close-btn:hover {
                color: var(--apex-primary);
            }
            
            .trial-form {
                margin-bottom: var(--space-lg);
            }
            
            .form-group {
                margin-bottom: var(--space-md);
            }
            
            .form-group label {
                display: block;
                color: var(--apex-white);
                font-weight: var(--font-weight-medium);
                margin-bottom: var(--space-xs);
            }
            
            .form-group input,
            .form-group select {
                width: 100%;
                background: var(--apex-black);
                border: 1px solid var(--apex-gray);
                border-radius: var(--radius-md);
                padding: var(--space-md);
                color: var(--apex-white);
                font-family: var(--font-family-primary);
            }
            
            .form-group input:focus,
            .form-group select:focus {
                outline: none;
                border-color: var(--apex-primary);
                box-shadow: 0 0 0 2px rgba(0, 217, 255, 0.2);
            }
            
            .trial-features {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: var(--space-sm);
                margin-top: var(--space-lg);
                padding-top: var(--space-lg);
                border-top: 1px solid var(--apex-gray);
            }
            
            .feature {
                color: var(--apex-white-muted);
                font-size: var(--font-size-sm);
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideUp {
                from { transform: translateY(30px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', styles);
    document.body.appendChild(modal);
    
    // Handle form submission
    const form = modal.querySelector('.trial-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Add loading state
        submitBtn.innerHTML = '<span class="cta-icon">⏳</span> Generating License...';
        submitBtn.disabled = true;
        submitBtn.style.background = 'var(--apex-warning)';
        
        // Play processing sound
        if (window.tactileFeedback) {
            window.tactileFeedback.sounds.processing();
        }
        
        // Simulate processing
        setTimeout(() => {
            submitBtn.innerHTML = '<span class="cta-icon">✅</span> Success! Check Your Email';
            submitBtn.style.background = 'var(--apex-success)';
            
            // Play success sound
            if (window.tactileFeedback) {
                window.tactileFeedback.sounds.success();
            }
            
            // Add confetti effect
            this.addConfettiEffect(modal);
            
            setTimeout(() => {
                closeTrial();
                
                // Show download notification
                this.showDownloadNotification();
            }, 2000);
        }, 1500);
    });
    
    // Add confetti effect
    this.addConfettiEffect = (container) => {
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-piece';
            confetti.style.cssText = `
                position: absolute;
                width: 10px;
                height: 10px;
                background: ${['var(--apex-primary)', 'var(--apex-secondary)', 'var(--apex-success)', 'var(--apex-warning)'][Math.floor(Math.random() * 4)]};
                top: 50%;
                left: 50%;
                pointer-events: none;
                animation: confetti-fall ${2 + Math.random() * 3}s ease-out forwards;
                transform: translate(-50%, -50%) rotate(${Math.random() * 360}deg);
            `;
            
            container.appendChild(confetti);
            
            setTimeout(() => {
                if (confetti.parentNode) {
                    confetti.parentNode.removeChild(confetti);
                }
            }, 5000);
        }
        
        // Add confetti animation if not exists
        if (!document.querySelector('#confetti-styles')) {
            const style = document.createElement('style');
            style.id = 'confetti-styles';
            style.textContent = `
                @keyframes confetti-fall {
                    0% {
                        transform: translate(-50%, -50%) rotate(0deg);
                        opacity: 1;
                    }
                    100% {
                        transform: translate(${-200 + Math.random() * 400}px, 300px) rotate(720deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    };
    
    // Show download notification
    this.showDownloadNotification = () => {
        const notification = document.createElement('div');
        notification.className = 'download-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">🚀</div>
                <div class="notification-text">
                    <strong>APEX is downloading!</strong><br>
                    <small>Trial license sent to your email</small>
                </div>
                <button onclick="this.parentNode.parentNode.remove()" class="notification-close">×</button>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--apex-gray-dark);
            border: 1px solid var(--apex-success);
            border-radius: var(--radius-xl);
            padding: var(--space-lg);
            box-shadow: var(--shadow-glow), 0 10px 30px rgba(0, 0, 0, 0.3);
            z-index: 10001;
            animation: slideInRight 0.5s ease-out;
            max-width: 300px;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .notification-content {
                display: flex;
                align-items: center;
                gap: var(--space-md);
            }
            
            .notification-icon {
                font-size: var(--font-size-2xl);
            }
            
            .notification-text {
                flex: 1;
                color: var(--apex-white);
            }
            
            .notification-close {
                background: none;
                border: none;
                color: var(--apex-white-muted);
                font-size: var(--font-size-lg);
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
            }
            
            .notification-close:hover {
                color: var(--apex-primary);
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Play notification sound
        if (window.tactileFeedback) {
            window.tactileFeedback.sounds.notification();
        }
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideInRight 0.5s ease-out reverse';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 500);
            }
        }, 5000);
    };
}

function closeTrial() {
    const modal = document.querySelector('.trial-modal');
    if (modal) {
        modal.remove();
    }
}

function watchDemo() {
    // Scroll to terminal demo and highlight it
    const terminal = document.querySelector('.terminal-container');
    terminal.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Add highlight effect
    terminal.style.boxShadow = 'var(--shadow-glow-strong)';
    setTimeout(() => {
        terminal.style.boxShadow = 'var(--shadow-xl)';
    }, 3000);
}

function downloadDMG() {
    // Simulate download
    const btn = event.target.closest('.download-btn');
    btn.style.background = 'var(--apex-success)';
    btn.style.borderColor = 'var(--apex-success)';
    btn.querySelector('.download-title').textContent = '✅ Downloading...';
    
    setTimeout(() => {
        btn.querySelector('.download-title').textContent = '🎉 Download Complete!';
        btn.querySelector('.download-subtitle').textContent = 'Check your Downloads folder';
    }, 2000);
    
    // Reset after 5 seconds
    setTimeout(() => {
        btn.style.background = '';
        btn.style.borderColor = '';
        btn.querySelector('.download-title').textContent = '📦 Download for macOS';
        btn.querySelector('.download-subtitle').textContent = 'Native PyWebView • 45MB • Instant install';
    }, 5000);
}

function downloadElectron() {
    // Similar to DMG download
    const btn = event.target.closest('.download-btn');
    btn.style.background = 'var(--apex-success)';
    btn.style.borderColor = 'var(--apex-success)';
    btn.querySelector('.download-title').textContent = '✅ Downloading...';
    
    setTimeout(() => {
        btn.querySelector('.download-title').textContent = '🎉 Download Complete!';
        btn.querySelector('.download-subtitle').textContent = 'Check your Downloads folder';
    }, 2000);
    
    setTimeout(() => {
        btn.style.background = '';
        btn.style.borderColor = '';
        btn.querySelector('.download-title').textContent = '⚡ Download Electron Version';
        btn.querySelector('.download-subtitle').textContent = 'Cross-platform • 120MB • Full features';
    }, 5000);
}

// Particle System for Background
class ParticleSystem {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.particleCount = 50;
        
        this.init();
    }
    
    init() {
        this.setupCanvas();
        this.createParticles();
        this.animate();
        
        window.addEventListener('resize', () => this.handleResize());
    }
    
    setupCanvas() {
        this.canvas.style.position = 'absolute';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '-1';
        
        this.handleResize();
        
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
            heroSection.appendChild(this.canvas);
        }
    }
    
    handleResize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    createParticles() {
        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2
            });
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around edges
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;
            
            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(0, 217, 255, ${particle.opacity})`;
            this.ctx.fill();
        });
        
        requestAnimationFrame(() => this.animate());
    }
}

// Advanced Tactile Feedback System
class TactileFeedback {
    constructor() {
        this.audioContext = null;
        this.sounds = {};
        this.init();
    }
    
    init() {
        this.setupAudio();
        this.addButtonEffects();
        this.addHapticFeedback();
        this.addMouseTracking();
        this.addCardInteractions();
    }
    
    setupAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.createSounds();
        } catch (e) {
            console.log('Audio context not available');
        }
    }
    
    createSounds() {
        // Create sophisticated UI sound effects with musical harmony
        this.sounds.hover = () => {
            // Gentle major third interval
            this.playTone(800, 0.08, 0.04);
            setTimeout(() => this.playTone(1000, 0.08, 0.03), 50);
        };
        
        this.sounds.click = () => {
            // Satisfying click with harmonic
            this.playTone(1200, 0.12, 0.08);
            setTimeout(() => this.playTone(1500, 0.08, 0.04), 30);
            if (navigator.vibrate) navigator.vibrate([25]);
        };
        
        this.sounds.success = () => {
            // Triumphant major chord progression: C-Am-F-G-C
            const progression = [
                [523.25, 659.25, 783.99], // C major
                [440, 523.25, 659.25],    // A minor
                [349.23, 440, 523.25],    // F major
                [392, 493.88, 587.33],    // G major
                [523.25, 659.25, 783.99, 1046.50] // C major octave
            ];
            
            progression.forEach((chord, i) => {
                setTimeout(() => {
                    this.playChord(chord, 0.4, 0.1);
                }, i * 300);
            });
            
            // Add twinkling sparkle arpeggios
            setTimeout(() => {
                const sparkleNotes = [1046.50, 1174.66, 1318.51, 1567.98, 2093.00]; // C-D-E-G-C
                sparkleNotes.forEach((freq, i) => {
                    setTimeout(() => {
                        this.playTone(freq, 0.2, 0.06, 'sine');
                    }, i * 80);
                });
            }, 1000);
            
            if (navigator.vibrate) navigator.vibrate([100, 30, 100, 30, 100, 30, 200]);
        };
        
        this.sounds.processing = () => {
            // Subtle pulse with gentle modulation
            this.playModulatedTone(600, 0.3, 0.05, 'triangle', 2);
            setTimeout(() => {
                this.playModulatedTone(750, 0.3, 0.04, 'sine', 3);
            }, 150);
        };
        
        this.sounds.notification = () => {
            // Gentle bell-like chime with decay
            const bellChord = [880, 1108, 1320]; // Perfect fifth + major third
            this.playChord(bellChord, 0.6, 0.08);
            
            // Add a gentle echo
            setTimeout(() => {
                this.playChord(bellChord, 0.4, 0.04);
            }, 400);
            
            if (navigator.vibrate) navigator.vibrate([60]);
        };
        
        this.sounds.ambient = () => {
            // Subtle ambient chord for background
            const ambientChord = [220, 330, 440]; // Low, warm chord
            this.playChord(ambientChord, 2.0, 0.02);
        };
        
        this.sounds.terminal = () => {
            // Retro terminal beep with character
            this.playTone(800, 0.06, 0.08, 'square');
            setTimeout(() => this.playTone(1000, 0.04, 0.05, 'square'), 60);
        };
        
        this.sounds.deploy = () => {
            // Rising deployment fanfare
            const deploySequence = [440, 523.25, 659.25, 783.99, 880]; // A-C-E-G-A
            deploySequence.forEach((freq, i) => {
                setTimeout(() => {
                    this.playTone(freq, 0.15, 0.06);
                }, i * 120);
            });
        };
        
        this.sounds.error = () => {
            // Dissonant but not harsh error sound
            this.playTone(300, 0.2, 0.06, 'sawtooth');
            setTimeout(() => this.playTone(280, 0.15, 0.04, 'sawtooth'), 100);
            if (navigator.vibrate) navigator.vibrate([150, 50, 150]);
        };
    }
    
    playTone(frequency, duration, volume = 0.1, type = 'sine') {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
        oscillator.type = type;
        
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(volume, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }
    
    playChord(frequencies, duration, volume = 0.1) {
        frequencies.forEach((freq, i) => {
            setTimeout(() => this.playTone(freq, duration, volume / frequencies.length), i * 50);
        });
    }
    
    playModulatedTone(frequency, duration, volume = 0.1, type = 'sine', modulationRate = 2) {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        const modulatorOsc = this.audioContext.createOscillator();
        const modulatorGain = this.audioContext.createGain();
        
        // Set up modulation
        modulatorOsc.frequency.setValueAtTime(modulationRate, this.audioContext.currentTime);
        modulatorGain.gain.setValueAtTime(10, this.audioContext.currentTime); // Modulation depth
        
        // Connect modulation chain
        modulatorOsc.connect(modulatorGain);
        modulatorGain.connect(oscillator.frequency);
        
        // Connect main audio chain
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
        oscillator.type = type;
        
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(volume, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        modulatorOsc.start(this.audioContext.currentTime);
        
        oscillator.stop(this.audioContext.currentTime + duration);
        modulatorOsc.stop(this.audioContext.currentTime + duration);
    }
    
    addButtonEffects() {
        // Add tactile feedback to all buttons
        document.querySelectorAll('button, .cta-primary, .cta-secondary, .download-btn').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                this.sounds.hover();
                this.addRipple(btn);
            });
            
            btn.addEventListener('mousedown', () => {
                this.sounds.click();
                this.addPressEffect(btn);
            });
            
            btn.addEventListener('mouseup', () => {
                this.removePressEffect(btn);
            });
            
            btn.addEventListener('mouseleave', () => {
                this.removePressEffect(btn);
            });
        });
    }
    
    addRipple(element) {
        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';
        
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (rect.width / 2 - size / 2) + 'px';
        ripple.style.top = (rect.height / 2 - size / 2) + 'px';
        
        element.style.position = 'relative';
        element.appendChild(ripple);
        
        // Add ripple styles
        if (!document.querySelector('#ripple-styles')) {
            const style = document.createElement('style');
            style.id = 'ripple-styles';
            style.textContent = `
                .ripple-effect {
                    position: absolute;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.2);
                    pointer-events: none;
                    transform: scale(0);
                    animation: ripple-animation 0.6s ease-out;
                    z-index: 1;
                }
                
                @keyframes ripple-animation {
                    to {
                        transform: scale(2);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }
    
    addPressEffect(element) {
        element.classList.add('pressed');
        
        if (!document.querySelector('#press-styles')) {
            const style = document.createElement('style');
            style.id = 'press-styles';
            style.textContent = `
                .pressed {
                    transform: scale(0.98) !important;
                    transition: transform 0.1s ease !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    removePressEffect(element) {
        element.classList.remove('pressed');
    }
    
    addHapticFeedback() {
        // Add haptic feedback for supported devices
        document.addEventListener('click', () => {
            if (navigator.vibrate) {
                navigator.vibrate([5]); // Subtle vibration
            }
        });
    }
    
    addMouseTracking() {
        // Add subtle mouse tracking effects
        document.addEventListener('mousemove', (e) => {
            const cards = document.querySelectorAll('.feature-card, .testimonial-card');
            
            cards.forEach(card => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 20;
                const rotateY = (centerX - x) / 20;
                
                if (x >= 0 && x <= rect.width && y >= 0 && y <= rect.height) {
                    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
                } else {
                    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
                }
            });
        });
    }
    
    addCardInteractions() {
        // Add breathing animation to cards on hover
        document.querySelectorAll('.feature-card, .testimonial-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.animation = 'breathe 2s ease-in-out infinite';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.animation = '';
            });
        });
        
        // Add breathing animation keyframes
        if (!document.querySelector('#breathe-styles')) {
            const style = document.createElement('style');
            style.id = 'breathe-styles';
            style.textContent = `
                @keyframes breathe {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Advanced Loading States
class LoadingStates {
    constructor() {
        this.init();
    }
    
    init() {
        this.addLoadingEffects();
    }
    
    addLoadingEffects() {
        // Add skeleton loading for sections
        const sections = document.querySelectorAll('.features-section, .social-proof-section');
        
        sections.forEach(section => {
            this.addSkeletonLoading(section);
        });
    }
    
    addSkeletonLoading(section) {
        // Add shimmer effect while content loads
        section.style.position = 'relative';
        
        const shimmer = document.createElement('div');
        shimmer.className = 'shimmer-overlay';
        
        if (!document.querySelector('#shimmer-styles')) {
            const style = document.createElement('style');
            style.id = 'shimmer-styles';
            style.textContent = `
                .shimmer-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(
                        90deg,
                        transparent,
                        rgba(0, 217, 255, 0.1),
                        transparent
                    );
                    transform: translateX(-100%);
                    animation: shimmer 2s infinite;
                    pointer-events: none;
                    z-index: 1;
                }
                
                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
            `;
            document.head.appendChild(style);
        }
        
        section.appendChild(shimmer);
        
        // Remove shimmer after content is visible
        setTimeout(() => {
            if (shimmer.parentNode) {
                shimmer.style.opacity = '0';
                setTimeout(() => {
                    if (shimmer.parentNode) {
                        shimmer.parentNode.removeChild(shimmer);
                    }
                }, 500);
            }
        }, 3000);
    }
}

// Magnetic Cursor Effects
class MagneticCursor {
    constructor() {
        this.cursor = null;
        this.init();
    }
    
    init() {
        this.createCursor();
        this.addMagneticEffects();
    }
    
    createCursor() {
        this.cursor = document.createElement('div');
        this.cursor.className = 'magnetic-cursor';
        document.body.appendChild(this.cursor);
        
        const style = document.createElement('style');
        style.textContent = `
            .magnetic-cursor {
                position: fixed;
                width: 20px;
                height: 20px;
                background: var(--apex-primary);
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
                mix-blend-mode: difference;
                transition: all 0.1s ease;
                opacity: 0;
            }
            
            .magnetic-cursor.active {
                opacity: 1;
                transform: scale(1.5);
                background: var(--apex-accent);
            }
        `;
        document.head.appendChild(style);
        
        document.addEventListener('mousemove', (e) => {
            this.cursor.style.left = e.clientX - 10 + 'px';
            this.cursor.style.top = e.clientY - 10 + 'px';
        });
        
        document.addEventListener('mouseenter', () => {
            this.cursor.style.opacity = '1';
        });
        
        document.addEventListener('mouseleave', () => {
            this.cursor.style.opacity = '0';
        });
    }
    
    addMagneticEffects() {
        const magneticElements = document.querySelectorAll('.cta-primary, .cta-secondary, .feature-card, .testimonial-card');
        
        magneticElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                this.cursor.classList.add('active');
            });
            
            element.addEventListener('mouseleave', () => {
                this.cursor.classList.remove('active');
            });
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TerminalDemo();
    new StatsCounter();
    new TabSwitcher();
    new ScrollAnimations();
    new ParticleSystem();
    new TactileFeedback();
    new LoadingStates();
    new MagneticCursor();
    
    console.log('🚀 APEX Sales Demo initialized - Ready to convert some engineers!');
    console.log('🎯 Full tactile feedback system active!');
});

// Easter eggs and fun interactions
document.addEventListener('keydown', (e) => {
    // Konami code for APEX developers
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'KeyB', 'KeyA'];
    
    if (!window.konamiIndex) window.konamiIndex = 0;
    
    if (e.code === konamiCode[window.konamiIndex]) {
        window.konamiIndex++;
        if (window.konamiIndex === konamiCode.length) {
            // Easter egg for developers
            document.body.style.filter = 'hue-rotate(180deg)';
            alert('🎮 APEX Developer Mode Activated! (Refresh to return to normal)');
            window.konamiIndex = 0;
        }
    } else {
        window.konamiIndex = 0;
    }
});