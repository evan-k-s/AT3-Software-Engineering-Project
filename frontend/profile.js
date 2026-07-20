    
export const displayAuthors = async (author) => {    
    var authorContent = document.createElement("div");
    var apiUrl = `https://openlibrary.org/search/authors.json?q=${encodeURIComponent(author)}&limit=1`;
    var authorResponse = await fetch(apiUrl);
    if (!authorResponse.ok) {
        throw new Error("Failed to fetch data");
    }
    var data = await authorResponse.json();
    var authorResult = data.docs;
    var authorKey = authorResult[0].key;
    var worksURL = `https://openlibrary.org/authors/${authorKey}/works.json?limit=3`;
    var worksResponse = await fetch(worksURL);
    if (!worksResponse.ok) {
        throw new Error("Failed to fetch data");
    }
    var worksData = await worksResponse.json();
    var works = worksData.entries;

    var booksul = document.createElement('ul');
    works.forEach(work => {
        var bookli = document.createElement('li');
        bookli.textContent = work.title;
        booksul.appendChild(bookli);
    })
    authorContent.classList.add("author-card");
    authorContent.innerHTML = `<p class="fav-author-name">${author}</p>
            <p>Some of their titles... </p>`;
    authorContent.appendChild(booksul);
    return authorContent;
}