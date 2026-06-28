document.querySelectorAll('.file-upload').forEach(function (wrapper) {
    var input = wrapper.querySelector('input[type="file"]');
    var nameEl = wrapper.querySelector('.file-upload-name');
    if (!input || !nameEl) {
        return;
    }

    var defaultText = nameEl.dataset.default || 'Файл не выбран';

    input.addEventListener('change', function () {
        nameEl.textContent = input.files.length ? input.files[0].name : defaultText;
    });
});
