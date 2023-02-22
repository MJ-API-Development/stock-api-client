

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
        .then(response => response.json())
        .then(data => {
            if (data.status && data.account && data.account.uuid) {
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

// user registration form
register_button.addEventListener('click', (event) => {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('r_password').value;
    const form = document.getElementById('registration_form');

    fetch(form.action, {
        method: form.method,
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
})