# aiagentobfluau/app.py

from flask import Flask, jsonify, request

from arena import Arena


app = Flask(__name__)
arena = Arena()

MAX_SOURCE_LENGTH = 10_000


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "project": "aiagentobfluau"
    })


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

    except (TypeError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except Exception:
        app.logger.exception("Arena execution failed")

        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


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
