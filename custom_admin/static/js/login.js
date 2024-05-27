/**
 * This code snippet assigns an event handler to the 'submit' event of the 'loginForm' element.
 * When the form is submitted, it performs form validation by checking if the email and password fields are empty.
 * If either field is empty, an error message is displayed next to the respective field.
 * The error message is set by modifying the innerHTML of the error element and changing its visibility to 'visible'.
 * The function showError is used to display the error message and set the isValid flag to false.
 * After validating the form, the function returns the value of the isValid flag.
 */
document.getElementById('loginForm').onsubmit = function () {
    var isValid = true;
    var email = document.getElementById('email');
    var password = document.getElementById('password');
    var emailError = document.getElementById('email-error');
    var passwordError = document.getElementById('password-error');

    function showError(element, message) {
        element.innerHTML = message;
        element.style.visibility = 'visible';
        isValid = false;
    }

    emailError.innerHTML = '';
    emailError.style.visibility = 'hidden';
    passwordError.innerHTML = '';
    passwordError.style.visibility = 'hidden';

    if (email.value.trim() === "") {
        showError(emailError, 'Please enter your email.');
    }
    if (password.value.trim() === "") {
        showError(passwordError, 'Please enter your password.');
    }

    return isValid;
};
