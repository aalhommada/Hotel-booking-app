document.addEventListener('DOMContentLoaded', function() {
    const { booked_dates, room_pk, check_availability_url } = window.ROOM_DATA;
    const submitButton = document.getElementById('booking-submit');

    // Initialize Flatpickr for check-in
    const checkInPicker = flatpickr("#check_in", {
        dateFormat: "Y-m-d",
        minDate: "today",
        disable: booked_dates,
        onChange: function(selectedDates, dateStr) {
            if (selectedDates[0]) {
                // Set minimum date for checkout to the day after check-in
                const nextDay = new Date(selectedDates[0]);
                nextDay.setDate(nextDay.getDate() + 1);
                checkOutPicker.set('minDate', nextDay);

                // Clear checkout if it's before the new check-in date
                if (checkOutPicker.selectedDates[0] &&
                    checkOutPicker.selectedDates[0] <= selectedDates[0]) {
                    checkOutPicker.clear();
                }
                checkAvailability();
            }
        }
    });

    // Initialize Flatpickr for check-out
    const checkOutPicker = flatpickr("#check_out", {
        dateFormat: "Y-m-d",
        minDate: "today",
        disable: booked_dates,
        onChange: function(selectedDates) {
            if (selectedDates[0]) {
                checkAvailability();
            }
        }
    });

    // Function to check availability
    function checkAvailability() {
        const checkIn = document.getElementById('check_in').value;
        const checkOut = document.getElementById('check_out').value;
        const messageDiv = document.getElementById('availability-message');

        if (checkIn && checkOut) {
            fetch(`${check_availability_url}?check_in=${checkIn}&check_out=${checkOut}`)
                .then(response => response.json())
                .then(data => {
                    messageDiv.classList.remove('hidden');
                    messageDiv.className = data.available
                        ? 'p-4 mb-4 bg-green-100 text-green-700 rounded-md'
                        : 'p-4 mb-4 bg-red-100 text-red-700 rounded-md';
                    messageDiv.textContent = data.message;
                    submitButton.disabled = !data.available;
                });
        } else {
            submitButton.disabled = true;
            messageDiv.classList.add('hidden');
        }
    }

    // Prevent form submission if dates are invalid
    document.getElementById('booking-form').addEventListener('submit', function(e) {
        if (!checkInPicker.selectedDates[0] || !checkOutPicker.selectedDates[0]) {
            e.preventDefault();
            alert('Please select both check-in and check-out dates.');
            return;
        }

        if (checkOutPicker.selectedDates[0] <= checkInPicker.selectedDates[0]) {
            e.preventDefault();
            alert('Check-out date must be after check-in date.');
            return;
        }
    });
});
