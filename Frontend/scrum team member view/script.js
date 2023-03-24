
var panelsElement = document.querySelectorAll('.card')

var removeActiveClasses = () => {
    panelsElement.forEach(card => {
        card.classList.remove('expanded');
    });
};
panelsElement.forEach(card => {
    card.addEventListener('click',() => {
        removeActiveClasses();
        card.classList.toggle('expanded')
    });
});
   
