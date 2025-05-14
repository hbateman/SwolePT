# Local Development

This directory contains all the local development specific code and utilities for the SwolePT backend.

## Directory Structure

```
local/
├── __init__.py          # Package initialization
├── server.py           # Local development server
├── setup.py            # Local environment setup
├── db.py               # Local database utilities
├── auth.py             # Local authentication utilities
├── logs/               # Log files
│   ├── backend.log
│   └── workout_upload.log
└── pids/               # Process ID files
    ├── backend.pid
    └── frontend.pid
```

## Setup

1. Ensure you have all prerequisites installed:
   - Python 3.8+
   - Docker and Docker Compose
   - Node.js and npm

2. Run the setup script:
   ```bash
   ./build.sh local setup
   ```

## Running the Application

1. Start the application:
   ```bash
   ./build.sh local start
   ```

2. Stop the application:
   ```bash
   ./build.sh local stop
   ```

## Logs

Log files are stored in the `logs` directory:
- `backend.log`: Backend server logs
- `workout_upload.log`: Workout upload processing logs

## Process Management

Process ID files are stored in the `pids` directory and are used by the build script to manage the application processes. 