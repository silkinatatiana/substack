document.addEventListener('DOMContentLoaded', function () {
    var container = document.querySelector('[data-image-sortable]');
    var orderInput = document.getElementById('id_image_order');
    var deletedInput = document.getElementById('id_deleted_image_ids');
    if (!container || !orderInput) {
        return;
    }

    var deletedIds = [];

    function syncOrder() {
        var ids = container.querySelectorAll('[data-image-id]');
        orderInput.value = Array.from(ids)
            .map(function (el) { return el.dataset.imageId; })
            .join(',');
    }

    function syncDeleted() {
        if (deletedInput) {
            deletedInput.value = deletedIds.join(',');
        }
    }

    var dragged = null;

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

        deletedIds.push(item.dataset.imageId);
        item.remove();
        syncDeleted();
        syncOrder();
    });

    container.closest('form').addEventListener('submit', function () {
        syncOrder();
        syncDeleted();
    });

    syncOrder();
});
