    var apiKeyEl = document.getElementById('api_key');
    var showApiKeyBtn = document.getElementById('show_api_key');
    var copyApiKeyBtn = document.getElementById('copy_api_key');

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