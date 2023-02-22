

const form = document.getElementById('auth_form');
const username_input = document.getElementById('username');
const password_input = document.getElementById('password');

const submit_btn = document.getElementById('submit_login');
const message_elem = document.getElementById('message');
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
            if (data.status){
                document.redirect('/account/{data.account.uuid}')
            }
            // failed to login show the user a response message instead
            message_elem.innerHTML = data.message;
    })

}
form.addEventListener('submit', (event) => {
    login(event);
});
submit_btn.addEventListener( 'click', (event) => {
    login(event);
});

