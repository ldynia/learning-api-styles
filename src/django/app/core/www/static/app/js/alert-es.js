let eventSource = null;

async function getAccessToken() {
  try {
    // WARNING: NEVER HARDCODE CREDENTIALS IN THE CODE!
    // REASON: We do it ONLY to have a user interaction-less setup.
    // ALTERNATIVE: Ask the user for credentials.
    let response = await fetch('/api/jwt/obtain',{
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({'username': 'admin', 'password': 'admin'})
    });

    if (response.status === 200) {
      let data = await response.json();
      return data.access;
    } else {
      return null;
    }
  } catch (e) {
    console.error(e.message);
  }
}

function shortenUrl(url) {
  return url.split('?')[0];
}

function buildUrl(token) {
  const tokenB64 = btoa(token);
  const port = parseInt(window.location.port) + 1;
  const city_uuid = new URLSearchParams(window.location.search).get('city_uuid');
  return `${window.location.protocol}//${window.location.hostname}:${port}/sse/v1/alert?city_uuid=${city_uuid}&access_token=${tokenB64}`;
}

function handleEventSourceConnection() {
  eventSource.onopen = function(e) {
    console.info(`Connected to ${shortenUrl(eventSource.url)}`);
  }

  eventSource.onmessage = function(e) {
    const message = JSON.parse(e.data)['message'];
    console.info(`Received '${message}' message from ${shortenUrl(eventSource.url)}`);
    document.getElementById('messageDisplay').value += `${message}\n`;
  }

  eventSource.onerror = function(e) {
    console.error(`Encountered an error when talking to ${shortenUrl(eventSource.url)}`);
  }
}

window.onload = function() {
  const response = getAccessToken();
  response.then(function(token) {
    // Connect to WebSocket server
    if (token !== null) {
      const url = buildUrl(token);
      eventSource = new EventSource(url);
      handleEventSourceConnection();
    }
  }).catch(function(e) {
    console.error(e.message);
  });
}