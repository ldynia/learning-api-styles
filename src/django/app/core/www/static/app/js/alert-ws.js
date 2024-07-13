let RECONNECT_DELAY_MS = 10000;
let RECONNECT_LIMIT = 15;
let reconnectCount = 0;
let socket = null;

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

function handleWebSocketConnection() {
  // WebSocket connection was open
  socket.onopen = function(e) {
    console.info('Connected to', shortenUrl(socket.url));
  }

  // Messages received from the WebSocket
  socket.onmessage = function(e) {
    const message = JSON.parse(e.data).message;
    console.info(`Received '${message}' message from`, shortenUrl(socket.url));
    document.getElementById('messageDisplay').value += `${message}\n`;
  }

  // WebSocket connection closed - try to reconnect to the server
  socket.onclose = function(e) {
    if (e.reason !== '') {
      console.error('Disconnected from', shortenUrl(socket.url), e.reason);
    } else {
      let interval = setTimeout(function(){
        reconnectCount++;
        if (reconnectCount > RECONNECT_LIMIT) {
          clearInterval(interval);
          console.error(`Stop reconnecting, reconnection limit reached after ${--reconnectCount} attempts.`);
          return;
        }
        console.info(`Reconnecting ${reconnectCount}/${RECONNECT_LIMIT} to socket`, shortenUrl(socket.url));
        webSocketReconnect();
      }, RECONNECT_DELAY_MS);
    }
  }

  // WebSocket error occurred
  socket.onerror = function(e) {
    console.error('Failed connect to', shortenUrl(socket.url), 'Make sure that token is valid!');
  }
}

function webSocketReconnect() {
  // Close existing WebSocket connection
  if (socket !== null) {
    socket.close();
  }

  const response = getAccessToken();
  response.then(function(token) {
    // Connect to WebSocket server
    if (token !== null) {
      const url = buildUrl(token);
      socket = new WebSocket(url);
      handleWebSocketConnection();
    }
  }).catch(function(e) {
    console.error(e.message);
  });
}

function shortenUrl(url) {
  return url.split('?')[0];
}

function buildUrl(token) {
  const tokenB64 = btoa(token);
  const hostname = window.location.hostname;
  const queryParams = window.location.search;
  let url = `ws://${hostname}/ws/v1/alert${queryParams}&access_token=${tokenB64}`;

  // Build the WebSocket URL for GitHub Codespaces
  if (hostname.endsWith('.github.dev')) {
    url = `ws://${hostname.replace('8000', '8001')}/ws/v1/alert?access_token=${tokenB64}`;
    if (queryParams !== '') {
      url = `ws://${hostname.replace('8000', '8001')}/ws/v1/alert${queryParams}&access_token=${tokenB64}`;
    }
  }

  // Build the WebSocket URL for local environment
  if (window.location.port) {
    url = `ws://${hostname}:8001/ws/v1/alert?access_token=${tokenB64}`;
    if (queryParams !== '') {
      url = `ws://${hostname}:8001/ws/v1/alert${queryParams}&access_token=${tokenB64}`;
    }
  }

  // Adjust WebSocket scheme based on HTTP scheme
  if (window.location.protocol === 'https:' ) {
    url = url.replace('ws://', 'wss://')
  }

  return url;
}

window.onload = function() {
  const response = getAccessToken();
  response.then(function(token) {
    // Connect to WebSocket server
    if (token !== null) {
      const url = buildUrl(token);
      socket = new WebSocket(url);
      handleWebSocketConnection();
    }
  }).catch(function(e) {
    console.error(e.message);
  });
}
