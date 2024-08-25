$(document).ready(function () {
    $('#search-input').on('input', function () {
        var query = $(this).val();
        if (query.length > 0) {
            $.ajax({
                url: '/search-suggestions',
                method: 'GET',
                data: { query: query },
                success: function (response) {
                    var suggestions = response.suggestions.slice(0, 4); // Limit to 4 suggestions
                    var movieSuggestions = suggestions.filter(item => item.type === 'movie');
                    var tvShowSuggestions = suggestions.filter(item => item.type === 'tv_show');
                    var suggestionsList = '';

                    if (movieSuggestions.length > 0) {
                        suggestionsList += '<h3>Movies</h3>';
                        suggestionsList += movieSuggestions.map(function (item) {
                            return `
                                <li>
                                    <a href="/movie/${item.id}-${item.title.replace('-').toLowerCase()}">
                                        <img src="${item.poster}" alt="${item.title}" class="suggestion-poster">
                                        <div class="suggestion-details">
                                            <span class="suggestion-title">${item.title}</span>
                                            <span class="suggestion-rating">${item.rating}/10</span>
                                        </div>
                                    </a>
                                </li>
                            `;
                        }).join('');
                    }

                    if (tvShowSuggestions.length > 0) {
                        suggestionsList += '<h3>TV Shows</h3>';
                        suggestionsList += tvShowSuggestions.map(function (item) {
                            return `
                                <li>
                                    <a href="/tv-show/${item.id}-${item.title.replace(/ /g, '-').toLowerCase()}"> 
                                        <img src="${item.poster}" alt="${item.title}" class="suggestion-poster">
                                        <div class="suggestion-details">
                                            <span class="suggestion-title">${item.title}</span>
                                            <span class="suggestion-rating">${item.rating}/10</span>
                                        </div>
                                    </a>
                                </li>
                            `;
                        }).join('');
                    }

                    if (suggestionsList === '') {
                        suggestionsList = '<li class="no-results">No results found</li>';
                    }

                    $('#search-suggestions').html(suggestionsList);
                    $('#search-suggestions').show();
                }
            });
        } else {
            $('#search-suggestions').hide();
        }
    });

    $('#search-toggle').on('click', function () {
        $('#mobile-search-wrapper').fadeIn();
    });

    $('#mobile-search-close').on('click', function () {
        $('#mobile-search-wrapper').fadeOut();
    });

    $('#mobile-search-input').on('input', function () {
        var query = $(this).val();
        if (query.length > 0) {
            $.ajax({
                url: '/search-suggestions',
                method: 'GET',
                data: { query: query },
                success: function (response) {
                    var suggestions = response.suggestions.slice(0, 4); // Limit to 4 suggestions
                    var movieSuggestions = suggestions.filter(item => item.type === 'movie');
                    var tvShowSuggestions = suggestions.filter(item => item.type === 'tv_show');
                    var suggestionsList = '';

                    if (movieSuggestions.length > 0) {
                        suggestionsList += '<h3>Movies</h3>';
                        suggestionsList += movieSuggestions.map(function (item) {
                            return `
                                <li>
                                    <a href="/movie/${item.id}-${item.title.replace('-').toLowerCase()}">
                                        <img src="${item.poster}" alt="${item.title}" class="suggestion-poster">
                                        <div class="suggestion-details">
                                            <span class="suggestion-title">${item.title}</span>
                                            <span class="suggestion-rating">${item.rating}/10</span>
                                        </div>
                                    </a>
                                </li>
                            `;
                        }).join('');
                    }

                    if (tvShowSuggestions.length > 0) {
                        suggestionsList += '<h3>TV Shows</h3>';
                        suggestionsList += tvShowSuggestions.map(function (item) {
                            return `
                                <li>
                                    <a href="/tv-show/${item.id}-${item.title.replace(/ /g, '-').toLowerCase()}"> 
                                        <img src="${item.poster}" alt="${item.title}" class="suggestion-poster">
                                        <div class="suggestion-details">
                                            <span class="suggestion-title">${item.title}</span>
                                            <span class="suggestion-rating">${item.rating}/10</span>
                                        </div>
                                    </a>
                                </li>
                            `;
                        }).join('');
                    }

                    if (suggestionsList === '') {
                        suggestionsList = '<li class="no-results">No results found</li>';
                    }

                    $('#mobile-search-suggestions').html(suggestionsList);
                    $('#mobile-search-suggestions').show();
                }
            });
        } else {
            $('#mobile-search-suggestions').hide();
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var menuToggle = document.getElementById('menu-toggle');
    var menuClose = document.getElementById('menu-close');
    var navWrapper = document.getElementById('nav-wrapper');

    if (menuToggle) {
        menuToggle.addEventListener('click', function () {
            if (navWrapper.classList.contains('show')) {
                navWrapper.classList.remove('show');
            } else {
                navWrapper.classList.add('show');
            }
        });
    }

    if (menuClose) {
        menuClose.addEventListener('click', function () {
            navWrapper.classList.remove('show');
        });
    }
});