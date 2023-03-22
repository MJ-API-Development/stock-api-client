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
  const data = localStorage.getItem('uuid');
  console.log("data : " + data);
  console.log("data saved");
  if (data !== null) {
    account_data = JSON.parse(data);
    console.log("parsed data: " + account_data);
    let uuid = account_data.uuid;
    let baseUrl = settings.base_url;

    const url = `${baseUrl}/account/${uuid}`;
    let headers = { 'Content-type': 'application/json' };

    let response = await fetch(new Request(url, {
      method: 'GET',
      headers: new Headers({...headers}),
      mode: 'no-cors',
      credentials: 'same-origin',
    }));

    await refresh_account_details(response);

  } else {
    redirectToLogin();
  }
});


async function refresh_account_details(response){
    if (response === 200){
        let json_data = await response.json();
        //Setting the Global Account Data
        account_data = response.payload;
        console.log(account_data);
        localStorage.setItem('uuid', JSON.stringify(account_data));
        first_name_dom.value = account_data.first_name;
        second_name_dom.value = account_data.second_name;
        surname_dom.value = account_data.surname;
        cell_dom.value = account_data.cell;
        email_dom.value = account_data.email;
    }
}

async function updateAccountDetails(response) {
  if (response.ok) {
    const json = await response.json();
    localStorage.setItem('uuid', json.uuid);
    setAccountData(json);
    updateUI(json);
  } else {
    clearLocalStorage();
    redirectToLogin();
  }
}

function setAccountData(data) {
  account_data = data;
}

function updateUI(data) {
  first_name_dom.value = data.first_name;
  second_name_dom.value = data.second_name;
  surname_dom.value = data.surname;
  cell_dom.value = data.cell;
  email_dom.value = data.email;
}

function clearLocalStorage() {
  account_data = {};
  localStorage.clear();
}

function redirectToLogin() {
  window.location.href = "/login";
}
