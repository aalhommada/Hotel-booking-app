document.addEventListener('DOMContentLoaded', function() {
    // Function to calculate total price
    function calculateTotalPrice() {
        const checkIn = document.getElementById('id_check_in').value;
        const checkOut = document.getElementById('id_check_out').value;
        const roomSelect = document.getElementById('id_room');

        if (checkIn && checkOut && roomSelect) {
            const start = new Date(checkIn);
            const end = new Date(checkOut);
            const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));

            // Get room price from data attribute
            const roomPrice = parseFloat(roomSelect.selectedOptions[0].getAttribute('data-price') || 0);

            if (days > 0 && roomPrice > 0) {
                const totalPrice = days * roomPrice;
                document.getElementById('id_total_price').value = totalPrice.toFixed(2);
            }
        }
    }

    // Add event listeners to relevant fields
    const checkInField = document.getElementById('id_check_in');
    const checkOutField = document.getElementById('id_check_out');
    const roomField = document.getElementById('id_room');

    if (checkInField && checkOutField && roomField) {
        checkInField.addEventListener('change', calculateTotalPrice);
        checkOutField.addEventListener('change', calculateTotalPrice);
        roomField.addEventListener('change', calculateTotalPrice);
    }

    // Disable past dates in date fields
    const today = new Date().toISOString().split('T')[0];
    if (checkInField) {
        checkInField.setAttribute('min', today);
    }
    if (checkOutField) {
        checkOutField.setAttribute('min', today);
    }
});
