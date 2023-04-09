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
const popupTimeout = 45000; // 45 seconds

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
