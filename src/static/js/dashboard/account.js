// APIKeys Script
const apiKeyEl = document.getElementById('api_key');
const showApiKeyBtn = document.getElementById('show_api_key');
const copyApiKeyBtn = document.getElementById('copy_api_key');

let account_data = {};
// Function to set a cookie with account data

let settings = {
    live_base_url: 'https://client.eod-stock-api.site',
    base_url: 'http://localhost:8081'
}

// Account Script
const updateAccountButton = document.getElementById('update_account_button');
const password = document.getElementById('password');
const first_name_dom = document.getElementById('first_name');
const second_name_dom = document.getElementById('second_name');
const surname_dom = document.getElementById('surname');
const cell_dom = document.getElementById('cell');
const email_dom = document.getElementById('email');

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
  const data = localStorage.getItem('uuid');
  if (data !== null) {
    account_data = JSON.parse(data);
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
    console.log(json_data)
    if (json_data.status === true){
        // let json_data = await response.json();
        //Setting the Global Account Data
        account_data = json_data.payload;
        localStorage.setItem('uuid', JSON.stringify(account_data));
        first_name_dom.value = account_data.first_name;
        second_name_dom.value = account_data.second_name;
        surname_dom.value = account_data.surname;
        cell_dom.value = account_data.cell;
        email_dom.value = account_data.email;
    }
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
  setAccountCookie(account_data)
}

function redirectToLogin() {
  /**
   *
   * @type {string}
   */
  window.location.href = "/login";
}
