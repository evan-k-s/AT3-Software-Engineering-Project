const searchButton = document.getElementById("searchButton");
const searchInput = document.getElementById("title-search");
const resultsDropdown = document.getElementById("title-results");

const titleField = document.getElementById("title");
const authorField = document.getElementById("author");
const olidField = document.getElementById("olid");

let booksResults = [];

searchButton.addEventListener('click', async function(event) {
    let search = searchInput.value.trim();
    if (search.length < 3) {
        alert("Please enter at least 3 characters to search");
        return;
    }

    try {
        const apiUrl = `https://openlibrary.org/search.json?q=${encodeURIComponent(search)}`;
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error("Failed to fetch data");
        }
        const data = await response.json();
        booksResults = data.docs;
        resultsDropdown.innerHTML = "";
        booksResults.forEach(book => {
            const option = document.createElement('option');
            option.value = `${book.title} by ${book.author_name} (${book.cover_edition_key})`;
            option.setAttribute('data-title', book.title);
            option.setAttribute('data-author', book.author_name);
            option.setAttribute('data-olid', book.cover_edition_key);
            resultsDropdown.appendChild(option);
        });
        searchInput.showPicker();
    } catch (error) {
        console.log("Failed to load results");
    }
});


searchInput.addEventListener('input', function(event) {
    const selectedBook = event.target.value;
    const selectedOption = resultsDropdown.querySelector(`option[value="${selectedBook}"]`);

    if (selectedOption) {
        const title = selectedOption.getAttribute('data-title');
        const author = selectedOption.getAttribute('data-author');
        const olid = selectedOption.getAttribute('data-olid');

        titleField.value = title;
        authorField.value = author;
        olidField.value = olid;
    } else {
        titleField.value = "";
        authorField.value = "";
        olidField.value = "";
    }
})