/**
 * The regex-based validation functions are:
 *
 * validateName(name): Validates the name field by allowing only alphabetic characters and spaces, with a length between 1 and 32 characters.
 * validateEmail(email): Validates the email field by allowing only valid email addresses.
 * validateCellNumber(cell): Validates the cell phone number field by allowing only international phone numbers with a minimum length of 6 digits and a maximum length of 14 digits.
 * validatePassword(password): Validates the password field by requiring at least one uppercase letter, one lowercase letter, one digit, one special character, and a length between 8 and 64 characters.
 * The DOM interface provides functionality for user login and registration. It consists of:
 *
 * Login form with username and password fields and a submit button.
 * Registration form with name, email, cell phone number, password fields, and a submit button.
 * The login function takes in the event, reads the username and password, validates them using the validateEmail and validatePassword functions, respectively. If the validation succeeds, it sends the form data to the server using fetch API and logs in the user. If the response from the server contains a UUID, it sets the account cookie and redirects to the account page. Otherwise, it displays an error message to the user.
 *
 * The register_user function creates a new user account by reading the input fields, validating them using the validateName, validateEmail, validateCellNumber, and validatePassword functions, and sending the data to the server using fetch API. If the response status is 201, it logs the status text. Otherwise, it extracts the data from the response and adds it to the account details.
 *
 * Both the login and registration forms use event listeners to trigger the login and register_user functions, respectively, when the submit button is clicked.
 *
 *
 */

// Regex Based Validators
function validateName(name) {
  const regex = /^[a-zA-Z]{1,32}( [a-zA-Z]{1,32}){0,2}$/;
  return regex.test(name);
}
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}
function validateCellNumber(cell) {
  const regex = /^\+(?:[0-9] ?){6,14}[0-9]$/;
  return regex.test(cell);
}
function validatePassword(password) {
  const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,64}$/;
  return regex.test(password);
}

// DOM Interface

// login dom interface
const login_form = document.getElementById('auth_form');
const username_input = document.getElementById('username');
const password_input = document.getElementById('password');

const login_btn = document.getElementById('submit_login');
const message_elem = document.getElementById('message');

login_form.addEventListener('submit', async (event) => {
   await login(event);
});
login_btn.addEventListener( 'click', async (event) => {
    await login(event);
});


// get the input DOM Fields for registering a new user
// const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
// const cellInput = document.getElementById('cell');
const passwordInput = document.getElementById('r_password');



// Attach a validation function to the form's submit event
const registrationForm = document.getElementById('registration_form');
const registerButton = document.getElementById('submit_registration');



async function login (event) {
    /**
     * login function takes in even and read password and username
     * then validates both and then logs in
     */
    event.preventDefault();
    const username = username_input.value;
    const password = password_input.value;

    if (!validateEmail(username)) {
        alert('Username must at least be a valid email address');
        return;
    }
    if (!validatePassword(password)) {
        alert('Password does not meet minimum recommended complexity');
        return;
    }
    // send form data
    const response  = await fetch(login_form.action, {
        method: login_form.method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username, password
        })
    });
    const data = await response.json()
    console.log(`data account : ${data}`)
    //   check if user is logged in
    if (data.status && data.payload && data.payload.uuid) {
        console.log("setting up login")
        account_data = data.payload;
        setAccountCookie(account_data)
        window.location.href = `/account`;
    }else{
        account_data = {};
        setAccountCookie(account_data);
        message_elem.innerHTML = data.message;
    }
}


const register_user = async (mode) => {
    /**
     *  register_user
     * register_user -> creates a new user account
     * @param {mode}
     */

    // const name = nameInput.value;
    const email = emailInput.value;
    // const cell = cellInput.value;
    const password = passwordInput.value;

    console.log("creating new account");
    console.log(registrationForm.action);

    // if (!validateName(name)){
    //     alert("Names or Names are invalid");
    //     return;
    // }
    if (!validateEmail(email)){
        alert("Email should at least be a valid email address");
        return;
    }
    // if (!validateCellNumber(cell)){
    //     alert("Cell number should contain international codes");
    //     return;
    // }
    if (!validatePassword(password)){
        alert("Try to meet our minimum password complexity requirements");
        return;
    }

    const request = new Request(registrationForm.action, {
        method: registrationForm.method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email,  password }),
        mode: mode,
        credentials: "same-origin",
    });


    try {
        let response = await fetch(request);
        const data = await response.json();

        if (response.status === 200 || response.status === 201) {
            document.getElementById('message-subscribe').innerHTML = `${data.message} </br>
                <a class="btn btn-dark" href="/login"> <i class="fa fa-user"> </i> Login </a>
            `;
        } else {
            document.getElementById('message-subscribe').innerHTML = "An error occurred.";
        }
    }catch (e){
        document.getElementById('message-subscribe').innerHTML = "An error occurred.";
    }

};

// Attach the submitForm function to the form's submit event
registrationForm.addEventListener('submit', async event => {
    /**
     * will trigger a method to register a new user and pass the event
     * @param {event}
     */
    event.preventDefault();
    await register_user( 'cors');
});
// Attach the submitForm function to the register button's click event
registerButton.addEventListener('click', async (event) => {
   event.preventDefault();
   await register_user('cors');
});
