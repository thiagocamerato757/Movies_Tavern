document.addEventListener('DOMContentLoaded', function() {
    var btnAvaliar = document.getElementById('btn-avaliar');
    var avaliacao = document.querySelector('.avaliacao');
    var submitButton = document.getElementById('submit-rating');
    var stars = document.querySelectorAll('.star-icon');

    btnAvaliar.addEventListener('click', function() {
        if (btnAvaliar.textContent === 'Excluir') {
            rating = 0;
            paintStars(rating);
            submitButton.style.display = 'none';
            avaliacao.classList.remove('avaliacao-enviada');
            btnAvaliar.textContent = 'Avaliar';
            avaliacao.classList.add('desabilitada');
        }
        else{
            avaliacao.classList.remove('desabilitada');
            stars.forEach(star => {
                star.style.pointerEvents = 'auto';
            });
        }
        
    });

    stars.forEach(star => {
        star.addEventListener('click', function() {
            if (!avaliacao.classList.contains('avaliacao-enviada')) {
                rating = parseInt(star.getAttribute('data-avaliacao'));
                paintStars(rating);
                submitButton.style.display = 'block';
            }
        });
    });

    submitButton.addEventListener('click', function() {
        var activeStars = document.querySelectorAll('.star-icon.ativo');
        if (activeStars.length > 0) {
            avaliacao.classList.add('avaliacao-enviada');
            submitButton.style.display = 'none';
            btnAvaliar.textContent = 'Excluir';
            stars.forEach(star => {
                star.style.pointerEvents = 'none';
            });
        }
    });

    function paintStars(rating) {
        stars.forEach((s, index) => {
            if (index < rating) {
                s.classList.add('ativo');
            } else {
                s.classList.remove('ativo');
            }
        });
    }
});
