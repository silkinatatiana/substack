document.addEventListener('DOMContentLoaded', function () {
    var container = document.querySelector('[data-image-sortable]');
    if (!container) {
        return;
    }

    var form = container.closest('form');
    var orderInput = document.getElementById('id_image_order');
    var deletedInput = document.getElementById('id_deleted_image_ids');
    var fileInput = form ? form.querySelector('.file-upload input[type="file"]') : null;
    var deletedIds = [];
    var pendingFiles = [];
    var newFileCounter = 0;
    var dragged = null;

    function isNewItem(id) {
        return id.indexOf('new-') === 0;
    }

    function syncFileInput() {
        if (!fileInput || typeof DataTransfer === 'undefined') {
            return;
        }

        var dt = new DataTransfer();
        container.querySelectorAll('[data-image-id]').forEach(function (item) {
            var id = item.dataset.imageId;
            if (!isNewItem(id)) {
                return;
            }
            var entry = pendingFiles.find(function (pending) {
                return pending.id === id;
            });
            if (entry) {
                dt.items.add(entry.file);
            }
        });
        fileInput.files = dt.files;
    }

    function syncOrder() {
        if (!orderInput) {
            syncFileInput();
            return;
        }

        var newIndex = 0;
        var tokens = [];

        container.querySelectorAll('[data-image-id]').forEach(function (item) {
            var id = item.dataset.imageId;
            if (isNewItem(id)) {
                tokens.push('new:' + newIndex);
                newIndex += 1;
            } else {
                tokens.push(id);
            }
        });

        orderInput.value = tokens.join(',');
        syncFileInput();
    }

    function syncDeleted() {
        if (deletedInput) {
            deletedInput.value = deletedIds.join(',');
        }
    }

    function createPreviewItem(file) {
        var id = 'new-' + (newFileCounter += 1);
        pendingFiles.push({ id: id, file: file });

        var item = document.createElement('div');
        item.className = 'post-image-sort-item';
        item.dataset.imageId = id;
        item.draggable = true;

        var img = document.createElement('img');
        img.alt = file.name;

        var removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'post-image-sort-remove';
        removeBtn.dataset.removeImage = '';
        removeBtn.setAttribute('aria-label', 'Удалить изображение');
        removeBtn.textContent = '×';

        var handle = document.createElement('span');
        handle.className = 'post-image-sort-handle';
        handle.setAttribute('aria-hidden', 'true');
        handle.textContent = '⋮⋮';

        item.appendChild(img);
        item.appendChild(removeBtn);
        item.appendChild(handle);
        container.appendChild(item);

        var reader = new FileReader();
        reader.onload = function (event) {
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);

        syncOrder();
    }

    if (fileInput) {
        fileInput.addEventListener('change', function () {
            Array.from(fileInput.files).forEach(function (file) {
                if (file.type.indexOf('image/') === 0) {
                    createPreviewItem(file);
                }
            });
            fileInput.value = '';
        });
    }

    container.addEventListener('dragstart', function (e) {
        if (e.target.closest('[data-remove-image]')) {
            e.preventDefault();
            return;
        }
        dragged = e.target.closest('[data-image-id]');
    });

    container.addEventListener('dragover', function (e) {
        e.preventDefault();
        var target = e.target.closest('[data-image-id]');
        if (!dragged || !target || dragged === target) {
            return;
        }

        var rect = target.getBoundingClientRect();
        var after = e.clientX > rect.left + rect.width / 2;
        container.insertBefore(dragged, after ? target.nextSibling : target);
    });

    container.addEventListener('drop', function () {
        syncOrder();
        dragged = null;
    });

    container.addEventListener('click', function (e) {
        var removeBtn = e.target.closest('[data-remove-image]');
        if (!removeBtn) {
            return;
        }

        var item = removeBtn.closest('[data-image-id]');
        if (!item) {
            return;
        }

        var id = item.dataset.imageId;
        if (isNewItem(id)) {
            pendingFiles = pendingFiles.filter(function (pending) {
                return pending.id !== id;
            });
        } else {
            deletedIds.push(id);
            syncDeleted();
        }

        item.remove();
        syncOrder();
    });

    if (form) {
        form.addEventListener('submit', function () {
            syncOrder();
            syncDeleted();
        });
    }

    syncOrder();
});
