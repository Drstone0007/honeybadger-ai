/**
 * HONEY BADGER KERNEL OS — Terminal User Interface
 * Glassmorphism Aesthetic + Boot Sequence
 */

const HoneyBadgerKernel = {
    version: '1.0.0',
    codename: 'TITAN',
    
    // Boot sequence messages
    bootSequence: [
        { text: 'Initializing Honey Badger Kernel...', delay: 100 },
        { text: 'Loading TITAN core modules', delay: 150, success: true },
        { text: 'Mounting /dev/neural', delay: 120, success: true },
        { text: 'Starting glassmorphism renderer', delay: 180, success: true },
        { text: 'Calibrating AI inference engine', delay: 200, success: true },
        { text: 'Establishing secure mesh network', delay: 160, success: true },
        { text: 'Loading neural pathway cache', delay: 140, success: true },
        { text: 'Initializing quantum-resistant TLS', delay: 190, success: true },
        { text: 'Mounting /opt/models', delay: 130, success: true },
        { text: 'Starting background workers', delay: 170, success: true },
        { text: 'Loading user preferences', delay: 110, success: true },
        { text: 'Kernel modules loaded', delay: 100, success: true },
        { text: 'System ready', delay: 50, success: true },
    ],
    
    // Initialize kernel
    init() {
        console.log(`[HB] Honey Badger Kernel v${this.version} (${this.codename})`);
        this.createKernelBadge();
        this.setupEventListeners();
    },
    
    // Create kernel version badge
    createKernelBadge() {
        const badge = document.createElement('div');
        badge.className = 'hb-kernel-badge';
        badge.innerHTML = `HB KERNEL v${this.version}`;
        document.body.appendChild(badge);
    },
    
    // Boot sequence animation
    async runBootSequence(container) {
        const bootLog = container.querySelector('.boot-log');
        if (!bootLog) return;
        
        for (const item of this.bootSequence) {
            await this.sleep(item.delay);
            
            const line = document.createElement('div');
            line.className = `boot-line ${item.success ? 'success' : ''}`;
            line.textContent = item.text;
            line.style.animationDelay = `${this.bootSequence.indexOf(item) * 0.1}s`;
            bootLog.appendChild(line);
        }
        
        // Fade out boot screen after completion
        await this.sleep(500);
        container.style.opacity = '0';
        container.style.transition = 'opacity 0.5s ease';
        await this.sleep(500);
        container.style.display = 'none';
    },
    
    // Setup event listeners
    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl+K: Command palette
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.showCommandPalette();
            }
        });
    },
    
    // Command palette
    showCommandPalette() {
        // TODO: Implement command palette
        console.log('[HB] Command palette triggered');
    },
    
    // Utility: sleep
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    // Create glassmorphism element
    createGlassElement(type = 'div', className = '') {
        const el = document.createElement(type);
        el.className = `hb-glass ${className}`;
        return el;
    },
    
    // Create terminal window
    createTerminal(title = 'TERMINAL') {
        const terminal = document.createElement('div');
        terminal.className = 'hb-terminal';
        terminal.innerHTML = `
            <div class="hb-terminal-header">
                <div class="hb-terminal-dots">
                    <span class="hb-terminal-dot"></span>
                    <span class="hb-terminal-dot active"></span>
                    <span class="hb-terminal-dot"></span>
                </div>
                <div class="hb-terminal-title">${title}</div>
            </div>
            <div class="hb-terminal-body"></div>
        `;
        return terminal;
    },
    
    // Typing effect
    async typeText(element, text, speed = 30) {
        element.textContent = '';
        for (const char of text) {
            element.textContent += char;
            await this.sleep(speed);
        }
    },
    
    // Create status indicator
    createStatusDot(status = 'online') {
        const dot = document.createElement('span');
        dot.className = 'status-dot';
        dot.style.background = status === 'online' ? 'var(--hb-accent)' : 'var(--hb-danger)';
        return dot;
    },
    
    // Format timestamp
    formatTime(date = new Date()) {
        return date.toLocaleTimeString('en-US', { 
            hour12: false, 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
    },
    
    // Get kernel uptime
    getUptime() {
        const start = window._hbStartTime || Date.now();
        const diff = Math.floor((Date.now() - start) / 1000);
        const hours = Math.floor(diff / 3600);
        const minutes = Math.floor((diff % 3600) / 60);
        const seconds = diff % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window._hbStartTime = Date.now();
        HoneyBadgerKernel.init();
    });
} else {
    window._hbStartTime = Date.now();
    HoneyBadgerKernel.init();
}

// Export for global access
window.HoneyBadgerKernel = HoneyBadgerKernel;
