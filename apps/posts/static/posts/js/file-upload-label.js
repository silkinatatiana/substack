document.querySelectorAll('.file-upload').forEach(function (wrapper) {
    var input = wrapper.querySelector('input[type="file"]');
    var nameEl = wrapper.querySelector('.file-upload-name');
    if (!input || !nameEl) {
        return;
    }

    var defaultText = nameEl.dataset.default || 'Файл не выбран';

    input.addEventListener('change', function () {
        if (!input.files.length) {
            nameEl.textContent = defaultText;
            return;
        }
        if (input.files.length === 1) {
            nameEl.textContent = input.files[0].name;
            return;
        }
        nameEl.textContent = input.files.length + ' файлов выбрано';
    });
});
