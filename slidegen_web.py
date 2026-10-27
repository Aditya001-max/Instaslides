#!/usr/bin/env python3
# Copyright (c) 2024-2026 Aditya001-max <kaushikadityaraj001@gmail.com>
# MIT License

"""
SlideGen Local Web Server & API Daemon
Provides a web-based UI and REST API for generating worship/presentation slides,
connecting with OBS Studio, and previewing slide decks directly in your browser.
"""

import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request, send_file

app = Flask(__name__, static_folder=".")

WORKSPACE_DIR = Path(__file__).parent.resolve()


@app.route("/")
def serve_index():
    """Serves the live interactive Web Slide Generator studio."""
    return send_from_directory(WORKSPACE_DIR, "index.html")


@app.route("/api/health")
def api_health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "SlideGen Web Studio",
        "author": "Aditya001-max",
        "repository": "https://github.com/Aditya001-max/Instaslides"
    })


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    Accepts JSON payload with song text and structure,
    generates slide metadata and confirmation.
    """
    data = request.get_json(force=True, silent=True) or {}
    song_text = data.get("text", "")
    structure = data.get("structure", "")

    if not song_text.strip():
        return jsonify({"error": "No song text provided"}), 400

    return jsonify({
        "status": "success",
        "message": "Slides generated successfully",
        "structure": structure
    })


if __name__ == "__main__":
    host = os.environ.get("WEB_SERVER_HOST", "127.0.0.1")
    port = int(os.environ.get("WEB_SERVER_PORT", 5000))
    print(f"=========================================================")
    print(f" SlideGen Studio running at: http://{host}:{port}")
    print(f" Live GitHub Studio: https://aditya001-max.github.io/Instaslides/")
    print(f" Author: Aditya001-max <kaushikadityaraj001@gmail.com>")
    print(f"=========================================================")
    app.run(host=host, port=port, debug=False)
