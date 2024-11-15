// static/js/booking.js
document.addEventListener('DOMContentLoaded', function() {
    const checkInInput = document.getElementById('check_in');
    const checkOutInput = document.getElementById('check_out');
    const submitButton = document.getElementById('booking-submit');
    const bookedDates = window.bookedDates || [];

    // Function to disable dates in the datepicker
    function disableBookedDates() {
        const inputs = [checkInInput, checkOutInput];
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                const selectedDate = this.value;
                if (bookedDates.includes(selectedDate)) {
                    this.value = '';
                    alert('This date is not available');
                }
            });
        });
    }

    // Function to update checkout min date
    checkInInput.addEventListener('change', function() {
        if (this.value) {
            const nextDay = new Date(this.value);
            nextDay.setDate(nextDay.getDate() + 1);
            checkOutInput.min = nextDay.toISOString().split('T')[0];
            if (checkOutInput.value && new Date(checkOutInput.value) <= new Date(this.value)) {
                checkOutInput.value = '';
            }
        }
    });

    // Handle availability check response
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt.id === 'availability-message') {
            const response = JSON.parse(evt.detail.xhr.response);
            const messageDiv = document.getElementById('availability-message');

            messageDiv.classList.remove('hidden');
            messageDiv.className = response.available
                ? 'p-4 mb-4 bg-green-100 text-green-700 rounded-md'
                : 'p-4 mb-4 bg-red-100 text-red-700 rounded-md';
            messageDiv.textContent = response.message;

            submitButton.disabled = !response.available;
        }
    });

    disableBookedDates();
});
