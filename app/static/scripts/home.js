document.addEventListener('DOMContentLoaded', function () {
    const toggleTabButton = document.getElementById('toggleTab');
    const tab = document.getElementById('tab');

    toggleTabButton.addEventListener('click', function () {
        tab.classList.toggle('hidden');
    });
});

