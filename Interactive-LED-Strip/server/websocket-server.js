const { readFileSync } = require('fs')
const { createServer } = require('https')
const { WebSocketServer } = require('ws')

// Brightness value the DotStar should use (should be 0.0 - 1.0)
const BRIGHTNESS = 0.1

// Create server for WSS (listen port is set at the end of the file)
const server = createServer({
  cert: readFileSync('/etc/ssl/certs/your-domain.dev.crt'),
  key: readFileSync('/etc/ssl/certs/your-domain.dev.key')
})
const sslWss = new WebSocketServer({ server })

// Non-secure port (for the microcontroller if needed)
const wss = new WebSocketServer({ port: 8880 })

// Store the last color selected
let lastColor = `"25,5,125,${BRIGHTNESS}"`

// Secure websocket logic
sslWss.on('connection', function connection (ws) {
  // Send the last color chosen on connection
  ws.send(lastColor)

  // A new color has been selected!
  ws.on('message', function message (data) {
    let message = data.toString()

    // Check if a valid message (color)...
    const matches = message.match(/"(\d{1,3}),(\d{1,3}),(\d{1,3})"/)
    if (!matches) return

    // Add the brightness value we'd like
    message = `"${matches[1]},${matches[2]},${matches[3]},${BRIGHTNESS}"`

    // Rebroadcast to all clients
    sslWss.clients.forEach((client) => client.send(message))
    wss.clients.forEach((client) => client.send(message))
    lastColor = message
  })
})

// Non-secure websocket logic
wss.on('connection', function connection (ws) {
  ws.send(lastColor)
})

// Set the listen port for the secure websocket
server.listen(8443)
