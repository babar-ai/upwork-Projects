from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the connection
    while True:
        data = await websocket.receive_text()  # Receive message from the client
        await websocket.send_text(f"Message received: {data}")  # Send message back to client

# For testing in the browser
@app.get("/")
async def get():
    html_content = """
    <html>
        <head>
            <title>WebSocket Test</title>
        </head>
        <body>
            <h1>WebSocket Test</h1>
            <textarea id="messageInput" placeholder="Type a message..."></textarea><br>
            <button onclick="sendMessage()">Send Message</button>
            <h2>Received messages:</h2>
            <div id="messages"></div>
            <script>
                var ws = new WebSocket("ws://localhost:8000/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById("messages");
                    messages.innerHTML += "<p>" + event.data + "</p>";
                };
                function sendMessage() {
                    var input = document.getElementById("messageInput").value;
                    ws.send(input);
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
