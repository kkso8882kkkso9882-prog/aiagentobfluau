# aiagentobfluau/app.py

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

arena_lock = threading.Lock()

total_score = {
    "obfuscator": 0,
    "deobfuscator": 0
}

round_count = 0

last_result = None


# =========================
# Arena Loop
# =========================

def arena_loop():

    global arena_running
    global round_count
    global total_score
    global last_result

    while arena_running:

        source = (
            f"print('AI Arena Round {round_count + 1}')"
        )

        try:

            result = arena.run(source)

            with arena_lock:

                round_count += 1

                total_score["obfuscator"] += (
                    result["score"]["obfuscator"]
                )

                total_score["deobfuscator"] += (
                    result["score"]["deobfuscator"]
                )

                last_result = result

        except Exception:

            app.logger.exception(
                "Arena round failed"
            )

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
# Start
# =========================

@app.post("/arena/start")
def start_arena():

    global arena_running
    global arena_thread

    with arena_lock:

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
# Stop
# =========================

@app.post("/arena/stop")
def stop_arena():

    global arena_running

    with arena_lock:

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

    with arena_lock:

        return jsonify({
            "success": True,

            "running":
                arena_running,

            "rounds":
                round_count,

            "score": {
                "obfuscator":
                    total_score["obfuscator"],

                "deobfuscator":
                    total_score["deobfuscator"]
            }
        })


# =========================
# Last Result
# =========================

@app.get("/arena/last")
def get_last_result():

    with arena_lock:

        if last_result is None:

            return jsonify({
                "success": True,
                "result": None
            })

        return jsonify({
            "success": True,
            "result": last_result
        })


# =========================
# Manual Arena Run
# =========================

@app.post("/arena/run")
def run_arena():

    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):

        return jsonify({
            "success": False,
            "error":
                "Request body must be JSON"
        }), 400

    source = data.get("source")

    if not isinstance(source, str):

        return jsonify({
            "success": False,
            "error":
                "source must be a string"
        }), 400

    source = source.strip()

    if not source:

        return jsonify({
            "success": False,
            "error":
                "source cannot be empty"
        }), 400

    if len(source) > MAX_SOURCE_LENGTH:

        return jsonify({
            "success": False,
            "error":
                f"source exceeds "
                f"{MAX_SOURCE_LENGTH} characters"
        }), 400

    try:

        result = arena.run(source)

        return jsonify(
            result
        ), 200

    except Exception:

        app.logger.exception(
            "Arena execution failed"
        )

        return jsonify({
            "success": False,
            "error":
                "Internal server error"
        }), 500


# =========================
# 404
# =========================

@app.errorhandler(404)
def not_found(_error):

    return jsonify({
        "success": False,
        "error":
            "Endpoint not found"
    }), 404


# =========================
# Local
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
