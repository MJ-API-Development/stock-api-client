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

//this event will trigger on every page load
// self.addEventListener('load', async () => {
//     /**
//      * this event will trigger on every page load
//      * @type {string}
//      */
//         let storage_item = localStorage.getItem('uuid');
//         console.log(`storage_item: ${storage_item}`);
//         if (storage_item !== null){
//             let data = JSON.parse(storage_item);
//             console.log(data);
//             await refresh_account(data.uuid);
//         } else {
//             console.log("storage not found");
//             account_data = {};
//             setAccountCookie(account_data);
//             console.log(`window location : ${window.location}`);
//             if (window.location.pathname === '/account'){
//                 window.location = '/login'
//             }
//         }
// });



//
// async function refresh_account(uuid) {
//     /**
//      * will refresh account details when loading the page
//      * @type {string}
//      */
//
//     let url = `${settings.base_url}/account/${uuid}`;
//     let request = new Request(url, {
//         method: 'GET',
//         headers: new Headers({"Content-Type": "application/json"}),
//         mode: "cors",
//         credentials: "same-origin"
//     });
//
//     let response = await fetch(request);
//
//     if (response.status === 200) {
//
//         const json_data = await response.json();
//         account_data = json_data.payload;
//         setAccountCookie(account_data);
//         await refresh_account_details(response);
//
//     }
// }
self.addEventListener('load', async () => {
    if (document.cookie.indexOf("cookie-accepted=true") !== -1) {
      // Cookie has been accepted, don't display pop-up
      document.getElementById("cookie-popup").style.display = "none";
    } else {
      // Cookie has not been accepted, display pop-up
      document.getElementById("cookie-popup").style.display = "block";
    }

})

// set the time in milliseconds
const popupTimeout = 5000; // 5 seconds

// function to remove the cookie pop-up
function removePopup() {
  const popup = document.getElementById("cookie-popup");
  if (popup) {
    popup.remove();
    // set a cookie to remember that the user has accepted the cookie policy
    document.cookie = "cookie-accepted=true; path=/";
  }
}

// remove the cookie pop-up after a certain amount of time
setTimeout(removePopup, popupTimeout);

// Get the cookie popup element
const cookiePopup = document.getElementById('cookie-popup');
// Get the cookie accept button
const cookieAccept = document.getElementById('cookie-accept');

// Check if the cookie is set
if (getCookie('cookie-accepted') !== 'true') {
    // Show the cookie popup
    cookiePopup.style.display = 'none';
}

// Add a click event listener to the cookie accept button
cookieAccept.addEventListener('click', function() {
    // Set the cookie to expire in 365 days
    setCookie('cookie-accepted', 'true', 365);

    // Hide the cookie popup
    cookiePopup.style.display = 'block';
});
// Set a cookie with the given name, value and number of days until it expires
function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = 'expires=' + date.toUTCString();
    document.cookie = name + '=' + value + ';' + expires + ';path=/';
}

// Get the value of the cookie with the given name
function getCookie(name) {
    const cookieName = name + '=';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.indexOf(cookieName) === 0) {
            return cookie.substring(cookieName.length, cookie.length);
        }
    }
    return '';
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

