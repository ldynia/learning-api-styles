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
      body: JSON.stringify({'username': 'admin', 'password': 'admin' })
    });

    if (response.status === 200) {
      toggleInput(false);
      let data = await response.json();
      return data.access;
    }
    return null;
  } catch (e) {
  console.error(e.message);
    toggleInput();
  }
}

function handleWebSocketConnection() {
  // WebSocket connection was open
  socket.onopen = function(e) {
    console.info('Connected to', shortenUrl(socket.url));
    toggleInput(false);
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
      document.getElementById('messageDisplay').value = e.reason;
      console.error('Disconnected from', shortenUrl(socket.url), 'Reason:', e.reason);
      toggleInput();
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
    console.error('Failed connect to', shortenUrl(socket.url), 'Make sure that your token is valid!');
  }

  // Trigger click on ENTER
  document.getElementById('messageInput').focus();
  document.getElementById('messageInput').onkeyup = function(e) {
    if (e.key === 'Enter') {
      document.getElementById('messageSubmit').click();
    }
  }

  // Send a message to the WebSocket server
  document.getElementById('messageSubmit').onclick = function(e) {
    e.preventDefault();
    if (Boolean(socket.readyState)) {
      const messageInputDom = document.getElementById('messageInput');
      const message = messageInputDom.value;
      if (messageInputDom.value !== '') {
        socket.send(JSON.stringify({'message': message}));
        messageInputDom.value = '';

        // Scroll to the bottom of the message display
        const messageDisplay = document.getElementById('messageDisplay');
        messageDisplay.scrollTop = messageDisplay.scrollHeight;
        console.info(`Sent '${message}' message to`, shortenUrl(shortenUrl(socket.url)));
      }
    }
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
  let url = `ws://${hostname}/ws/v1/chat${queryParams}&access_token=${tokenB64}`;

  // Build the WebSocket URL for GitHub Codespaces
  if (hostname.endsWith('.github.dev')) {
    url = `ws://${hostname.replace('8000', '8001')}/ws/v1/chat?access_token=${tokenB64}`;
    if (queryParams !== '') {
      url = `ws://${hostname.replace('8000', '8001')}/ws/v1/chat${queryParams}&access_token=${tokenB64}`;
    }
  }

  // Build the WebSocket URL for local environment
  if (window.location.port) {
    url = `ws://${hostname}:8001/ws/v1/chat?access_token=${tokenB64}`;
    if (queryParams !== '') {
      url = `ws://${hostname}:8001/ws/v1/chat${queryParams}&access_token=${tokenB64}`;
    }
  }

  // Adjust WebSocket scheme based on HTTP scheme
  if (window.location.protocol === 'https:' ) {
    url = url.replace('ws://', 'wss://')
  }

  return url;
}

function toggleInput(disabled = true) {
  document.getElementById('messageInput').disabled = disabled;
  document.getElementById('messageSubmit').disabled = disabled;
}

function clearDisplay(e) {
  e.preventDefault();
  document.getElementById('messageDisplay').value = '';
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
