
var panelsElement = document.querySelectorAll('.card')

var removeActiveClasses = () => {
    panelsElement.forEach(card => {
        card.classList.remove('expanded');
    });
};
panelsElement.forEach(card => {
    card.addEventListener('click',() => {
        if(card.classList.contains('expanded')){
            card.classList.remove('expanded');
        }
        else{
            removeActiveClasses();
            card.classList.toggle('expanded')
        }
    });
});
   
