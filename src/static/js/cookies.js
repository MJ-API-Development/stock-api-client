
const cookieName = 'cookie-accepted';

document.addEventListener('load', async () => {
    if (document.cookie.indexOf("cookie-accepted=true") !== -1) {
      // Cookie has been accepted, don't display pop-up
      document.getElementById("cookie-popup").style.display = "none";
    } else {
      // Cookie has not been accepted, display pop-up
      document.getElementById("cookie-popup").style.display = "block";
    }
});

function removePopup() {
    const popup = document.getElementById("cookie-popup");
    if (popup) {
      popup.remove();
      // set a cookie to remember that the user has accepted the cookie policy
      setCookie(cookieName, 'true', 365);
    }
}

//    will ensure that the popup is removed if not clicked and an assumption that the cookie is accepted
(function() {
  // set the time in milliseconds
  const popupTimeout = 30000; // 30 seconds
  // remove the cookie pop-up after a certain amount of time
  setTimeout(removePopup, popupTimeout);
})();



(function() {
  // Get the cookie popup element
  const cookiePopup = document.getElementById('cookie-popup');
  // Get the cookie accept button
  const cookieAccept = document.getElementById('cookie-accept');
  // Check if the cookie is set
  if (getCookie(cookieName) !== true) {
      // Show the cookie popup
      cookiePopup.style.display = 'none';
  } else {
      cookiePopup.style.display = 'block';
  }
  // Add a click event listener to the cookie accept button
  cookieAccept.addEventListener('click', function() {
      // Set the cookie to expire in 365 days
      setCookie(cookieName, 'true', 365);
      // Hide the cookie popup
      cookiePopup.style.display = 'none';
  });

})();

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
