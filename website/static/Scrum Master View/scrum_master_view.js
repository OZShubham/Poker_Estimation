// Sample data for flip cards
const cardData = [
  { id: 1, front: 'Card 1 Front', back: 'Card 1 Back' },
  { id: 2, front: 'Card 2 Front', back: 'Card 2 Back' },
  { id: 3, front: 'Card 3 Front', back: 'Card 3 Back' }
];

// Function to create flip cards
function createFlipCard(data) {
  const card = document.createElement('div');
  card.classList.add('card');
  card.innerHTML = `
    <div class="card-inner">
      <div class="card-front">${data.front}</div>
      <div class="card-back">${data.back}</div>
    </div>
  `;
  return card;
}

// Function to add flip cards to the card container
function renderCards(cardData) {
  const cardContainer = document.getElementById('card-container');
  cardContainer.innerHTML = '';
  cardData.forEach(function(card) {
    cardContainer.appendChild(createFlipCard(card));
  });
}

// Render initial flip cards
renderCards(cardData);

// Add event listener to reveal button
const revealBtn = document.getElementById('reveal-btn');
revealBtn.addEventListener('click', function() {
  const cards = document.getElementsByClassName('card-inner');
  for (let i = 0; i < cards.length; i++) {
    cards[i].style.transform = 'rotateY(180deg)';
  }
});
