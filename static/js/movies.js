$(function () {
    // ---- Select2 search ----
    $('#movie-select').select2({
        placeholder: 'Search movie …',
        minimumInputLength: 2,
        ajax: {
            url: '/api/search',
            data: p => ({ q: p.term }),
            processResults: d => ({
                results: d.results.map(m => ({
                    id: m.id,
                    text: m.text,
                    poster_url: m.poster_url
                }))
            })
        },
        templateResult: m => {
            if (!m.id) return m.text;
            return $(`<span><img src="${m.poster_url}" class="poster-sm">${m.text}</span>`);
        },
        templateSelection: m => m.text || m.id
    });

    // ---- selected list ----
    const selected = new Set();
    function renderSelected() {
        const $ul = $('#selected-list').empty();
        selected.forEach(id => {
            const text = $(`#movie-select option[value="${id}"]`).text();
            $('<li class="list-group-item d-flex justify-content-between align-items-center">')
                .text(text)
                .append(
                    $('<button class="btn-close btn-close-sm"></button>').on('click', () => {
                        selected.delete(id);
                        $(`#movie-select option[value="${id}"]`).remove();
                        renderSelected();
                    })
                ).appendTo($ul);
        });
    }
    $('#movie-select').on('select2:select', e => {
        selected.add(e.params.data.id);
        renderSelected();
    });

    // ---- pagination helpers ----
    const pageSize = 10;
    let allResults = [];
    function renderPage(page) {
        const slice = allResults.slice((page - 1) * pageSize, page * pageSize);
        const $ul = $('#movie-results').empty();

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

    // ---- recommend ----
    $('#btn-movie').on('click', () => {
        if (selected.size === 0) return alert('Pick at least one movie!');

        const genre = $('#filter-genre').val() || null;
        const min_rating = parseFloat($('#filter-rating').val());

        $('#movie-results').html('<div class="text-muted">Loading…</div>');

        $.ajax({
            url: '/api/recommend/movies',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({ imdb_ids: [...selected], k: 50, genre, min_rating }),
            success: data => {
                allResults = data.slice(0, 50);
                if (!allResults.length) {
                    $('#movie-results').html('<div class="text-warning">No matches.</div>');
                    return;
                }
                renderPage(1);
            },
            error: x => alert(`Error ${x.status}: ${x.responseText}`)
        });
    });
});
