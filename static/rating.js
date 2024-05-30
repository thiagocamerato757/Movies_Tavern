var stars = document.querySelectorAll('.star-icon');
var submitButton = document.getElementById('submit-rating');

document.addEventListener('click', function(e) {
    var classStar = e.target.classList;
    if (!classStar.contains('ativo')) {
        stars.forEach(function(star) {
            star.classList.remove('ativo');
        });
        classStar.add('ativo');
        var rating = e.target.getAttribute('data-avaliacao');
        console.log(rating);
        submitButton.style.display = 'block';
    }
});

submitButton.addEventListener('click', function() {
    var activeStar = document.querySelector('.star-icon.ativo');
    var rating = activeStar.getAttribute('data-avaliacao');
    alert('Avaliação enviada: ' + rating);
    // Aqui você pode adicionar o código para enviar a avaliação para o servidor
});
