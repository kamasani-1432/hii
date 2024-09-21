import socket
from fastapi import FastAPI
from twilio.rest import Client

app = FastAPI()

# Twilio setup
account_sid = 'ACef646e3875aadd1e0c5d08676f49de77'
auth_token = '8a769912087a64c8fa0db126b7ac1228'
client = Client(account_sid, auth_token)
twilio_number = '+12083579769'
to_number = '+919176274608'

# Get the local IP address of the server
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable, we just need the correct interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

local_ip = get_local_ip()

@app.post("/post")
def make_emergency_call():
    try:
        call = client.calls.create(
            twiml='<Response><Say>Your emergency contact has initiated an emergency call. Please check on them.</Say></Response>',
            to=to_number,
            from_=twilio_number
        )
        print("Call initiated")
        return {"status": "success", "call_sid": call.sid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# To run the server and expose it on the local network
if __name__ == "__main__":
    import uvicorn
    print(f"Serving at http://{local_ip}:8080")
    uvicorn.run(app, host=local_ip, port=8080)
