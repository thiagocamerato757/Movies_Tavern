document.addEventListener('DOMContentLoaded', function() {
    var btnAvaliar = document.getElementById('btn-avaliar');
    var avaliacao = document.querySelector('.avaliacao');
    var submitButton = document.getElementById('submit-rating');
    var stars = document.querySelectorAll('.star-icon');
    var rating = parseInt(user_rating) || 0;
    var popup = document.getElementById('comment-popup');
    var span = document.getElementsByClassName("close")[0];
    var textarea = document.getElementById('comment-textarea');
    var isLoggedIn = (is_logged_in === 'true');
    

    if (rating > 0) {
        paintStars(rating);
        avaliacao.classList.add('desabilitada');
        btnAvaliar.textContent = 'Delete';
        stars.forEach(star => {
            star.style.pointerEvents = 'none';
        });
    } else {
        avaliacao.classList.add('desabilitada');
    }

    btnAvaliar.addEventListener('click', function() {
        if (!isLoggedIn) {
            fetch('/submit_rating', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    movie_id: movie_id
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    rating = 0;
                    paintStars(rating)
                    avaliacao.classList.add('avaliacao-enviada');
                    submitButton.style.display = 'none';
                    btnAvaliar.textContent = 'Rate';
                    stars.forEach(star => {
                        star.style.pointerEvents = 'none';
                    });
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
        else if (btnAvaliar.textContent === 'Delete') {
            rating = 0;
            paintStars(rating);
            submitButton.style.display = 'none';
            avaliacao.classList.remove('avaliacao-enviada');
            btnAvaliar.textContent = 'Rate';
            avaliacao.classList.add('desabilitada');
            deleteRating()
        } else {
            openPopup()
            avaliacao.classList.remove('desabilitada');
            stars.forEach(star => {
                star.style.pointerEvents = 'auto';
            });
            textarea.disabled = false;
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
            var comentario = textarea.value;
            fetch('/rate_movie', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    movie_id: movie_id,
                    rating: rating,
                    comentario: comentario
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'error') {
                    alert(data.message || 'There was an error processing your request.');
                } else if (data.status === 'rated') {
                    alert('Rating submitted successfully!');
                    avaliacao.classList.add('avaliacao-enviada');
                    submitButton.style.display = 'none';
                    btnAvaliar.textContent = 'Delete';
                    stars.forEach(star => {
                        star.style.pointerEvents = 'none';
                    });
                    textarea.disabled = true;
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('An error occurred. Please try again later.');
            });
        } else {
            alert('Please select a rating before submitting.');
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

    function deleteRating() {
        fetch('/delete_rating', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                movie_id: movie_id
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function openPopup() {
        popup.style.display = "flex";
    }

    span.onclick = function() {
        popup.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == popup) {
            popup.style.display = "none";
        }
    }

    // Ajusta a area de texto conforme o usuário digita
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
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
        const movieItems = document.querySelectorAll('.favorito-item');
        movieItems.forEach((item, index) => {
            if (index >= 7) {
                item.style.display = 'block';
            }
        });
        document.getElementById('show-more').style.display = 'none';
        document.getElementById('show-less').style.display = 'block';
    }

    function showLessFavorite() {
        const movieItems = document.querySelectorAll('.favorito-item');
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

document.addEventListener("DOMContentLoaded", function() {
    function showMoreReviews() {
        const reviewItems = document.querySelectorAll('.review-item');
        reviewItems.forEach((item, index) => {
            if (index >= 7) {
                item.style.display = 'block';
            }
        });
        document.getElementById('show-more-reviews').style.display = 'none';
        document.getElementById('show-less-reviews').style.display = 'block';
    }

    function showLessReviews() {
        const reviewItems = document.querySelectorAll('.review-item');
        reviewItems.forEach((item, index) => {
            if (index >= 7) {
                item.style.display = 'none';
            }
        });
        document.getElementById('show-more-reviews').style.display = 'block';
        document.getElementById('show-less-reviews').style.display = 'none';
    }

    window.showMoreReviews = showMoreReviews;
    window.showLessReviews = showLessReviews;

    showLessReviews();
});


function toggleFavorite(movieId) {
    fetch('/add_to_favorites', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ movie_id: movieId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            alert(data.error || 'There was an error processing your request.');
            document.getElementById('btn-favoritar').checked = !document.getElementById('btn-favoritar').checked;
        } else {
            alert(data.status === 'added' ? 'Added to favorites!' : 'Removed from favorites!');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        // alert('An error occurred. Please try again later.');
    });
}