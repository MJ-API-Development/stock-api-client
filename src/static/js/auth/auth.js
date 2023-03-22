

const form = document.getElementById('auth_form');
const username_input = document.getElementById('username');
const password_input = document.getElementById('password');

const submit_btn = document.getElementById('submit_login');
const message_elem = document.getElementById('message');

//register new user button
const register_button = document.getElementById('submit_registration')

async function login (event) {
    event.preventDefault();
    const username = username_input.value;
    const password = password_input.value;

    // send form data
    const response  = await fetch(form.action, {
        method: form.method,
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

form.addEventListener('submit', async (event) => {
   await login(event);
});
submit_btn.addEventListener( 'click', async (event) => {
    await login(event);
});


// create a function to validate a single field
function validateField(value, rules) {
  if (rules.required && !value.trim()) {
    return 'This field is required';
  }

  if (rules.minLength && value.length < rules.minLength) {
    return `This field must be at least ${rules.minLength} characters`;
  }

  if (rules.maxLength && value.length > rules.maxLength) {
    return `This field must be no more than ${rules.maxLength} characters`;
  }

  if (rules.email && !isValidEmail(value)) {
    return 'Please enter a valid email address';
  }

  return null;
}

// create a function to validate all fields
function validateForm() {
  let isValid = true;

  // iterate over the validation rules and validate each field
  Object.keys(validationRules).forEach(fieldName => {
    const value = document.getElementById(fieldName).value;
    const rules = validationRules[fieldName];
    const errorMessage = validateField(value, rules);
    const errorElement = document.getElementById(`${fieldName}_error`);

    if (errorMessage) {
      errorElement.innerHTML = errorMessage;
      isValid = false;
    } else {
      errorElement.innerHTML = '';
    }
  });

  return isValid;
}

// get the input fields
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('r_password');

// create an object to store the validation rules for each field
const validationRules = {
  name: {
    required: true,
    minLength: 2,
    maxLength: 50
  },
  email: {
    required: true,
    email: true
  },
  password: {
    required: true,
    minLength: 6,
    maxLength: 50
  }
};



/** TODO refactor the code to create only one Method for both event listeners **/
// attach a validation function to the form's submit event
const registrationForm = document.getElementById('registration_form');

registrationForm.addEventListener('submit', event => {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const cell = document.getElementById('cell').value;
    const password = document.getElementById('r_password').value;
    console.log("submitting registration form");
    console.log(registrationForm.action);

    const request = new Request(registrationForm.action,{
         method: registrationForm.method,
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify({ name, email, cell, password}),
        mode: "no-cors",
        credentials: "same-origin",
    });

    console.log(request);
    let response =  fetch(request);
    if (response.status !== 201){
        data = response.json();
        if (data.status && data.account && data.account.uuid) {

        }
    }else{
        console.log(response.statusText)
    }
});

// user registration form
register_button.addEventListener('click', async (event) => {
    /**
     * Will register a new user with the just name and email
     * User will then need to update their details on Account
     */
    event.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const cell = document.getElementById('cell').value;
    const password = document.getElementById('r_password').value;
    console.log("submitting registration form");
    console.log(registrationForm.action);

    const request = new Request(registrationForm.action,{
         method: registrationForm.method,
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify({ name, email, cell, password}),
        mode: "cors",
        credentials: "same-origin",
    });

    console.log(request);
    let response = await fetch(request);
    if (response.status !== 201){
        const data = response.json();
        if (data.status && data.account && data.account.uuid) {
        //    TODO - add to account details
        }
    }else{
        console.log(response.statusText)
    }
});
