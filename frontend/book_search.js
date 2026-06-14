const searchButton = document.getElementById("searchButton");
const searchInput = document.getElementById("title-search");
const resultsDropdown = document.getElementById("title-results");

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
            option.value = `${book.title} by ${book.author_name}`;
            console.log(option.value);
            resultsDropdown.appendChild(option);
        });
        searchInput.showPicker();
    } catch (error) {
        console.log("Failed to load results");
    }
})