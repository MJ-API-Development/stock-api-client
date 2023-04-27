// APIKeys Script
// noinspection JSUnresolvedVariable

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

const update_api_key_button = document.getElementById('update_api_key_button');

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
/** Copy API Key  **/
copyApiKeyBtn.addEventListener('click', function() {
  apiKeyEl.focus();
  apiKeyEl.select();
  document.execCommand('copy');
  alert('API Key copied to clipboard');
});

/**
 * adding event listener to update account details
 */
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


/**
 * Update API KeY Button
 */
/**
 * Update API KeY Button
 */
(function() {
  if (update_api_key_button) {
    update_api_key_button.addEventListener('click', async (e) => {
      e.preventDefault();
      const path = '/update-api-key';
      const request = new Request(path, {
        method: "POST",
        body: JSON.stringify(account_data),
        headers: new Headers({'Content-type': 'application/json'}),
        mode: 'cors',
        credentials: 'same-origin',
      });
      const response = await fetch(request);
      if (response.headers.get('Content-type') === 'application/json') {
        const payload = await response.json();
        document.getElementById('api_key').innerHTML = payload.api_key;
      }
    });
  }
})();

/**
 * Adding load event listener to fetch account data
 */
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
    console.log(url);
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

  subscription_details_dom.innerHTML = '<div> </div>';
  subscription_details_dom.appendChild(subscriptionDetailsListDOM);
  endpoints_dom.innerHTML = '<div> </div>';
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
    price: plan.Amount,
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


const plansSelect = document.getElementById('plans_select');

// Function to fetch plans and populate the select element
async function populatePlansSelect() {
  try {
    const baseurl = settings.base_url;
    const url = `${baseurl}/plans-all`;
    const headers = { 'Content-type': 'application/json' };

    const response = await fetch(new Request(url, {
      method: 'GET',
      headers: new Headers(headers),
      mode: 'cors',
      credentials: 'same-origin',
    }));
    if ((response.headers.has('Content-type')) && (response.headers['Content-type'] === 'application/json')){
          const plans = await response.json();
          // Clear existing options
          plansSelect.innerHTML = '<option> </option>';
          // Create new option elements for each plan
          plans.forEach(plan => {
            const option = document.createElement('option');
            option.textContent = `${plan.plan_name} - $ ${plan.price}`;
            plansSelect.appendChild(option);
          });
    }else{

    }
  } catch (error) {
    console.error(error);
  }
}

// Call function to populate select element on page load
window.addEventListener('load', populatePlansSelect);
