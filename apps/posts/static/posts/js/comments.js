document.addEventListener('DOMContentLoaded', function () {

    async function sendAjax(form) {

        const response = await fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const contentType = response.headers.get('content-type') || '';

        if (!contentType.includes('application/json')) {
            throw new Error(
                'Сервер вернул не JSON. Проверь Django View.'
            );
        }

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || 'Ошибка выполнения запроса'
            );
        }

        return data;
    }

    function showError(form, message) {

        const errorDiv = form.querySelector('.ajax-error');

        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        } else {
            alert(message);
        }
    }

    document.addEventListener('submit', async function (e) {

        const form = e.target;

        if (!form.matches(
            '.ajax-form, .ajax-comment-create, .post-comments > .comment-form'
        )) {
            return;
        }

        e.preventDefault();

        const textarea = form.querySelector('textarea');
        const button = form.querySelector('button[type="submit"]');

        if (!textarea || !button) {
            return;
        }

        const newText = textarea.value.trim();

        if (!newText) {
            showError(
                form,
                'Комментарий не может быть пустым'
            );
            return;
        }

        if (button.disabled) {
            return;
        }

        const originalText = button.textContent;

        button.disabled = true;
        button.textContent = '...';

        const errorDiv = form.querySelector('.ajax-error');

        if (errorDiv) {
            errorDiv.style.display = 'none';
        }

        try {

            const data = await sendAjax(form);

            if (!data.html) {
                throw new Error(
                    'Сервер не вернул HTML нового комментария'
                );
            }

            const template = document.createElement('template');

            template.innerHTML = data.html.trim();

            const newComment = template.content.firstElementChild;

            if (!newComment || !newComment.matches('li')) {
                throw new Error(
                    'Получен некорректный HTML комментария'
                );
            }

            if (data.parent_id) {

                const parent = document.getElementById(
                    'comment-' + data.parent_id
                );

                if (!parent) {
                    throw new Error(
                        'Родительский комментарий не найден'
                    );
                }

                const parentBody = parent.querySelector(
                    ':scope > .comment-body'
                );

                if (!parentBody) {
                    throw new Error(
                        'Контейнер родительского комментария не найден'
                    );
                }

                let answersUl = parentBody.querySelector(
                    ':scope > .comment-answers'
                );

                if (!answersUl) {

                    answersUl = document.createElement('ul');

                    answersUl.className = 'comment-answers';

                    parentBody.appendChild(answersUl);
                }

                answersUl.appendChild(newComment);

            } else {

                const section = document.querySelector('#comments');

                if (!section) {
                    throw new Error(
                        'Секция комментариев не найдена'
                    );
                }

                let commentList = section.querySelector(
                    '.comment-list'
                );

                if (!commentList) {

                    commentList = document.createElement('ul');

                    commentList.className = 'comment-list';

                    section.appendChild(commentList);
                }

                commentList.appendChild(newComment);

                const empty = section.querySelector('.comment-empty');

                if (empty) {
                    empty.remove();
                }
            }

            textarea.value = '';

            const details = form.closest('details');

            if (details) {
                details.open = false;
            }

        } catch (error) {

            console.error(
                'Ошибка создания комментария:',
                error
            );

            showError(
                form,
                error.message || 'Не удалось создать комментарий'
            );

        } finally {

            button.disabled = false;
            button.textContent = originalText;

        }

    });

    document.addEventListener('submit', async function (e) {

        const form = e.target;

        if (!form.matches('.comment-delete-form')) {
            return;
        }

        e.preventDefault();

        const confirmMessage =
            form.getAttribute('data-confirm-msg') ||
            'Удалить комментарий?';

        if (!confirm(confirmMessage)) {
            return;
        }

        const button = form.querySelector(
            'button[type="submit"]'
        );

        if (button && button.disabled) {
            return;
        }

        if (button) {
            button.disabled = true;
        }

        try {

            const data = await sendAjax(form);

            const commentEl = document.getElementById(
                'comment-' + data.deleted_id
            );

            if (commentEl) {

                commentEl.remove();

            }

        } catch (error) {

            console.error(
                'Ошибка удаления комментария:',
                error
            );

            alert(
                error.message ||
                'Ошибка при удалении комментария'
            );

        } finally {

            if (button) {
                button.disabled = false;
            }

        }

    });

    document.addEventListener('submit', async function (e) {

        const form = e.target;

        if (!form.matches('.comment-edit form')) {
            return;
        }

        e.preventDefault();

        const textarea = form.querySelector('textarea');

        const button = form.querySelector(
            'button[type="submit"]'
        );

        if (!textarea || !button) {
            return;
        }

        const newText = textarea.value.trim();

        if (!newText) {
            alert('Комментарий не может быть пустым');
            return;
        }

        if (button.disabled) {
            return;
        }

        const originalText = button.textContent;

        button.disabled = true;
        button.textContent = '...';

        try {

            const data = await sendAjax(form);

            const commentEl = document.getElementById(
                'comment-' + data.comment_id
            );

            if (commentEl) {

                const textP = commentEl.querySelector(
                    ':scope > .comment-body > .comment-text'
                );

                if (textP) {

                    textP.textContent = data.new_text;

                }
            }

            const details = form.closest('details');

            if (details) {
                details.open = false;
            }

        } catch (error) {

            console.error(
                'Ошибка редактирования комментария:',
                error
            );

            alert(
                error.message ||
                'Ошибка при сохранении комментария'
            );

        } finally {

            button.disabled = false;
            button.textContent = originalText;

        }

    });

});
