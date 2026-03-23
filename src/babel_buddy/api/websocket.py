import base64
import json
from fastapi import WebSocket, WebSocketDisconnect

async def websocket_chat(ws: WebSocket, engine):
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)

            if msg["type"] == "control":
                if msg["action"] == "start_session":
                    session_id = await engine.start_session()
                    await ws.send_json({"type": "state", "state": "listening", "session_id": session_id})
                elif msg["action"] == "end_session":
                    await engine.end_session()
                    await ws.send_json({"type": "state", "state": "idle"})
                    break

            elif msg["type"] == "audio":
                audio_bytes = base64.b64decode(msg["data"])
                await ws.send_json({"type": "state", "state": "processing"})
                result = await engine.process_audio(audio_bytes)

                await ws.send_json({
                    "type": "transcript",
                    "text": result.transcript,
                    "language": result.language,
                })

                if result.is_exit:
                    await ws.send_json({"type": "state", "state": "idle"})
                    break

                await ws.send_json({
                    "type": "reply",
                    "text": result.reply,
                    "translation": result.translation,
                    "language": result.language,
                })

                if result.audio:
                    audio_b64 = base64.b64encode(result.audio).decode()
                    await ws.send_json({"type": "audio", "data": audio_b64})

                await ws.send_json({"type": "state", "state": "listening"})

    except WebSocketDisconnect:
        await engine.end_session()
