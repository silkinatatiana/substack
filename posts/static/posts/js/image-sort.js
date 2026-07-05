document.addEventListener('DOMContentLoaded', function () {
    var container = document.querySelector('[data-image-sortable]');
    var orderInput = document.getElementById('id_image_order');
    if (!container || !orderInput) return;

    function syncOrder() {
        var ids = container.querySelectorAll('[data-image-id]');
        orderInput.value = Array.from(ids)
            .map(function (el) { return el.dataset.imageId; })
            .join(',');
    }

    var dragged = null;

    container.addEventListener('dragstart', function (e) {
        dragged = e.target.closest('[data-image-id]');
    });

    container.addEventListener('dragover', function (e) {
        e.preventDefault();
        var target = e.target.closest('[data-image-id]');
        if (!dragged || !target || dragged === target) return;

        var rect = target.getBoundingClientRect();
        var after = e.clientX > rect.left + rect.width / 2;
        container.insertBefore(dragged, after ? target.nextSibling : target);
    });

    container.addEventListener('drop', function () {
        syncOrder();
        dragged = null;
    });

    container.closest('form').addEventListener('submit', function () {
        syncOrder();
    });

    syncOrder();
});