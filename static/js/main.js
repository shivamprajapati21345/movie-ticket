// Main JavaScript file for Shivam Booking

document.addEventListener('DOMContentLoaded', function () {
    console.log('Shivam Booking website loaded successfully');

    // Check for any messages in sessionStorage
    const message = sessionStorage.getItem('message');
    if (message) {
        showNotification(message, 'success');
        sessionStorage.removeItem('message');
    }
});

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Format currency
function formatCurrency(amount) {
    return '₹' + amount.toFixed(2);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-IN', options);
}

// Validate email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate password strength
function validatePasswordStrength(password) {
    if (password.length < 6) {
        return { strength: 'weak', message: 'Password must be at least 6 characters' };
    }
    if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
        return { strength: 'medium', message: 'Password should contain uppercase, lowercase, and numbers' };
    }
    return { strength: 'strong', message: 'Password is strong' };
}

// Search movies
function searchMovies(query) {
    const movieCards = document.querySelectorAll('.movie-card');
    movieCards.forEach(card => {
        const title = card.querySelector('h3').textContent.toLowerCase();
        if (title.includes(query.toLowerCase())) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Filter movies by genre
function filterByGenre(genre) {
    const movieCards = document.querySelectorAll('.movie-card');
    movieCards.forEach(card => {
        const movieGenre = card.querySelector('.genre').textContent.toLowerCase();
        if (genre === '' || movieGenre.includes(genre.toLowerCase())) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Calculate total price
function calculateTotal(pricePerSeat, numberOfSeats) {
    return pricePerSeat * numberOfSeats;
}

// Toggle seat selection
function toggleSeatSelection(seatElement) {
    if (seatElement.classList.contains('booked')) {
        return false;
    }
    seatElement.classList.toggle('selected');
    return true;
}

// Get selected seats
function getSelectedSeats() {
    const selectedSeats = [];
    document.querySelectorAll('.seat.selected').forEach(seat => {
        selectedSeats.push(seat.textContent);
    });
    return selectedSeats;
}

// Print ticket
function printTicket(bookingId) {
    window.print();
}

// Download ticket as PDF (placeholder function)
function downloadTicketPDF(bookingId) {
    alert('Download functionality would be implemented here');
    // In real implementation, this would generate and download a PDF
}

// Cancel booking
function cancelBooking(bookingId) {
    if (confirm('Are you sure you want to cancel this booking? You will receive a refund.')) {
        // Make API call to cancel booking
        fetch(`/api/cancel-booking/${bookingId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Booking cancelled successfully', 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showNotification('Failed to cancel booking', 'error');
                }
            });
    }
}

// Initialize tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function () {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
        });
    });
}

// Smooth scroll to element
function smoothScroll(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Local storage utilities
const Storage = {
    set: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
    get: (key) => JSON.parse(localStorage.getItem(key)),
    remove: (key) => localStorage.removeItem(key),
    clear: () => localStorage.clear()
};

// Session storage utilities
const SessionStorage = {
    set: (key, value) => sessionStorage.setItem(key, JSON.stringify(value)),
    get: (key) => JSON.parse(sessionStorage.getItem(key)),
    remove: (key) => sessionStorage.removeItem(key),
    clear: () => sessionStorage.clear()
};

// API helpers
const API = {
    get: async (url) => {
        const response = await fetch(url);
        return response.json();
    },
    post: async (url, data) => {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return response.json();
    }
};

console.log('Shivam Booking JavaScript utilities loaded');
