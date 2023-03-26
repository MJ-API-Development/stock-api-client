function validateName(name) {
  const regex = /^[a-zA-Z]{1,32}( [a-zA-Z]{1,32}){0,2}$/;
  return regex.test(name);
}
function validateEmail(email) {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(email);
}
function validateCellNumber(cell) {
  const regex = /^\+(?:[0-9] ?){6,14}[0-9]$/;
  return regex.test(cell);
}
function validatePassword(password) {
    const regex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/
    return regex.test(password);
}

// Function to set a cookie with account data
function setAccountCookie(account_data) {
  const cookieName = 'account_data';
  const cookieValue = JSON.stringify(account_data);
  const secureFlag = window.location.protocol === 'https:' ? '; secure' : '';
  document.cookie = `${cookieName}=${cookieValue}${secureFlag}; path=/; SameSite=Strict`;
}

// Function to read the cookie and get the account data
function getAccountFromCookie() {
  const cookieName = 'account_data';
  const cookieValue = `; ${document.cookie}`;
  const parts = cookieValue.split(`; ${cookieName}=`);
  if (parts.length === 2) {
    return JSON.parse(parts.pop().split(';').shift());
  }
  return null;
}


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


async function login (event) {
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
        localStorage.setItem('uuid', JSON.stringify(account_data));
        window.location.href = `/account`;
    }else{
        account_data = {};
        localStorage.clear();
        message_elem.innerHTML = data.message;
    }
}



// get the input fields
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const cellInput = document.getElementById('cell');
const passwordInput = document.getElementById('r_password');



// Attach a validation function to the form's submit event
const registrationForm = document.getElementById('registration_form');
const registerButton = document.getElementById('submit_registration');


const submitForm = async (event, mode) => {
    event.preventDefault();
    const name = nameInput.value;
    const email = emailInput.value;
    const cell = cellInput.value;
    const password = password_input.value;
    console.log("submitting registration form");
    console.log(registrationForm.action);

    if (!validateName(name)){
        alert("Names or Names are invalid");
        return;
    }
    if (!validateEmail(email)){
        alert("Email should at least be a valid email address");
        return;
    }
    if (!validateCellNumber(cell)){
        alert("Cell number should contain international codes");
        return;
    }
    if (!validatePassword(password)){
        alert("Try to meet our minimum password complexity requirements");
        return;
    }

    const request = new Request(registrationForm.action, {
        method: registrationForm.method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name, email, cell, password }),
        mode: mode,
        credentials: "same-origin",
    });

    console.log(request);
    let response = await fetch(request);
    if (response.status !== 201) {
        const data = response.json();
        if (data.status && data.account && data.account.uuid) {
            // TODO - add to account details
        }
    } else {
        console.log(response.statusText)
    }
};

// Attach the submitForm function to the form's submit event
registrationForm.addEventListener('submit', async event => {
   await submitForm(event, 'cors');
});

// Attach the submitForm function to the register button's click event
registerButton.addEventListener('click', async (event) => {
   await submitForm(event, 'cors');
});
