# Installation

## Prerequisites

*   **Operating System:** Linux (Ubuntu 20.04+ recommended)
*   **Python:** 3.11 or higher
*   **Docker:** (Optional but recommended) For running components in containers.
*   **Make:** (Optional) For build automation.

## Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/URV-teacher/bmde
    cd bmde
    ```

2.  **Install dependencies:**
    ```bash
    make install
    ```

3.  **Verify installation:**
    ```bash
    ./venv/bin/bmde --help
    ```
