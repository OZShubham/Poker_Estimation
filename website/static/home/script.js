const estimateButton = document.getElementById("estimate-button");

estimateButton.addEventListener("click", (event) => {
	event.preventDefault();

	const cardsInput = document.getElementById("cards");
	const cards = cardsInput.value;

	// Implement logic to estimate the strength of the poker hand
});

// Add a click event listener to the Logout button
document.getElementById("logoutBtn").addEventListener("click", function() {
    // Perform logout actions, such as clearing session data or deleting cookies
    // Replace this with your own logout logic
    console.log("Logging out...");

    // Redirect to login page after successful logout
    window.location.href = "login.html";
});

