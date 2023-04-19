/*document.getElementById("create-poker-board-form").addEventListener("submit", function(event) {
    // Prevent form submission
    event.preventDefault();

    // Get form data
    var teamId = document.getElementById("team-id").value;
    var userRole = document.getElementById("user-role").value;
    var userId = document.getElementById("user-id").value;
    var pokerBoardType = document.getElementById("poker-board-type").value;

    // Validate required fields
    if (teamId === '' || userRole === '' || userId === '' || pokerBoardType === '0') {
        alert("Please fill in all required fields.");
        return;
    }

    // Make API request to Cloud Function
    // Replace with your actual API endpoint and library for making API requests
    // Example using fetch()
    fetch('https://us-central1-pokerestimation-380716.cloudfunctions.net/create_poker_board', {
        method: 'POST',
        body: JSON.stringify({
            team_id: teamId,
            user_role: userRole,
            poker_board_type: pokerBoardType,
            user_id: userId
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(function(response) {
        if (response.ok) {
            // Handle successful response from Cloud Function
            return response.json(); // Parse response JSON
        } else {
            // Handle error response from Cloud Function
            throw new Error('Failed to create Poker Board. Please try again.');
        }
    })
    .then(function(data) {
        // Handle data from Cloud Function
        alert("Poker Board created successfully!"); // Show success message
        // Do something with data returned by Cloud Function if needed
        console.log(data);
    })
    .catch(function(error) {
        console.error(error);
        // Handle error in making API request
        alert(error.message); // Show error message from throw statement
    });
});*/
