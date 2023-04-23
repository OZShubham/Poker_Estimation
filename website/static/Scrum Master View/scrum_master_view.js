document.getElementById('jira-form').addEventListener('submit', function(event) {
  event.preventDefault();
  var jiraId = document.getElementById('jira-id').value;

  var cardContainer = document.getElementById('card-container');
  cardContainer.innerHTML = '';

  // Fetch data from backend (replace with your actual API call)
  fetch('/scrum_master_view') // Update the URL to match your backend API endpoint
    .then(response => response.json())
    .then(data => {
      var userId = data.user_id; // Fetch user_id from fetched data
      var storyPoints = data.story_points; // Fetch story_points from fetched data

      // Create a new card element
      var card = document.createElement('div');
      card.className = 'card';

      // Create a card front element
      var front = document.createElement('div');
      front.className = 'front';
      front.textContent = 'Click to reveal'; // Text content on the front of the card

      // Create a card back element
      var back = document.createElement('div');
      back.className = 'back';

      // Create a user ID element
      var userIdElement = document.createElement('p');
      userIdElement.textContent = 'User ID: ' + userId;

      // Create a story points element
      var storyPointsElement = document.createElement('p');
      storyPointsElement.textContent = 'Story Points: ' + storyPoints;

      // Append user ID and story points elements to the card back element
      back.appendChild(userIdElement);
      back.appendChild(storyPointsElement);

      // Append card front and back elements to the card element
      card.appendChild(front);
      card.appendChild(back);

      // Append the card element to the card container
      cardContainer.appendChild(card);

      // Add click event listener to the card element
      card.addEventListener('click', function() {
        // Flip the card to reveal the back side
        front.style.display = 'none';
        back.style.display = 'block';
      });
    })
    .catch(error => console.error('Error fetching data:', error));
});
