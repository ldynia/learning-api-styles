// When the page has loaded, establish a websocket connection
window.onload = function() {

  const hostname = window.location.hostname;
  let url = `ws://${hostname}/ws/v1/echo`;

  // Build the WebSocket URL for GitHub Codespaces
  if (hostname.endsWith('.github.dev')) {
    url = `ws://${hostname.replace('8000', '8001')}/ws/v1/echo`;
  }

  // Build the WebSocket URL for local development environment
  if (window.location.port) {
    url = `ws://${hostname}:8001/ws/v1/echo`;
  }

  // Adjust WebSocket scheme based on HTTP scheme
  if (window.location.protocol === 'https:' ) {
    url = url.replace('ws://', 'wss://');
  }

  // Establish a websocket connection
  const socket = new WebSocket(url);

  // Websocket connection was open
  socket.onopen = function(e) {
    console.info(`Connected to ${socket.url}`);
    const msg = {'message': 'Hello WebSocket!'};
    socket.send(JSON.stringify(msg));
    console.info(`Sent '${msg.message}' message to ${socket.url}`);
  }

  // Messages received from the websocket
  socket.onmessage = function(e) {
    const message = JSON.parse(e.data).message;
    document.querySelector('h1').innerText = message;
    console.info(`Received '${message}' message from ${socket.url}`);
    socket.close();
  }

  // Websocket connection was closed
  socket.onclose = function(e) {
    console.info(`Closed connection to ${socket.url}`);
  }

  // Websocket error occurred
  socket.onerror = function(e) {
    console.error(`Encountered an error when talking to ${socket.url}`);
  }
}