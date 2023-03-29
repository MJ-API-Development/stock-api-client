// APIKeys Script
const apiKeyEl = document.getElementById('api_key');
const showApiKeyBtn = document.getElementById('show_api_key');
const copyApiKeyBtn = document.getElementById('copy_api_key');

// Account Script
const updateAccountButton = document.getElementById('update_account_button');
const password = document.getElementById('password');
const first_name_dom = document.getElementById('first_name');
const second_name_dom = document.getElementById('second_name');
const surname_dom = document.getElementById('surname');
const cell_dom = document.getElementById('cell');
const email_dom = document.getElementById('email');


//

const subscription_details_dom = document.getElementById('subscription_details');
const endpoints_dom = document.getElementById('resources');

// Hide and Show API Key
showApiKeyBtn.addEventListener('click', function() {
  if (apiKeyEl.disabled) {
    apiKeyEl.disabled = false;
    apiKeyEl.type = 'text';
    showApiKeyBtn.innerHTML = '<i class="fa fa-eye-slash"></i>';
  } else {
    apiKeyEl.disabled = true;
    apiKeyEl.type = 'password';
    showApiKeyBtn.innerHTML = '<i class="fa fa-eye"></i>';
  }
});

copyApiKeyBtn.addEventListener('click', function() {
  apiKeyEl.focus();
  apiKeyEl.select();
  document.execCommand('copy');
  alert('API Key copied to clipboard');
});


updateAccountButton.addEventListener('click', async (e) => {
  e.preventDefault();

  const firstName = first_name_dom.value;
  const secondName = second_name_dom.value;
  const surname = surname_dom.value;
  const cell = cell_dom.value;
  const email = email_dom.value;

  let uuid = account_data.uuid;
  let baseUrl = settings.base_url;

  if (uuid !== undefined) {
    const url = `${baseUrl}/account/${uuid}`;
    let headers = { 'Content-type': 'application/json' };
    let body = { firstName, secondName, surname, cell, email };

    let response = await fetch(url, {
      method: 'PUT',
      headers: new Headers({...headers}),
      body: JSON.stringify(body),
      mode: 'cors',
      credentials: 'same-origin',
    });

    await updateAccountDetails(response);
  } else {
    await updateUI(account_data);
  }
});

self.addEventListener('load', async (e) => {
  /**
   * reloads the account data from the backend
   * @type {string}
   */
  const data = getAccountFromCookie();
  if (data !== null) {
    account_data = data;
    let uuid = account_data.uuid;
    let baseUrl = settings.base_url;

    const url = `${baseUrl}/account/${uuid}`;
    let headers = { 'Content-type': 'application/json' };

    let response = await fetch(new Request(url, {
      method: 'GET',
      headers: new Headers(headers),
      mode: 'cors',
      credentials: 'same-origin',
    }));
    // console.log("refresh response : " + await response.json());
    await refresh_account_details(response);

  } else {
    redirectToLogin();
  }
});


async function refresh_account_details(response){
    let json_data = await response.json();
    // Handle the JSON data
    console.dir(json_data)
    if (json_data.status === true){
        // let json_data = await response.json();
        //Setting the Global Account Data
        account_data = json_data.payload;
        // console.dir(account_data);
        setAccountCookie(account_data);
        first_name_dom.value = account_data.first_name;
        second_name_dom.value = account_data.second_name;
        surname_dom.value = account_data.surname;
        cell_dom.value = account_data.cell;
        email_dom.value = account_data.email;
        const {subscription} = account_data.apikey;
        apiKeyEl.value = account_data.apikey.api_key;
        await update_subscription_details(subscription);
    }
}


