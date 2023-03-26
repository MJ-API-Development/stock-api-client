/**
 * Subscribe
 *
 * @type {HTMLElement}
 */

// Define variables for subscription form elements
const basic_plan_button = document.getElementById('basic_plan');
const professional_plan_button = document.getElementById('professional_plan');
const business_plan_button = document.getElementById('business_plan');
const enterprise_plan_button = document.getElementById('enterprise_plan');


basic_plan_button.addEventListener('click', async (event) => {
  event.preventDefault();
  const plan_type = "basic_plan";
  await start_process_subscription(plan_type);

});

professional_plan_button.addEventListener('click', async (event) => {
  event.preventDefault();
  const plan_type = "professional_plan";
  await start_process_subscription(plan_type);

});

business_plan_button.addEventListener('click', async (event) => {
  event.preventDefault();
  const plan_type = "business_plan";
  await start_process_subscription(plan_type);

});

enterprise_plan_button.addEventListener('click', async (event) => {
  event.preventDefault();
  const plan_type = "enterprise_plan";
  await start_process_subscription(plan_type);

});

// Add event listener for subscription form submission
async function start_process_subscription(plan) {
  // Prevent form submission from reloading the page
  account_data = getAccountFromCookie();
  if (!account_data){
    window.location.href = '/login';
  }else{
   await processSubscription(account_data, plan);
  }
}

// Function to process user subscription
async function processSubscription(account_data, plan) {
  // Check if user has an existing account
  const uuid = account_data.uuid;
  const account_exist = await checkExistingAccount(uuid);

  if (account_exist) {
    // If user has an existing account, proceed to subscription form
    await showSubscriptionForm(plan, uuid);
  } else {
    // If user doesn't have an existing account, prompt them to create one
    const should_create_account = confirm('You don\'t have an existing account. Would you like to create one?');
    if (should_create_account) {
      // Call function to create new user account
      window.location.href = '/login';
    } else {
      // If user doesn't want to create an account, redirect them to home page
      window.location.href = '/';
    }
  }
}

// Function to check if user has an existing account
async function checkExistingAccount(uuid) {
  // Check if account with the specified UUID exists
  const response = await fetch(`/account/${uuid}`, {
    method: 'GET',
    headers:  {'Content-Type': 'application/json'},
    mode: 'cors',
    credentials: "same-origin"
  });

  // If response status is 200, account exists
  if (response.status === 200) {
    return true;
  }
  // If response status is not 200, account does not exist
  return false;
}

// Function to show subscription form
function showSubscriptionForm(plan_id, uuid) {
  // Show subscription form and hide login form
  console.log(`will now create plan : ${plan_id}`);
  console.log(`uuid : ${uuid}`);
  window.location.href = `/plan-subscription/${plan_id}`;


}

