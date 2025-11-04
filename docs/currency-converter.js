// VeloCity Currency Converter - ZAR/USD Toggle
// Fetches current exchange rate and converts all currency values

class CurrencyConverter {
    constructor() {
        this.currentCurrency = localStorage.getItem('velocity-currency') || 'ZAR';
        this.exchangeRate = null;
        this.rarToUsdRate = 1; // Default fallback
        this.init();
    }

    async init() {
        await this.fetchExchangeRate();
        this.applyCurrencyPreference();
        this.setupToggleButtons();
    }

    async fetchExchangeRate() {
        try {
            // Try multiple free exchange rate APIs for reliability
            const response = await fetch('https://api.exchangerate-api.com/v4/latest/ZAR');
            const data = await response.json();

            if (data && data.rates && data.rates.USD) {
                this.rarToUsdRate = data.rates.USD; // ZAR to USD (direct conversion rate)
                console.log(`Exchange rate (ZAR/USD): 1 ZAR = ${this.rarToUsdRate.toFixed(4)} USD`);

                // Update rate display if element exists
                const rateDisplay = document.getElementById('exchange-rate-display');
                if (rateDisplay) {
                    rateDisplay.textContent = `1 ZAR = $${this.rarToUsdRate.toFixed(4)}`;
                }
            }
        } catch (error) {
            console.warn('Could not fetch exchange rate:', error);
            // Use fallback rate (approximately 0.052 ZAR = 1 USD)
            this.rarToUsdRate = 0.052;

            const rateDisplay = document.getElementById('exchange-rate-display');
            if (rateDisplay) {
                rateDisplay.innerHTML = `<span style="opacity: 0.7;">(Fallback rate: 1 ZAR ≈ $${this.rarToUsdRate.toFixed(4)})</span>`;
            }
        }
    }

    applyCurrencyPreference() {
        // Apply stored currency preference on page load
        const storedCurrency = localStorage.getItem('velocity-currency') || 'ZAR';
        this.currentCurrency = storedCurrency;

        // Update button states
        document.querySelectorAll('.currency-toggle-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.currency === storedCurrency) {
                btn.classList.add('active');
            }
        });

        // Convert all values to match preference
        this.convertAllValues();
    }

    setupToggleButtons() {
        const toggleButtons = document.querySelectorAll('.currency-toggle-btn');
        toggleButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const currency = e.target.dataset.currency;
                this.setCurrency(currency);
            });
        });
    }

    setCurrency(currency) {
        if (currency !== 'ZAR' && currency !== 'USD') return;

        this.currentCurrency = currency;
        localStorage.setItem('velocity-currency', currency);

        // Update button states
        document.querySelectorAll('.currency-toggle-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.currency === currency) {
                btn.classList.add('active');
            }
        });

        // Convert all currency values
        this.convertAllValues();
    }

    convertAllValues() {
        // Convert all elements with data-currency-zar attribute
        const currencyElements = document.querySelectorAll('[data-currency-zar]');

        currencyElements.forEach(element => {
            const zarValue = parseFloat(element.dataset.currencyZar);

            if (this.currentCurrency === 'USD') {
                const usdValue = zarValue * this.rarToUsdRate;
                element.textContent = this.formatCurrency(usdValue, 'USD');
                element.dataset.currencyDisplay = 'USD';
            } else {
                element.textContent = this.formatCurrency(zarValue, 'ZAR');
                element.dataset.currencyDisplay = 'ZAR';
            }
        });

        // Handle table cells with currency data
        const currencyTableCells = document.querySelectorAll('[data-currency-zar-table]');
        currencyTableCells.forEach(cell => {
            const zarValue = parseFloat(cell.dataset.currencyZarTable);

            if (this.currentCurrency === 'USD') {
                const usdValue = zarValue * this.rarToUsdRate;
                cell.textContent = this.formatCurrency(usdValue, 'USD');
            } else {
                cell.textContent = this.formatCurrency(zarValue, 'ZAR');
            }
        });

        // Update currency labels
        const labels = document.querySelectorAll('[data-currency-label]');
        labels.forEach(label => {
            if (this.currentCurrency === 'USD') {
                label.textContent = label.dataset.currencyLabel.replace(/R\s?/g, '$');
            } else {
                if (!label.dataset.currencyLabel.startsWith('R')) {
                    label.textContent = 'R' + label.dataset.currencyLabel.replace(/\$/g, '');
                } else {
                    label.textContent = label.dataset.currencyLabel;
                }
            }
        });
    }

    formatCurrency(value, currency) {
        if (currency === 'USD') {
            return '$' + this.formatNumber(value);
        } else {
            return 'R' + this.formatNumber(value);
        }
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        } else if (num >= 1) {
            return num.toFixed(2);
        } else {
            return num.toFixed(4);
        }
    }

    // Utility function to convert a single value
    convertValue(zarAmount) {
        if (this.currentCurrency === 'USD') {
            return zarAmount * this.rarToUsdRate;
        }
        return zarAmount;
    }

    getCurrentCurrency() {
        return this.currentCurrency;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.currencyConverter = new CurrencyConverter();
    });
} else {
    window.currencyConverter = new CurrencyConverter();
}
