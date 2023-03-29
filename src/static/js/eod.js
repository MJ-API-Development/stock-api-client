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

let settings = {
    live_base_url: 'https://client.eod-stock-api.site',
    base_url: 'https://client.eod-stock-api.site'
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
  sessionStorage.setItem('uuid', JSON.stringify(account_data));
}

// Function to read the cookie and get the account data
function getAccountFromCookie() {
  const cookieName = 'uuid';
  const cookieValue = `; ${document.cookie}`;
  const parts = cookieValue.split(`; ${cookieName}=`);
  if (parts.length === 2) {
      const session_data = sessionStorage.getItem('uuid');
      const cookie_data = parts.pop().split(';').shift();
      if (session_data){
          return JSON.parse(session_data);
      }
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