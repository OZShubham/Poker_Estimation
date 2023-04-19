/*document.getElementById("update-form").addEventListener("submit", function (event) {
  event.preventDefault();
  updatePokerBoard();
});


function updatePokerBoard() {
  var form = document.getElementById("update-form");
  var formData = new FormData(form);
  fetch("https://us-central1-pokerestimation-380716.cloudfunctions.net/update_poker_board", {
    method: "POST",
    body: formData
  })
    .then(function (response) {
      if (response.ok) {
        return response.text();
      } else {
        throw new Error("Error: " + response.status);
      }
    })
    .then(function (responseText) {
      console.log("Success:", responseText);
    })
    .catch(function (error) {
      console.error(error);
    });
}
*/
