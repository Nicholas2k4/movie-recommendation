$(function () {
    const pageSize = 10;
    let allResults = [];

    function renderPage(page) {
        const slice = allResults.slice((page - 1) * pageSize, page * pageSize);
        const $ul = $('#plot-results').empty();

        slice.forEach(d => {
            $('<li class="list-group-item bg-dark text-light">').html(`
        <div class="d-flex">
          <img src="${d.poster_url}" class="poster-sm">
          <div>
            <h6 class="mb-1">${d.title}
              <span class="badge bg-secondary">${d.vote_average}</span>
            </h6>
            <small>${d.overview}</small>
          </div>
        </div>
      `).appendTo($ul);
        });

        const totalPages = Math.ceil(allResults.length / pageSize);
        const $nav = $('<nav class="mt-3">').appendTo($ul);
        const $pag = $('<ul class="pagination justify-content-center pagination-sm mb-0">').appendTo($nav);

        for (let i = 1; i <= totalPages; i++) {
            const li = $(`<li class="page-item"><a class="page-link">${i}</a></li>`).appendTo($pag);
            if (i === page) li.find('a').addClass('active');
            li.on('click', () => renderPage(i));
        }
    }

    $('#btn-plot').on('click', () => {
        const plot = $('#plot-input').val().trim();
        if (!plot) return alert('Please enter a plot description');

        const genre = $('#filter-genre').val() || null;
        const min_rating = parseFloat($('#filter-rating').val());

        $('#plot-results').html('<div class="text-muted">Loading…</div>');

        $.ajax({
            url: '/api/recommend/plot',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({ plot, k: 50, genre, min_rating }),
            success: data => {
                allResults = data.slice(0, 50);
                if (!allResults.length) {
                    $('#plot-results').html('<div class="text-warning">No matches.</div>');
                    return;
                }
                renderPage(1);
            },
            error: x => alert(`Error ${x.status}: ${x.responseText}`)
        });
    });
});
