/**
 *
 *make a request to an endpoint which will retrieve the status of all servers
 *
 *
 */
self.addEventListener('load', async (e) => {

    const request = new Request({
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
    });

    console.log('will be fetching data');

    let response = await fetch("/status/", request);
    const data = await response.json();
    console.log(`fetched data : ${data}`);

    if (data.status && data.payload){
        const server_status = data.payload.server_status;
        document.getElementById('server_1').innerHTML = server_status.API_Master;
        document.getElementById('server_2').innerHTML = server_status.API_Slave;
        document.getElementById('gateway').innerHTML = server_status.Gateway;
        alert('status updated')
    }
})