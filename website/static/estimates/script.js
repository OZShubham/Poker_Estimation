var cardInners = document.getElementsByClassName("card-inner");
function revealAll() {
    
    for (var i = 0; i < cardInners.length; i++) {
        cardInners[i].style.transform = cardInners[i].style.transform === 'rotateY(180deg)' ? '' : 'rotateY(180deg)';
    }
}
