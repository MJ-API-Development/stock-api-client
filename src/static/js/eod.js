


let account_data = {};

//this event will trigger on every page load
self.addEventListener('load', async () => {
        let storage_item = localStorage.getItem('uuid');
        console.log(`storage_item: ${storage_item}`);
        if (storage_item !== null){
            let data = JSON.parse(storage_item);
            console.log(data);
            await refresh_account(data.uuid);
        } else {
            console.log("storage not found")
            account_data = {}
            localStorage.clear();
            console.log(`window location : ${window.location}`);
            if (window.location.pathname === '/account'){
                window.location = '/login'
            }
        }
});



let settings = {
    live_base_url: 'https://client.eod-stock-api.site',
    base_url: 'http://localhost:8081'
}


async function refresh_account(uuid) {

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
        localStorage.setItem('uuid', JSON.stringify(account_data));
        await refresh_account_details(response);

    } else {
        account_data = {}
        localStorage.clear();
        if (window.location.pathname === '/account'){
            window.location = '/login'
        }

    }

}