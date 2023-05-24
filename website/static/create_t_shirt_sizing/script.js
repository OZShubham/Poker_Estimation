function selectStoryPoint(point) {
  var cards = document.querySelectorAll("#story-point-cards > div");
  for (var i = 0; i < cards.length; i++) {
    cards[i].classList.remove("selected");
  }
  document.getElementById("story_point").value = point;
  event.target.classList.add("selected");
}
