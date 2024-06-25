from flask import Flask, request, jsonify, Blueprint, Response
import asyncio
import websockets
import threading

app = Flask(__name__)
blueprint = Blueprint("blueprint", __name__)

# websockets clients
clients = {"agent": None, "user": None}


@blueprint.after_request
def after_request(response: Response):
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@blueprint.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    api_key = request.headers.get("Authorization")
    if not api_key or not api_key.startswith("Bearer "):
        return jsonify({"error": "Invalid or missing API key"}), 401
    try:
        data = request.get_json()
        if not data or "messages" not in data:
            raise ValueError("Invalid request: 'messages' field is required")
    except Exception as e:
        return jsonify({"error": f"Invalid request: {e}"}), 400

    response = asyncio.run(
        send_and_receive(
            data["messages"][-1]["content"],
            data["messages"][0]["content"]
            + "\n\nYou will start after the next prompt. For now, just assert your agreement.",
        )
    )
    response_data = {"choices": [{"message": {"content": response[1:]}}]}
    print(response_data)
    return jsonify(response_data), 200


async def websocket_handler(websocket, path):
    async for message in websocket:
        if message[0] == "p" or message[0] == "s":  # p: prompt, s: system prompt
            clients["user"] = websocket
            print("user client registered")
            # message == "p" is just for registering the client
            if message != "p" and clients["agent"]:
                await clients["agent"].send(message)
        elif message[0] == "r":
            clients["agent"] = websocket
            print("agent client registered")
            if message != "r" and clients["user"]:  # r: response
                await clients["user"].send(message)
        else:
            print(f"Received message with unexpected prefix: {message}")


async def start_websocket_server():
    server = await websockets.serve(websocket_handler, "localhost", 5001)
    await server.wait_closed()


def start_websocket_server_thread():
    asyncio.new_event_loop().run_until_complete(start_websocket_server())


async def send_and_receive(message, system):
    uri = "ws://localhost:5001"
    async with websockets.connect(uri) as websocket:
        # send system prompt -- the agent will discard it if already sent before
        await websocket.send("s" + system)
        await websocket.recv()

        await websocket.send("p" + message)
        response = await websocket.recv()

        return response


if __name__ == "__main__":
    # start websockets server in a separate thread
    websocket_thread = threading.Thread(
        target=start_websocket_server_thread, daemon=True
    )
    websocket_thread.start()

    # start flask app
    app.register_blueprint(blueprint)
    app.run(port=5000)
