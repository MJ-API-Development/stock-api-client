


let account_data = {};

document.addEventListener('load', async (e) => {
    // TODO - read data from localstorage
    // TODO if user data is found store the data on account_data;

    let data = localStorage.getItem('uuid');
    if (data !== null){
        account_data = data
    }
});
