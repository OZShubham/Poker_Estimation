function addItem(button) {
  var textarea = button.nextElementSibling;
  var newItem = document.createElement("div");
  newItem.innerHTML = `
        <textarea placeholder="Add item" style="margin-top: 5px;"></textarea>
        <span class="delete-button" onclick="removeItem(this)">Delete</span>
    `;
  textarea.parentNode.parentNode.insertBefore(
    newItem,
    textarea.parentNode.nextSibling
  );
}

function removeItem(span) {
  span.parentNode.remove();
}

function submitForm() {
  var form = document.getElementById("retro-form");
  var whatWentWellInput = document.getElementById("what_went_well");
  var whatWentWrongInput = document.getElementById("what_went_wrong");
  var whatCanBeImprovedInput = document.getElementById("what_can_be_improved");

  var whatWentWellItems = document.querySelectorAll("#what-went-well textarea");
  var whatWentWrongItems = document.querySelectorAll(
    "#what-went-wrong textarea"
  );
  var whatCanBeImprovedItems = document.querySelectorAll(
    "#what-can-be-improved textarea"
  );

  var whatWentWellValues = Array.from(whatWentWellItems).map(
    (item) => item.value
  );
  var whatWentWrongValues = Array.from(whatWentWrongItems).map(
    (item) => item.value
  );
  var whatCanBeImprovedValues = Array.from(whatCanBeImprovedItems).map(
    (item) => item.value
  );

  whatWentWellInput.value = whatWentWellValues.join(",");
  whatWentWrongInput.value = whatWentWrongValues.join(",");
  whatCanBeImprovedInput.value = whatCanBeImprovedValues.join(",");

  form.submit();
}

document
  .getElementById("retro-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    submitForm();
  });
