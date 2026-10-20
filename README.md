# pr-agent

A free AI pull-request reviewer for GitHub. It reads the changed lines of a PR,
asks an AI model (Groq) to look for bugs and security problems, and posts one
review with inline comments.

Setup: copy `.env.example` to `.env`, fill in your keys, install `requirements.txt`.
Never commit `.env`.