document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-carousel]').forEach(initCarousel);
});

function initCarousel(root) {
    var track = root.querySelector('.post-carousel-track');
    var slides = root.querySelectorAll('.post-carousel-slide');
    var prevBtn = root.querySelector('.post-carousel-prev');
    var nextBtn = root.querySelector('.post-carousel-next');
    var dotsContainer = root.querySelector('.post-carousel-dots');
    var counterEl = root.querySelector('.post-carousel-counter');
    var viewport = root.querySelector('.post-carousel-viewport');

    if (!track || !slides.length) {
        return;
    }

    var currentIndex = 0;
    var touchStartX = 0;
    var touchDeltaX = 0;

    if (slides.length <= 1) {
        root.classList.add('is-single');
        return;
    }

    slides.forEach(function (_, index) {
        var dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'post-carousel-dot';
        dot.setAttribute('aria-label', 'Фото ' + (index + 1));
        dot.addEventListener('click', function () {
            goTo(index);
        });
        dotsContainer.appendChild(dot);
    });

    var dots = dotsContainer.querySelectorAll('.post-carousel-dot');

    function goTo(index) {
        if (index < 0) {
            index = 0;
        }
        if (index > slides.length - 1) {
            index = slides.length - 1;
        }

        currentIndex = index;
        track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';

        dots.forEach(function (dot, i) {
            dot.classList.toggle('is-active', i === currentIndex);
        });

        if (counterEl) {
            counterEl.textContent = (currentIndex + 1) + ' / ' + slides.length;
        }

        if (prevBtn) {
            prevBtn.disabled = currentIndex === 0;
        }
        if (nextBtn) {
            nextBtn.disabled = currentIndex === slides.length - 1;
        }
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            goTo(currentIndex - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            goTo(currentIndex + 1);
        });
    }

    if (viewport) {
        viewport.addEventListener('touchstart', function (e) {
            if (!e.touches.length) {
                return;
            }
            touchStartX = e.touches[0].clientX;
            touchDeltaX = 0;
        }, { passive: true });

        viewport.addEventListener('touchmove', function (e) {
            if (!e.touches.length) {
                return;
            }
            touchDeltaX = e.touches[0].clientX - touchStartX;
        }, { passive: true });

        viewport.addEventListener('touchend', function () {
            if (touchDeltaX < -50) {
                goTo(currentIndex + 1);
            } else if (touchDeltaX > 50) {
                goTo(currentIndex - 1);
            }
            touchStartX = 0;
            touchDeltaX = 0;
        });
    }

    root.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') {
            goTo(currentIndex - 1);
        } else if (e.key === 'ArrowRight') {
            goTo(currentIndex + 1);
        }
    });

    goTo(0);
}