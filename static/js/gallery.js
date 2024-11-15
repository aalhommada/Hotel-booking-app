document.addEventListener('DOMContentLoaded', function() {
    const mainImage = document.getElementById('main-image');
    const thumbnails = document.querySelectorAll('.gallery-thumbnail');

    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            // Update main image
            mainImage.src = this.getAttribute('data-full-image');
            // Update active state
            thumbnails.forEach(t => t.classList.remove('ring-2', 'ring-blue-500'));
            this.classList.add('ring-2', 'ring-blue-500');
        });
    });
});

// Add date validation
const checkInDate = document.getElementById('check-in-date');
const checkOutDate = document.getElementById('check-out-date');

if (checkInDate && checkOutDate) {
    checkInDate.addEventListener('change', function() {
        checkOutDate.min = this.value;
    });
}
