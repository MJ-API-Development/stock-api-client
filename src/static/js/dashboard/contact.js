// Get the form and its elements
const form = document.getElementById('contact_form');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const messageInput = document.getElementById('message');
const submitButton = document.querySelector('button[type="submit"]');
const resetButton = document.querySelector('button[type="reset"]');
const success_message = document.getElementById('success_message');

// Add an event listener for when the form is submitted
form.addEventListener('submit', (event) => {
  // Prevent the default form submission behavior
  event.preventDefault();

  // Get the values of the input fields
  const name = nameInput.value;
  const email = emailInput.value;
  const message = messageInput.value;


  // Send the form data to the server using Fetch API
  fetch(form.action, {
    method: form.method,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: name,
      email: email,
      message: message
    })
  })
  .then(response => response.json())
  .then(data => {
    // Handle the server response
    form.reset();
    console.log(data);
    success_message.innerHTML = data.message;
  })
  .catch(error => {
    console.error(error);
  });
});

// Add an event listener for when the reset button is clicked
resetButton.addEventListener('click', (event) => {
  // Reset the form
  form.reset();
});
