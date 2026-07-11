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
            title.innerHTML = "&#9662; Filter Authors";
        };

        const valueToRemove = e.target.dataset.remove;
        selectedValues.delete(valueToRemove);
        e.target.parentElement.remove();
    }
})

document.addEventListener('click', (e) => {
    if (!genreSelect.contains(e.target)) {
        genreSelect.classList.remove('open');
    }
})

let eraGap = 1;

const rangeInput = document.querySelectorAll(".range-input input"),
eraInput = document.querySelectorAll(".fields input"),
progress = document.querySelector(".slider .progress");

rangeInput.forEach(input => {
    input.addEventListener("input", (e) => {
        let minVal = parseInt(rangeInput[0].value),
        maxVal = parseInt(rangeInput[1].value);

        if (maxVal - minVal < eraGap) {
            if (e.target.className == "range-min") {
                rangeInput[0].value = maxVal - eraGap;
            } else {
                rangeInput[1].value = minVal + eraGap;
            }
        } else {
            eraInput[0].value = minVal;
            eraInput[1].value = maxVal;
            progress.style.left = ((minVal - rangeInput[0].min) / (rangeInput[0].max - rangeInput[0].min)) * 100 + "%";
            progress.style.right = 100 - ((maxVal - rangeInput[1].min) / (rangeInput[1].max - rangeInput[1].min)) * 100 + "%";
            era_min = minVal;
            era_max = maxVal;
        };
    });
});

eraInput.forEach(input => {
    input.addEventListener("input", (e) => {
        let minVal = parseInt(eraInput[0].value),
        maxVal = parseInt(eraInput[1].value);

        if ((maxVal - minVal >= eraGap) && (maxVal <= rangeInput[1].max) && (minVal >= rangeInput[0].min)) {
            if (e.target.className == "era-min") {
                rangeInput[0].value = minVal;
                progress.style.left = ((minVal - rangeInput[0].min) / (rangeInput[0].max - rangeInput[0].min)) * 100 + "%";
                era_min = minVal;
            } else {
                rangeInput[1].value = maxVal;
                progress.style.right = 100 - ((maxVal - rangeInput[1].min) / (rangeInput[1].max - rangeInput[1].min)) * 100 + "%";
                era_max = maxVal;
            }
        };
    });
});