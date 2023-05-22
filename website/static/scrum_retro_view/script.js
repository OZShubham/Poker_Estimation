function addItem(button) {
    var textarea = button.nextElementSibling;
    var newItem = document.createElement("div");
    newItem.innerHTML = `
        <textarea placeholder="Add item"></textarea>
        <span class="delete-button" onclick="removeItem(this)">Delete</span>
    `;
    textarea.parentNode.parentNode.insertBefore(newItem, textarea.parentNode.nextSibling);
}

function removeItem(span) {
    span.parentNode.remove();
}

function submitForm() {
    var form = document.getElementById("retro-form");
    var whatWentWellInput = document.getElementById("what_went_well");
    var whatWentWrongInput = document.getElementById("what_went_wrong");
    var whatCanBeImprovedInput = document.getElementById("what_can_be_improved");
    
    var whatWentWellItems = document.querySelectorAll(".column:nth-child(1) textarea");
    var whatWentWrongItems = document.querySelectorAll(".column:nth-child(2) textarea");
    var whatCanBeImprovedItems = document.querySelectorAll(".column:nth-child(3) textarea");
    
    whatWentWellInput.value = Array.from(whatWentWellItems).map(item => item.value).join(",");
    whatWentWrongInput.value = Array.from(whatWentWrongItems).map(item => item.value).join(",");
    whatCanBeImprovedInput.value = Array.from(whatCanBeImprovedItems).map(item => item.value).join(",");
    
    form.submit();
}

document.getElementById("retro-form").addEventListener("submit", function(event) {
    event.preventDefault();
    submitForm();
});