self.addEventListener('fetch', event => {
  /**
   * This code sets up an event listener for the 'fetch' event, which is fired whenever the browser makes
   * a fetch request. When the event is triggered, it calls the handle_authentication() function to handle the
   * request.
   * The event.respondWith() method is used to respond to the fetch request with the result of the
   * handle_authentication() function. This ensures that the response is modified with the X-Auth-Token header
   * before it is returned to the browser.
   */
  event.respondWith(handle_authentication(event.request));
});

async function handle_authentication(request) {
  /**
   * This function takes a request object as input and adds an X-Auth-Token header to it. It then creates a
   * new request object with the modified headers and uses it to fetch the requested resource.
   * If the response includes an X-Auth-Token header, the token is extracted and saved in the cache
   * using the save_user_token() function. Finally, the response is returned.
   * @type {Cache}
   */
  const cache = await caches.open('eod');
  const token = await get_user_token(cache);

  const headers = new Headers(request.headers);
  headers.append('X-Auth-Token', token);

  const service_request = new Request(request, {
    headers: headers,
    mode: 'cors', // or 'no-cors' if you're requesting a resource from another origin
    cache: 'no-cache' // or 'no-cache' if you don't want the response to be cached
  });

  let response = await fetch(service_request);

  if (response) {
    if (response.ok && response.headers.get('X-Auth-Token')) {
      const token = response.headers.get('X-Auth-Token');
      await save_user_token(token, cache);
    }
  }

  return response;

}

async function get_user_token(cache) {
  /**
   * This function retrieves a user token from the specified cache (named "eod" in this case) and returns it.
   * If the token is not found in the cache, it returns an empty string.
   * @param {Cache} cache
   * @type {*}
   */
  const token = await cache.match('token');
  return token ? token.text() : '';
}

async function save_user_token(token, cache) {
  /**
   * This function saves the specified token in the specified cache (named "eod" in this case) using the put() method.
   * It returns a Promise that resolves when the token has been saved in the cache.
   */
  return cache.put('token', new Response(token));
}
