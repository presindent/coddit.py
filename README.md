# coddit with ChatGPT

This is a simple Python script to host a Flask server and a websockets server on the localhost to help interface ChatGPT via an OpenAI-like REST API. It currently supports the `/v1/chat/completions` endpoint, and has been written especially for usage with coddit.nvim. It may be extended for general usage in future.

It will require the [coddit Chrome extension](https://github.com/presindent/coddit-chrome) to be installed in your browser.

## Setup

Simply run the `server.py` in an environment with Flask installed. It will start an HTTP server at `localhost:5000` and a websockets server at `localhost:5001`, which may then be used to communicate with a ChatGPT webpage in the browser. Ensure that both of these ports are free, or modify them accordingly, before running the script.
