document.addEventListener('submit', async function (event) {
    const form = event.target.closest('.post-like-form, .comment-like-form');
    if (!form || form.dataset.submitting === 'true') {
        return;
    }

    event.preventDefault();
    form.dataset.submitting = 'true';

    const button = form.querySelector('.post-like-button, .comment-like-button');
    const likeContainer = form.closest('.post-engagement-like, .comment-like');
    const count = likeContainer?.querySelector('.post-like-count, .comment-like-count');

    if (button) {
        button.disabled = true;
    }

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        if (!response.ok) {
            throw new Error(`Like request failed: ${response.status}`);
        }

        const result = await response.json();
        button?.classList.toggle('is-liked', result.is_liked);
        button?.setAttribute('aria-pressed', String(result.is_liked));
        button?.setAttribute('aria-label', result.is_liked ? 'Убрать лайк' : 'Поставить лайк');
        if (count) {
            count.textContent = result.likes_count;
        }
    } catch (error) {
        form.submit();
    } finally {
        delete form.dataset.submitting;
        if (button) {
            button.disabled = false;
        }
    }
});
