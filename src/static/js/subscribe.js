// noinspection JSUnresolvedVariable

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

const basic_id = document.getElementById('basic_id');
const professional_id = document.getElementById('professional_id');
const business_id = document.getElementById('business_id');
const enterprise_id = document.getElementById('enterprise_id');
const paypal_id = document.getElementById('paypal_id');

let plan_data;

self.addEventListener('load', async (e) => {
  const response = await fetch(`/plans-all`, {

        method: 'GET',
        headers:  {'Content-Type': 'application/json'},
        mode: 'cors',
        credentials: "same-origin"
  });

  const json_data = await response.json();
  const plan_list = json_data.payload;
  await updatePlanIOs(plan_list);
  await updatePlanButtons(plan_list);
  plan_data = plan_list;
})

async function updatePlanIOs(plan_list){
  /**
   * Update Plan Id's
   */
  basic_id.value = getPlanId("BASIC", plan_list);
    professional_id.value = getPlanId("PROFESSIONAL", plan_list);
    business_id.value = getPlanId("BUSINESS", plan_list);
    enterprise_id.value = getPlanId("ENTERPRISE", plan_list);
}

async function updatePlanButtons(plan_list){
  /**
   * Will update the front page interface related to plans
   *
   */

    basic_plan_button.innerHTML = `
    <i class="fa fa-dollar">  </i> ${getPlanAmount('BASIC', plan_list )}.00 /Month
    `
    professional_plan_button.innerHTML = `
      <i class="fa fa-dollar">  </i> ${getPlanAmount('PROFESSIONAL', plan_list )}.00 /Month
    `
    business_plan_button.innerHTML = `
    <i class="fa fa-dollar">  </i> ${getPlanAmount('BUSINESS', plan_list )}.00 /Month
    `
    enterprise_plan_button.innerHTML = `
    <i class="fa fa-dollar">  </i> ${getPlanAmount('ENTERPRISE', plan_list )}.00 /Month
    `
}

function getPlanId(planName, plans) {
  for (let i = 0; i < plans.length; i++) {
    if (plans[i].plan_name.toUpperCase() === planName.toUpperCase()) {
      return plans[i].plan_id;
    }
  }
  return null; // return null if no match is found
}

function getPlanAmount(planName, plans) {
  for (let i = 0; i < plans.length; i++) {
    if (plans[i].plan_name.toUpperCase() === planName.toUpperCase()) {
      return plans[i].Amount;
    }
  }
  return null; // return null if no match is found
}


basic_plan_button.addEventListener('click', async (event) => {
  event.preventDefault();
  // await updatePlanIOs(plan_data);
  await start_process_subscription(basic_id.value);
});

professional_plan_button.addEventListener('click', async (event) => {
  event.preventDefault();
  // await updatePlanIOs(plan_data);
  await start_process_subscription(professional_id.value);

});

business_plan_button.addEventListener('click', async (event) => {
  event.preventDefault();
  // await updatePlanIOs(plan_data);
  await start_process_subscription(business_id.value);
});

enterprise_plan_button.addEventListener('click', async (event) => {
  event.preventDefault();
  // await updatePlanIOs(plan_data);
  await start_process_subscription(enterprise_id.value);
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
  window.location.href = `/plan-subscription/${plan_id}.${uuid}`;
}

