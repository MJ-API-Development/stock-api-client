


let account_data = {};

let settings = {
    live_base_url: 'https://client.eod-stock-api.site',
    base_url: 'http://localhost:8081'
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
    return JSON.parse(parts.pop().split(';').shift());
  }
  return null;
}

//this event will trigger on every page load
self.addEventListener('load', async () => {
    /**
     * this event will trigger on every page load
     * @type {string}
     */
        let storage_item = localStorage.getItem('uuid');
        console.log(`storage_item: ${storage_item}`);
        if (storage_item !== null){
            let data = JSON.parse(storage_item);
            console.log(data);
            await refresh_account(data.uuid);
        } else {
            console.log("storage not found");
            account_data = {};
            setAccountCookie(account_data);
            console.log(`window location : ${window.location}`);
            if (window.location.pathname === '/account'){
                window.location = '/login'
            }
        }
});




async function refresh_account(uuid) {
    /**
     * will refresh account details when loading the page
     * @type {string}
     */

    let url = `${settings.base_url}/account/${uuid}`;
    let request = new Request(url, {
        method: 'GET',
        headers: new Headers({"Content-Type": "application/json"}),
        mode: "no-cors",
        credentials: "same-origin"
    });

    let response = await fetch(request);

    if (response.status === 200) {

        const json_data = await response.json();
        account_data = json_data.payload;
        setAccountCookie(account_data);
        await refresh_account_details(response);

    }
}