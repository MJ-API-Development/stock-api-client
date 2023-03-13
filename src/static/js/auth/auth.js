

const form = document.getElementById('auth_form');
const username_input = document.getElementById('username');
const password_input = document.getElementById('password');

const submit_btn = document.getElementById('submit_login');
const message_elem = document.getElementById('message');

//register new user button
const register_button = document.getElementById('submit_registration')

function login (event) {
    event.preventDefault();

    const username = username_input.value;
    const password = password_input.value;

    // send form data

    fetch(form.action, {
        method: form.method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username, password
        })
    })
        .then(response => {
            console.log(response);
            return response.json();
        }).then(data => {

            if (data.status && data.account && data.account.uuid) {
                //Setting The Global Account Data Variable
                account_data = data.account;
                window.location.href = '/account/' + data.account.uuid;
            } else {
                message_elem.innerHTML = data.message;
            }
  });
}
form.addEventListener('submit', (event) => {
    login(event);
});
submit_btn.addEventListener( 'click', (event) => {
    login(event);
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

// attach a validation function to the form's submit event
const registrationForm = document.getElementById('registration_form');

registrationForm.addEventListener('submit', event => {
  event.preventDefault();

  if (validateForm()) {
    // form is valid, submit it
    const name = nameInput.value;
    const email = emailInput.value;
    const password = passwordInput.value;

    fetch(registrationForm.action, {
      method: registrationForm.method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name, email, password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status && data.account && data.account.uuid) {
        window.location.href = '/account/' + data.account.uuid;
      } else {
        message_elem.innerHTML = data.message;
      }
    });
  }
});

// user registration form
register_button.addEventListener('click', (event) => {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('r_password').value;
    alert(" working >>>");
    fetch(registrationForm.action, {
        method: registrationForm.method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({name, email, password})
    }).then(response => response.json()).then(data => {
        if (data.status){
            if (data.status && data.account && data.account.uuid) {
                window.location.href = '/account/' + data.account.uuid;
            } else {
                message_elem.innerHTML = data.message;
            }
        }
    })
});
