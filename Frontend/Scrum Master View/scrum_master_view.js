function flipCards() {
    var cards = document.getElementsByClassName('flip-card-inner');
    for (var i = 0; i < cards.length; i++) {
      cards[i].classList.toggle('flipped');
    }
  }

// Toggle button text on click

function handleClick() {
    const initialText = 'Reveal';
  
    if (button.textContent.toLowerCase().includes(initialText.toLowerCase())) {
      button.textContent = 'Hide';
    } else {
      button.textContent = initialText;
    }
  };
