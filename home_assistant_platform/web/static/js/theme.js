/**
 * Theme management (dark/light mode)
 */

class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }
    
    init() {
        this.applyTheme(this.theme);
        this.createToggle();
    }
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.theme = theme;
    }
    
    toggle() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        return newTheme;
    }
    
    createToggle() {
        // Add theme toggle to navbar if it doesn't exist
        const navbar = document.querySelector('.nav-menu');
        if (navbar && !document.getElementById('theme-toggle')) {
            const toggle = document.createElement('li');
            toggle.id = 'theme-toggle';
            toggle.innerHTML = `
                <button onclick="themeManager.toggle()" style="background: none; border: none; color: inherit; cursor: pointer; font-size: 1.2rem;">
                    ${this.theme === 'dark' ? '☀️' : '🌙'}
                </button>
            `;
            navbar.appendChild(toggle);
        }
    }
}

// Global theme manager
const themeManager = new ThemeManager();

