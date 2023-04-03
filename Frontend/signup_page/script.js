function validateForm() {
	let name = document.getElementById("name").value;
	let email = document.getElementById("email").value;
	let password = document.getElementById("password").value;

	if (name === "" || email === "" || password === "") {
		alert("Please fill in all fields.");
		return false;
	}
}

/* Name validation */

const nameInput = document.getElementById("name");

function validateName() {
  const name = nameInput.value;
  const regex = /^[a-zA-Z]+$/; // Regular expression to match alphabetic characters only

  if (!regex.test(name)) {
    nameInput.setCustomValidity("Please enter a valid name with alphabetic characters only");
  } else {
    nameInput.setCustomValidity("");
  }
}

nameInput.addEventListener("change", validateName);


/* Password matching validation. */

const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirm-password");

function validatePassword() {
  if (password.value != confirmPassword.value) {
    confirmPassword.setCustomValidity("Passwords don't match");
  } else {
    confirmPassword.setCustomValidity("");
  }
}

password.addEventListener("change", validatePassword);
confirmPassword.addEventListener("keyup", validatePassword);

/* Email validation. */

const emailInput = document.getElementById("email");

function validateEmail() {
  const email = emailInput.value;
  if (!email.includes("@") || !email.includes(".")) {
    emailInput.setCustomValidity("Please enter a valid email address");
  } else {
    emailInput.setCustomValidity("");
  }
}

emailInput.addEventListener("change", validateEmail);

/* Disable button logic  */

const signUpButton = document.getElementById("login-btn");

function validateForm() {
  if (nameInput.value && emailInput.value && password.value && confirmPassword.value) {
    signUpButton.removeAttribute("disabled");
  } else {
    signUpButton.setAttribute("disabled", "disabled");
  }
}

nameInput.addEventListener("input", validateForm);
emailInput.addEventListener("input", validateForm);
password.addEventListener("input", validateForm);
confirmPassword.addEventListener("input", validateForm);
