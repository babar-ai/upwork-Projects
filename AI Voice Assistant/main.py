import asyncio
import websockets 
import base64
import os
import json
from dotenv import load_dotenv

load_dotenv()

#prepares a WebSocket connection to Deepgram’s STS server.
def sts_connect():
  
  api_key = os.getenv('DEEPGRAM_API_KEY')
  if not api_key:
      raise ValueError("DEEPGRAM_API_KEY environment variable is not set")

  sts_ws = websockets.connect(
      "wss://agent.deepgram.com/v1/agent/converse",           # Deepgram’s server.the specific “room” on their server where real-time speech-to-speech (STS)
      subprotocols=["token", api_key]                          # Send authentication token (your API key)
  )

  return sts_ws



def load_config():
   
   with open("config.json", "r") as f:                         
         return json.load(f)                                   # Returns it as a Python object (usually a dictionary).
   


async def handle_berge_in(decoded, twilio_ws, streamsid):

    if decoded["type"] == "UserStardedSpeaking":
        clear_message = {
            "event": "start",
            "streamSid": streamsid
        }
        await twilio_ws.send(json.dumps(clear_message))



async def handle_text_message(decoded, twilio_ws, sts_ws, streamsid):

    await handle_berge_in(decoded, twilio_ws, streamsid)
    #to do handle funtion calling
#SEND AUDIO TO DEEPGRAM

async def sts_sender(sts_ws, audio_queue):
    
    print("Starting to send audio to Deepgram...")
    while True:
        chunk = await audio_queue.get()
        await sts_ws.send(chunk)



async def sts_reciver(sts_ws, twilio_ws, streamsid_queue):
    print("Starting to receive messages from Deepgram...")

    streamsid = await streamsid_queue.get()
    print(f"Received streamsid: {streamsid}")

    async for message in sts_ws:
        if type(message) is str:
            print("Received text message from Deepgram:", message)
            decoded = json.loads(message)
            await handle_text_message(decoded, twilio_ws, sts_ws, streamsid)
            continue

        raw_mulaw = message

        media_message = {
            "event": "media",
            "streamSid": streamsid,
            "media": {
                "payload": base64.b64encode(raw_mulaw).decode("ascii"),
            }
        }

        await twilio_ws.send(json.dumps(media_message))



async def twilio_reciver(twilio_ws, audio_queue, streamsid_queue):
    BUFFER_SIZE = 2 * 160                   # create fixed-size audio frames
    inbufer = bytearray(b"")           

    async for message in twilio_ws:         #iterates over messages arriving from the WebSocket.

        try:
            data = json.loads(message)       # parses the JSON string into a Python dict (data).
            event = data.get("event")      

            if event == "start":
                print("call started or get our streamsid")
                start = data.get("start", {})
                streamsid = start.get("streamsid")           #each call has a unique streamsid
                streamsid_queue.put_nowait(streamsid)        #places the streamsid into the streamsid_queue without awaiting
            
            elif event == "connected":
                print("call connected")
                continue

            elif event == "media":
                media = data.get("media", {})
                chunk = base64.b64decode(media.get("payload", ""))

                if media.get("track") == "inbound":            # Twilio can send multiple tracks (e.g., "inbound" = caller, "outbound" = agent)
                    inbufer.extend(chunk)
            
            elif event == "stop":
                    break                   


            while len(inbufer) >= BUFFER_SIZE:
                chunk = inbufer[:BUFFER_SIZE]
                audio_queue.put_nowait(chunk)
                inbufer = inbufer[BUFFER_SIZE:]

        except:
            break



async def twilio_handler(twilio_ws):
    audio_queue = asyncio.Queue()               #to pass audio chunks to other coroutines
    streamsid_queue = asyncio.Queue()           # caller unique id 

    async with sts_connect() as sts_ws:
        config_message = load_config()

        await sts_ws.send(json.dumps(config_message))
        
        await asyncio.wait(
            [
                asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
                asyncio.ensure_future(sts_reciver(sts_ws, twilio_ws, streamsid_queue)),
                asyncio.ensure_future(twilio_reciver(twilio_ws, audio_queue, streamsid_queue))

            ]
        )

        await twilio_ws.close()



async def main():

    await websockets.serve(twilio_handler, host="localhost", port=8000)       # This starts a WebSocket server locally (via websockets library).
    print("WebSocket server started on ws://localhost:8000")                   # twilio_ws = the live WebSocket connection between Twilio and your backend, injected by websockets.serve.
    await asyncio.Future()  # Run forever



if __name__ == "__main__":
    asyncio.run(main())





'''
4. Example Flow

Caller dials your Twilio number.

Twilio executes the TwiML and connects to wss://your-ngrok/twilio.

Your WebSocket server (websockets.serve) accepts the connection.

The twilio_handler(twilio_ws) function is invoked with the socket.

From then on, you use twilio_ws inside your code to:

Get audio chunks (from twilio_reciver).

Send audio/text back (from sts_reciver, etc

'''