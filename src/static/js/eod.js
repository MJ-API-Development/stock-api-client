


let account_data = {};

//this event will trigger on every page load
document.addEventListener('load', async (e) => {
    let storage_item = localStorage.getItem('uuid');
    // Data is available therefore lets try and refresh the data
    if (storage_item !== null){
        let data = JSON.parse(storage_item);
         await refresh_account(data.uuid);
    }else {
        if (account_data !== {}) {
            await refresh_account(account_data.uuid);
        }
    }
})


let settings = {
    live_base_url: 'https://client.eod-stock-api.site',
    base_url: 'http://localhost:8081'
}


async function refresh_account(uuid) {

    let url = `${settings.base_url}/account/${uuid}`;
    let request = new Request(url, {
        method: 'GET',
        headers: new Headers({"Content-Type": "application/json"}),
        mode: "cors",
        credentials: "same-origin"
    });

    let response = await fetch(request);

    if (response.status === 200) {
        const json_data = await response.json();
        account_data = json_data.payload;
        localStorage.setItem('uuid', JSON.stringify(account_data))
    } else {
        account_data = {}
        localStorage.clear();

    }

}