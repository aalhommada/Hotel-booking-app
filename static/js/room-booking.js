// static/js/room-booking.js
document.addEventListener('DOMContentLoaded', function() {
    const checkInInput = document.getElementById('check_in');
    const checkOutInput = document.getElementById('check_out');
    const submitButton = document.querySelector('button[type="submit"]');
    const availabilityMessage = document.getElementById('availability-message');

    if (checkInInput && checkOutInput) {
        // Get booked dates from data attribute
        const bookedDates = JSON.parse(checkInInput.dataset.bookedDates || '[]');
        
        // Disable booked dates
        function disableBookedDates(input) {
            const date = input.value;
            if (bookedDates.includes(date)) {
                input.value = '';
                alert('This date is not available');
            }
        }

        checkInInput.addEventListener('change', function() {
            // Set minimum check-out date to day after check-in
            if (this.value) {
                const nextDay = new Date(this.value);
                nextDay.setDate(nextDay.getDate() + 1);
                checkOutInput.min = nextDay.toISOString().split('T')[0];
                
                // Clear check-out if it's before new minimum
                if (checkOutInput.value && checkOutInput.value <= this.value) {
                    checkOutInput.value = '';
                }
            }
            disableBookedDates(this);
        });

        checkOutInput.addEventListener('change', function() {
            disableBookedDates(this);
        });
    }

    // HTMX event listeners
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt.id === 'availability-message') {
            const response = JSON.parse(evt.detail.xhr.response);
            submitButton.disabled = !response.available;
            
            availabilityMessage.className = response.available 
                ? 'p-4 bg-green-100 text-green-700 rounded-md'
                : 'p-4 bg-red-100 text-red-700 rounded-md';
            availabilityMessage.textContent = response.message;
        }
    });
});