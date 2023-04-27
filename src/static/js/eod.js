/**
 *
 *
 * This is a JavaScript code that defines two functions setAccountCookie and getAccountFromCookie and an event listener
 * for the load event.
 *
 * The setAccountCookie function takes an object account_data as input and sets a cookie with the name 'uuid' and the
 * value JSON.stringify(account_data). The function also adds a 'secure' flag to the cookie if the current page is
 * accessed via HTTPS protocol.
 *
 * The getAccountFromCookie function reads the cookie with the name 'uuid' and returns the parsed JSON object if it
 * exists, otherwise returns null.
 *
 * The load event listener checks if there is a uuid stored in the local storage, and if so, it calls the
 * refresh_account function with that uuid. If there is no uuid in the local storage, it sets an empty account_data
 * object as a cookie with the name 'uuid', and if the current page is the /account page, it redirects the user to
 * the /login page.
 *
 * The refresh_account function takes a uuid as input and sends an HTTP GET request to the URL
 * ${settings.base_url}/account/${uuid}. If the response status is 200, it sets the account_data object to the payload
 * property of the response JSON object and sets a cookie with the name 'uuid' and the value
 * JSON.stringify(account_data). The function also calls another function refresh_account_details with the response
 * object as a parameter, which is not defined in this code.
 *
 */


let account_data = {};

// Setting up host url
let url;
if (document.location.host.includes('eod-stock-api.local')){
    url = `http://eod-stock-api.local:8081`
}else{
    url = 'https://eod-stock-api.site'
}

let settings = {
    live_base_url: 'https://eod-stock-api.site',
    base_url: url
}

// Function to set a cookie with account data
function setAccountCookie(account_data) {
    /**
     *  setAccountCookie for authentication purposes
     * @type {string}
     */
  const cookieName = 'uuid';
  const cookieValue = JSON.stringify(account_data);
  const secureFlag = window.location.protocol === 'https:' ? '; secure' : '';
  document.cookie = `${cookieName}=${cookieValue}${secureFlag}; path=/; SameSite=Strict`;
}

// Function to read the cookie and get the account data
function getAccountFromCookie() {
  const cookieName = 'uuid';
  const cookieValue = `; ${document.cookie}`;
  const parts = cookieValue.split(`; ${cookieName}=`);
  if (parts.length === 2) {
      const cookie_data = parts.pop().split(';').shift();
      return JSON.parse(cookie_data);
  }
  return null;
}

function canRegisterServiceWorker() {
    /** checks if its safe to instance a service worker */
  return (window.location.protocol === 'https:' || window.location.protocol === 'http:') && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
}

// Register the service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    if (canRegisterServiceWorker()) {
        navigator.serviceWorker.register('/sw.js').then(function (registration) {
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }, function (err) {
            console.log('ServiceWorker registration failed: ', err);
        });
    }
  });
}


