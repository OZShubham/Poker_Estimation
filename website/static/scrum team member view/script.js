document.addEventListener('DOMContentLoaded', function() {
  // Get all the story point cards
  var storyPointCards = document.querySelectorAll('.story-point-card');
  
  // Add click event listener to each story point card
  storyPointCards.forEach(function(card) {
    card.addEventListener('click', function() {
      // Check if the clicked card is already active
      var isActive = this.classList.contains('active');
      
      // Remove the active class from all story point cards
      storyPointCards.forEach(function(card) {
        card.classList.remove('active');
        card.style.height = ''; // Reset the height property
      });
      
      // If the clicked card is not already active
      if (!isActive) {
        // Add the active class to the clicked story point card
        this.classList.add('active');
        
        // Set the height of the clicked card to its scroll height to expand it
        this.style.height = this.scrollHeight + 'px';
      } else {
        // If the clicked card is already active, remove the active class
        // and reset the height property to collapse it
        this.classList.remove('active');
        this.style.height = '';
      }
    });
  });
});

$(document).ready(function() {
        // Add click event listener to story-point-cards
        $(".story-point-card").on("click", function() {
            // Get the data-value attribute of the clicked element
            var value = $(this).data("value");
            // Send the data to Flask route via an HTTP request (e.g., AJAX)
            $.ajax({
                type: "POST",
                url: "/your-flask-route",
                data: { value: value },
                success: function(response) {
                    // Handle success response
                    console.log(response);
                },
                error: function(error) {
                    // Handle error response
                    console.log(error);
                }
            });
        });
    });