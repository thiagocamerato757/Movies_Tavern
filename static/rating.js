document.addEventListener('DOMContentLoaded', function() {
    var btnAvaliar = document.getElementById('btn-avaliar');
    var avaliacao = document.querySelector('.avaliacao');
    var submitButton = document.getElementById('submit-rating');
    var stars = document.querySelectorAll('.star-icon');
    var rating = 0;

    btnAvaliar.addEventListener('click', function() {
        if (btnAvaliar.textContent === 'Excluir') {
            rating = 0;
            paintStars(rating);
            submitButton.style.display = 'none';
            avaliacao.classList.remove('avaliacao-enviada');
            btnAvaliar.textContent = 'Rate';
            avaliacao.classList.add('desabilitada');
        } else {
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

        star.addEventListener('mouseover', function() {
            if (!avaliacao.classList.contains('avaliacao-enviada')) {
                var hoverRating = parseInt(star.getAttribute('data-avaliacao'));
                paintStars(hoverRating);
            }
        });

        star.addEventListener('mouseout', function() {
            if (!avaliacao.classList.contains('avaliacao-enviada')) {
                paintStars(rating);
            }
        });
    });

    submitButton.addEventListener('click', function() {
        if (rating > 0) {
            fetch('/submit_rating', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    movie_id: movie_id,
                    rating: rating
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert(data.message);
                    avaliacao.classList.add('avaliacao-enviada');
                    submitButton.style.display = 'none';
                    btnAvaliar.textContent = 'Excluir';
                    stars.forEach(star => {
                        star.style.pointerEvents = 'none';
                    });
                }
            })
            .catch((error) => {
                console.error('Error:', error);
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


document.addEventListener("DOMContentLoaded", function() {
    function showMoreCast() {
        const castList = document.getElementById('cast-list');
        const castDataDiv = document.getElementById('full-cast-data');
        const fullCast = JSON.parse(castDataDiv.textContent);

        castList.innerHTML = '';
        fullCast.forEach(member => {
            const li = document.createElement('li');
            li.textContent = member.name + ' - ' + member.character;
            castList.appendChild(li);
        });
        document.getElementById('show-more').style.display = 'none';
        document.getElementById('show-less').style.display = 'block';
    }

    function showLessCast() {
        const castList = document.getElementById('cast-list');
        const castDataDiv = document.getElementById('full-cast-data');
        const fullCast = JSON.parse(castDataDiv.textContent);

        castList.innerHTML = '';
        fullCast.slice(0, 10).forEach(member => {
            const li = document.createElement('li');
            li.textContent = member.name + ' - ' + member.character;
            castList.appendChild(li);
        });
        document.getElementById('show-more').style.display = 'block';
        document.getElementById('show-less').style.display = 'none';
    }

    
    window.showMoreCast = showMoreCast;
    window.showLessCast = showLessCast;
});

document.addEventListener("DOMContentLoaded", function() {
    function showMoreFavorite() {
        const movieItems = document.querySelectorAll('.filme-item');
        movieItems.forEach((item, index) => {
            if (index >= 7) {
                item.style.display = 'block';
            }
        });
        document.getElementById('show-more').style.display = 'none';
        document.getElementById('show-less').style.display = 'block';
    }

    function showLessFavorite() {
        const movieItems = document.querySelectorAll('.filme-item');
        movieItems.forEach((item, index) => {
            if (index >= 7) {
                item.style.display = 'none';
            }
        });
        document.getElementById('show-more').style.display = 'block';
        document.getElementById('show-less').style.display = 'none';
    }

    window.showMoreFavorite = showMoreFavorite;
    window.showLessFavorite = showLessFavorite;

    showLessFavorite();
});


function toggleFavorite(movieId) {
    fetch('/toggle_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ movie_id: movieId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            document.getElementById('btn-favoritar').checked = !document.getElementById('btn-favoritar').checked;
        } else {
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}