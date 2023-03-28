function validateForm() {
	let name = document.getElementById("name").value;
	let email = document.getElementById("email").value;
	let password = document.getElementById("password").value;

	if (name === "" || email === "" || password === "") {
		alert("Please fill in all fields.");
		return false;
	}
}
