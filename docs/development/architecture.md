# Architecture

BMDE is built with a modular architecture.

*   **CLI Layer:** Uses `typer` to define commands and arguments.
*   **Service Layer:** Orchestrates the logic for each command.
*   **Backend Layer:** Abstracts the execution environment (Docker, Host).
*   **Configuration:** Uses `pydantic` for settings validation.
