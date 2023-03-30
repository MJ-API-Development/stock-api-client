self.addEventListener('fetch', event => {
  event.respondWith(addAuthHeader(event.request));
});

async function addAuthHeader(request) {
  const token = await getUserToken();

  const headers = new Headers(request.headers);
  headers.append('X-Auth-Token', token);

  const modifiedRequest = new Request(request, {
    headers: headers,
    mode: 'cors', // or 'no-cors' if you're requesting a resource from another origin
    cache: 'default' // or 'no-cache' if you don't want the response to be cached
  });

  const cache = await caches.open('eod');
  let response = await fetch(modifiedRequest);

  if (response) {
    if (response.ok && response.headers.get('X-Auth-Token')) {
      const token = response.headers.get('X-Auth-Token');
      await saveUserToken(token);
    }
  }
  return response;
}

async function getUserToken() {
  const cache = await caches.open('my-cache');
  const token = await cache.match('token');
  return token ? token.text() : '';
}

async function saveUserToken(token) {
  const cache = await caches.open('my-cache');

  return cache.put('token', new Response(token));
}
