$(document).ready(function () {
    function fetchSuggestions(query, targetElement) {
        if (query.length > 1) {
            $.ajax({
                url: '/search-suggestions',
                method: 'GET',
                data: { query: query },
                success: function (response) {
                    let suggestions = response.suggestions.slice(0, 5); // Limit to 5
                    let movieSuggestions = suggestions.filter(item => item.type === 'movie');
                    let tvShowSuggestions = suggestions.filter(item => item.type === 'tv_show');
                    let suggestionsList = '';

                    if (movieSuggestions.length > 0) {
                        suggestionsList += `
                            <h3 class="text-lg font-semibold text-gray-200 border-b border-gray-700 px-3 py-2">Movies</h3>
                            <ul class="space-y-2 p-3">
                        `;
                        movieSuggestions.forEach(item => {
                            suggestionsList += `
                                <li class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-800 transition">
                                    <a href="/movie/${item.id}-${item.title.replace(/ /g, '-').toLowerCase()}" class="flex items-center gap-3 w-full">
                                        <img src="${item.poster}" alt="${item.title}" class="w-12 h-16 rounded-lg object-cover shadow-md">
                                        <div class="flex flex-col">
                                            <span class="text-white font-medium">${item.title}</span>
                                            <span class="text-sm text-gray-400">${item.rating}/10</span>
                                        </div>
                                    </a>
                                </li>
                            `;
                        });
                        suggestionsList += '</ul>';
                    }

                    if (tvShowSuggestions.length > 0) {
                        suggestionsList += `
                            <h3 class="text-lg font-semibold text-gray-200 border-b border-gray-700 px-3 py-2 mt-3">TV Shows</h3>
                            <ul class="space-y-2 p-3">
                        `;
                        tvShowSuggestions.forEach(item => {
                            suggestionsList += `
                                <li class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-800 transition">
                                    <a href="/tv-show/${item.id}-${item.title.replace(/ /g, '-').toLowerCase()}" class="flex items-center gap-3 w-full">
                                        <img src="${item.poster}" alt="${item.title}" class="w-12 h-16 rounded-lg object-cover shadow-md">
                                        <div class="flex flex-col">
                                            <span class="text-white font-medium">${item.title}</span>
                                            <span class="text-sm text-gray-400">${item.rating}/10</span>
                                        </div>
                                    </a>
                                </li>
                            `;
                        });
                        suggestionsList += '</ul>';
                    }

                    if (suggestionsList === '') {
                        suggestionsList = '<li class="text-center text-gray-400 py-3">No results found</li>';
                    }

                    $(targetElement).html(suggestionsList).show();
                }
            });
        } else {
            $(targetElement).hide();
        }
    }

    // Desktop Search
    $('#search-input').on('input', function () {
        fetchSuggestions($(this).val(), '#search-suggestions');
    });

    // Mobile Search
    $('#mobile-search-input').on('input', function () {
        fetchSuggestions($(this).val(), '#mobile-search-suggestions');
    });

    // Toggle mobile search
    $('#search-toggle').on('click', function () {
        $('#mobile-search-wrapper').fadeIn().removeClass('hidden');
        $('#mobile-search-input').focus();
    });

    $('#mobile-search-close').on('click', function () {
        $('#mobile-search-wrapper').fadeOut().addClass('hidden');
    });

    // Hide suggestions when clicking outside
    $(document).on('click', function (event) {
        if (!$(event.target).closest('.search-container').length) {
            $('#search-suggestions, #mobile-search-suggestions').hide();
        }
    });
});


document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('menu-toggle').addEventListener('click', function() {
        document.getElementById('mobile-menu').classList.remove('translate-x-full');
    });

    document.getElementById('menu-close').addEventListener('click', function() {
        document.getElementById('mobile-menu').classList.add('translate-x-full');
    });
});
