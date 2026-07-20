window.displayNav = function () {
    var navbar = document.getElementById('navlist');
    if (navbar.style.display === "block") {
        navbar.style.display = "none";
    } else {
        navbar.style.display = "block";
    }
}