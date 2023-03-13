


    // APIKeys Script
    let apiKeyEl = document.getElementById('api_key');
    let showApiKeyBtn = document.getElementById('show_api_key');
    let copyApiKeyBtn = document.getElementById('copy_api_key');

    // Hide and Show API Key
    showApiKeyBtn.addEventListener('click', function() {
        if (apiKeyEl.disabled) {
            apiKeyEl.disabled = false;
            apiKeyEl.type = "text"
            showApiKeyBtn.innerHTML = '<i class="fa fa-eye-slash"></i>';
        } else {
            apiKeyEl.disabled = true;
            apiKeyEl.type = "password"
            showApiKeyBtn.innerHTML = '<i class="fa fa-eye"></i>';
        }

    });

    copyApiKeyBtn.addEventListener('click', function() {
        apiKeyEl.focus();
        apiKeyEl.select();
        document.execCommand('copy');
        alert('API Key copied to clipboard');
    });


    //Account Script
    let update_account_button = document.getElementById('update_account_button');
    let password = document.getElementById('password');

    // Update Account Personal Data
    update_account_button.addEventListener('click', async (e) => {
        e.preventDefault();

        const first_name_dom = document.getElementById('first_name');
        const second_name_dom = document.getElementById("second_name");
        const surname_dom = document.getElementById('surname');
        const cell_dom = document.getElementById('cell');
        const email_dom = document.getElementById('email');

        const first_name = first_name_dom.value;
        const second_name = second_name_dom.value;
        const surname = surname_dom.value;
        const cell = cell_dom.value;
        const email = email_dom.value;

        let uuid = account_data.uuid;
        let base_url = settings.base_url;

        const url = `${base_url}/account/${uuid}`;
        let headers = {'Content-type': 'application/json'}
        let body = {first_name, second_name, surname, cell, email};
        alert(`${base_url}`);
        let response = await fetch(new Request(url, {
            method: "put",
            headers: new Headers({...headers}),
            body: JSON.stringify(body),
            mode: "cors",
            credentials: "same-origin",

        }));

        //Updates Account Data depending on the return status
        if (response.status === 201){
            // request successfully updated account details
            let json_data = await response.json();
            //Setting the Global Account Data
            account_data = response.payload;
        }else{account_data = {}}

        //refreshing data
        first_name_dom.value = account_data.first_name;
        second_name_dom.value = account_data.second_name;
        surname_dom.value = account_data.surname;
        cell_dom.value = account_data.cell;
        email_dom.value = account_data.email;
    });