async function update_subscription_details(subscription){
  // console.log(subscription_details);
  // Updating the APIKey element on Intergace

  const planDetails = await getPlanDetails(subscription.plan_id, subscription.uuid);
  const plan_details = `${planDetails.name} -  $ ${planDetails.price} / Month, ${planDetails.maxRequests} Requests/Month`;
  const dateSubscribed = new Date(subscription.time_subscribed * 1000).toLocaleDateString();
  const monthlyRequestLimit = subscription.api_requests_balance;
  const maxRequests = planDetails.maxRequests;
  const monthlyPayment = subscription.subscription_id;
  const dateLastPayment = new Date().toLocaleDateString(); // this value needs to be obtained from the subscription data
  // const resourceList = planDetails.resources.map(resource => {
  //   const parts = resource.split('.');
  //   let displayText = parts.join(' > ');
  //   displayText = displayText.charAt(0).toUpperCase() + displayText.slice(1); // capitalize the first letter
  //   return `<li>${displayText}</li>`;
  // }).join('');
  //
  // // subscription_details_dom.innerHTML = `
  // //   <li class="list-group-item" > Plan Details: ${planType} </li>
  // //   <li class="list-group-item"> Date Subscribed: ${dateSubscribed} </li>
  // //   <li class="list-group-item"> Remaining Balance: ${monthlyRequestLimit} </li>
  // //  <li class="list-group-item"> Resources:</li>
  // //   <ul>
  // //     ${resourceList}
  // //   </ul>
  // //   <li class="list-group-item"> Rate Limiting: ${planDetails.rate_limit} </li>
  // //   <li class="list-group-item"> Monthly Payment: ${monthlyPayment} </li>
  // //   <li class="list-group-item"> Date Last Payment: ${dateLastPayment} </li>
  // // `;

  const resources = planDetails.resources.map(resource => {
    const resourceSplit = resource.split('.');
    const resourceType = resourceSplit[0].replace('_', ' ');
    const resourceAction = resourceSplit[1].replace('_', ' ');
    const resourceName = resourceSplit.slice(2).join(' ').replace('_', ' ');
    return {
      type: resourceType,
      action: resourceAction,
      name: resourceName
    };
  });

  const resourceListDOM = document.createElement('ul');
  resourceListDOM.classList.add('list-group');
  resourceListDOM.id = 'resource-list';

  resources.forEach(resource => {
    const resourceItem = document.createElement('li');
    resourceItem.classList.add('list-group-item');
    resourceItem.innerText = `${resource.type} - ${resource.action} - ${resource.name}`;
    resourceListDOM.appendChild(resourceItem);
  });

  // const resourcesButton = document.createElement('button');
  // resourcesButton.classList.add('btn', 'btn-primary');
  // resourcesButton.type = 'button';
  // resourcesButton.setAttribute('data-bs-toggle', 'collapse');
  // resourcesButton.setAttribute('data-bs-target', '#resource-list');
  // resourcesButton.setAttribute('aria-expanded', 'false');
  // resourcesButton.setAttribute('aria-controls', 'resource-list');
  // resourcesButton.innerText = 'Resources';

  const subscriptionDetailsListDOM = document.createElement('ul');
  subscriptionDetailsListDOM.classList.add('list-group', 'list-group-flush');
  subscriptionDetailsListDOM.appendChild(createListItem('Plan Details', plan_details ));
  subscriptionDetailsListDOM.appendChild(createListItem('Monthly Payment', `$${planDetails.price}`));
  subscriptionDetailsListDOM.appendChild(createNumberedElement('Rate Limit', planDetails.rate_limit));
  subscriptionDetailsListDOM.appendChild(createListItem('Date Subscribed', dateSubscribed));
  subscriptionDetailsListDOM.appendChild(createNumberedElement('Monthly Request Limit', maxRequests));
  subscriptionDetailsListDOM.appendChild(createNumberedElement('Requests Remaining', monthlyRequestLimit));
  // subscriptionDetailsListDOM.appendChild(createListItem('Monthly Payment', monthlyPayment));
  // subscriptionDetailsListDOM.appendChild(createListItem('Date Last Payment', dateLastPayment));
  // subscriptionDetailsListDOM.appendChild(resourcesButton);
  // subscriptionDetailsListDOM.appendChild(resourceListDOM);

  subscription_details_dom.innerHTML = '';
  subscription_details_dom.appendChild(subscriptionDetailsListDOM);
  endpoints_dom.innerHTML = '';
  endpoints_dom.appendChild(resourceListDOM);
}

function createListItem(label, value) {
  const item = document.createElement('li');
  item.classList.add('list-group-item');
  item.innerHTML = `<strong>${label}:</strong> <a><em>${value}</em></a>`;
  return item;
}
function createNumberedElement(tagName, number) {
  const value = new Intl.NumberFormat('en-US').format(number);
  const item = document.createElement('li');
  item.classList.add('list-group-item');
  item.innerHTML = `<strong>${tagName}:</strong> <a><em>${value}</em></a>`;
  return item;
}

async function getPlanDetails(plan_id, uuid) {
  const baseurl = settings.base_url;
  const url = `${baseurl}/plan-details/${plan_id}.${uuid}`;
  const headers = { 'Content-type': 'application/json' };
  const response = await fetch(new Request(url, {
      method: 'GET',
      headers: new Headers(headers),
      mode: 'cors',
      credentials: 'same-origin',
    }));

  const json = await response.json();
  const plan = json.payload;
  return {
    name: plan.plan_name,
    price: plan.Amount / 100,
    maxRequests: plan.plan_limit,
    limit_type: plan.plan_limit_type,
    rate_limit: plan.rate_limit,
    resources: plan.resources
  };
}



async function updateAccountDetails(response) {
  if (response.status === 200) {
    const json = await response.json();
    setAccountData(json.payload);
    updateUI(json.payload);
  } else {
    clearLocalStorage();
    redirectToLogin();
  }
}

function setAccountData(data) {
  /**
   * will set the account data on account data variable and also on the cookie
   */
  account_data = data;
  setAccountCookie(account_data);
}

function updateUI(data) {
  /**
   *  will update the account data form
   */
  first_name_dom.value = data.first_name;
  second_name_dom.value = data.second_name;
  surname_dom.value = data.surname;
  cell_dom.value = data.cell;
  email_dom.value = data.email;
}

function clearLocalStorage() {
  /**
   * @param {Object}
   * @type {{}}
   */
  account_data = {};
  setAccountCookie({})
}

function redirectToLogin() {
  /**
   *
   * @type {string}
   */
  window.location.href = "/login";
}
