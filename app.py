from flask import Flask, jsonify, request
from arena import Arena
import threading
import time

app = Flask(__name__)
arena = Arena()

MAX_SOURCE_LENGTH = 10_000

# =========================
# Arena State
# =========================

arena_running = False
arena_thread = None

total_score = {
    "obfuscator": 0,
    "deobfuscator": 0
}

round_count = 0


def arena_loop():
    global arena_running
    global round_count
    global total_score

    while arena_running:
        round_count += 1

        source = f"print('AI Arena Round {round_count}')"

        try:
            result = arena.run(source)

            total_score["obfuscator"] += result["score"]["obfuscator"]
            total_score["deobfuscator"] += result["score"]["deobfuscator"]

        except Exception:
            app.logger.exception("Arena round failed")

        time.sleep(1)


# =========================
# Health
# =========================

@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "project": "aiagentobfluau"
    })


# =========================
# Run One Round
# =========================

@app.post("/arena/run")
def run_arena():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Request body must be JSON"
        }), 400

    source = data.get("source")

    if not isinstance(source, str):
        return jsonify({
            "success": False,
            "error": "source must be a string"
        }), 400

    source = source.strip()

    if not source:
        return jsonify({
            "success": False,
            "error": "source cannot be empty"
        }), 400

    if len(source) > MAX_SOURCE_LENGTH:
        return jsonify({
            "success": False,
            "error": f"source exceeds {MAX_SOURCE_LENGTH} characters"
        }), 400

    try:
        result = arena.run(source)

        return jsonify(result), 200

    except Exception:
        app.logger.exception("Arena execution failed")

        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


# =========================
# Start Arena
# =========================

@app.post("/arena/start")
def start_arena():
    global arena_running
    global arena_thread

    if arena_running:
        return jsonify({
            "success": True,
            "status": "already_running"
        })

    arena_running = True

    arena_thread = threading.Thread(
        target=arena_loop,
        daemon=True
    )

    arena_thread.start()

    return jsonify({
        "success": True,
        "status": "running"
    })


# =========================
# Stop Arena
# =========================

@app.post("/arena/stop")
def stop_arena():
    global arena_running

    arena_running = False

    return jsonify({
        "success": True,
        "status": "stopped"
    })


# =========================
# Score
# =========================

@app.get("/score")
def get_score():
    return jsonify({
        "success": True,
        "running": arena_running,
        "rounds": round_count,
        "score": {
            "obfuscator": total_score["obfuscator"],
            "deobfuscator": total_score["deobfuscator"]
        }
    })


# =========================
# 404
# =========================

@app.errorhandler(404)
def not_found(_error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
