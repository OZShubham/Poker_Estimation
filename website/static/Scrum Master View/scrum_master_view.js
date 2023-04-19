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

function storePokerEstimation() {
    // Get the poker estimation data from the form
  var name = document.getElementById('name').value;
  var estimate = document.getElementById('estimate').value;

    // Create the request body as JSON
  var data = {
    "name": name,
    "estimate": estimate
  };

  // Send an HTTP POST request to the Cloud Function endpoint with the request body
  fetch('https://us-central1-pokerestimation-380716.cloudfunctions.net/store_poker_estimation', {
    method: 'POST',
    body: JSON.stringify(data)
  })
  .then(response => response.text())
  .then(data => {
    console.log(data); // Log the response from the Cloud Function
  })
  .catch(error => {
    console.error('Error:', error);
  });
};
