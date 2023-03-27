const form = document.querySelector('form');
const usernameInput = document.querySelector('#username');
const passwordInput = document.querySelector('#password');

form.addEventListener('submit', (e) => {
	e.preventDefault();

	const username = usernameInput.value;
	const password = passwordInput.value;

	if (username === 'admin' && password === 'password') {
		window.location.href = 'dashboard.html';
	} else {
		alert('Invalid username or password. Please try again.');
	}
});
