const genreSelect = document.getElementById('genre-select');

const selectedValues = new Set()

genreSelect.addEventListener('click', () => {
    genreSelect.classList.toggle('open');
});

dropdown.addEventListener('click', (e) => {
    const value = e.target.getAttribute('data-value');
    const label = e.target.textContent;
    
    if (!selectedValues.has(value)) {
        if (selectedValues.size == 0) {
            const title = document.getElementById('dropdown-arrow');
            title.innerHTML = "&#9662;";
        };

        selectedValues.add(value);

        const tag = document.createElement('span');
        tag.innerHTML = `${label} <i data-remove="${value}">&times;</i>`;
        selectedGenres.appendChild(tag);
    }
});

selectedGenres.addEventListener('click', (e) => {
    if (e.target.dataset.remove) {
        if (selectedValues.size == 1) {
            const title = document.getElementById('dropdown-arrow');
            title.innerHTML = "&#9662; Filter Genres";
        };

        const valueToRemove = e.target.dataset.remove;
        selectedValues.delete(valueToRemove);
        e.target.parentElement.remove();
    }
})