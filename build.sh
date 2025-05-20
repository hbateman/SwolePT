#!/bin/bash

# Exit on error
set -e

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local max_attempts=5
    local attempt=1
    
    echo "Waiting for $host:$port to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port >/dev/null 2>&1; then
            echo "✅ $host:$port is ready!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: $host:$port not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $host:$port failed to start after $max_attempts attempts"
    return 1
}

# Function to start backend
start_backend() {
    echo "Starting backend..."
    
    # Ensure log directory exists
    mkdir -p backend/local/logs
    
    # Clear previous logs
    echo "" > backend/local/logs/backend.log
    
    # Start backend in background
    cd backend
    # Set PYTHONPATH to include the current directory
    export PYTHONPATH=$(pwd):$PYTHONPATH
    python -m local.server > local/logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to be ready (single attempt)
    if wait_for_service localhost 8000; then
        echo "✅ Backend started successfully!"
        return 0
    fi
    
    echo "❌ Backend failed to start"
    echo "Backend error log:"
    cat backend/local/logs/backend.log
    
    # Clean up
    kill $BACKEND_PID 2>/dev/null || true
    return 1
}

# Function to display usage
function show_usage {
    echo "Usage: $0 [environment] [command]"
    echo "Environments:"
    echo "  local   - Local development environment"
    echo "  prod    - Production environment"
    echo "Commands:"
    echo "  setup   - Setup the environment"
    echo "  build   - Build the application"
    echo "  start   - Start the application"
    echo "  deploy  - Deploy the application"
    echo "Examples:"
    echo "  $0 local setup  - Setup local development environment"
    echo "  $0 prod deploy  - Deploy to production"
}

# Function to check if a command exists
function command_exists {
    command -v "$1" >/dev/null 2>&1
}

# Function to check service health
function check_service_health {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    echo "Checking health of $service..."
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service | grep -q "healthy"; then
            echo "✅ $service is healthy"
            return 0
        fi
        echo "Waiting for $service to be healthy (attempt $attempt/$max_attempts)..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service failed to become healthy after $max_attempts attempts"
    return 1
}

# Function to stop any running application processes
function stop_running_app {
    echo "Stopping any running application processes..."
    
    # Find and kill any running backend processes
    echo "Checking for running backend processes..."
    pkill -f "python -m local.server" || true
    
    # Find and kill any running frontend processes
    echo "Checking for running frontend processes..."
    # Kill processes using port 3000
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    # Kill React development server processes
    pkill -f "react-scripts start" || true
    pkill -f "node.*start.js" || true
    
    # Wait a moment for processes to fully terminate
    sleep 2
    
    # Verify ports are free
    if lsof -ti:3000 >/dev/null 2>&1; then
        echo "❌ Warning: Port 3000 is still in use. Trying to force kill..."
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    if lsof -ti:8000 >/dev/null 2>&1; then
        echo "❌ Warning: Port 8000 is still in use. Trying to force kill..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    echo "✅ Process cleanup completed"
}

# Set workspace root
export WORKSPACE_ROOT="$(pwd)"

# Check if environment is specified
if [ -z "$1" ]; then
    echo "❌ Error: Environment not specified"
    show_usage
    exit 1
fi

ENV=$1
COMMAND=$2

# Function to switch environment
function switch_environment {
    local env=$1
    case $env in
        "local")
            echo "Setting up local development environment..."
            if [ -f .env.local ]; then
                cp .env.local .env
                # Export all variables from .env.local
                set -a
                source .env.local
                set +a
                export LOCAL_DEVELOPMENT=true
                echo "✅ Switched to local development environment"
            else
                echo "❌ Error: .env.local file not found"
                exit 1
            fi
            ;;
        "prod")
            echo "Setting up production environment..."
            if [ -f .env.prod ]; then
                cp .env.prod .env
                # Export all variables from .env.prod
                set -a
                source .env.prod
                set +a
                export LOCAL_DEVELOPMENT=false
                echo "✅ Switched to production environment"
            else
                echo "❌ Error: .env.prod file not found"
                exit 1
            fi
            ;;
        *)
            echo "❌ Error: Invalid environment '$env'"
            show_usage
            exit 1
            ;;
    esac
}

# Check prerequisites
if [ "$ENV" = "local" ]; then
    if ! command_exists docker; then
        echo "❌ Error: Docker is not installed"
        exit 1
    fi
    if ! command_exists docker-compose; then
        echo "❌ Error: Docker Compose is not installed"
        exit 1
    fi
    if ! command_exists python3; then
        echo "❌ Error: Python 3 is not installed"
        exit 1
    fi
    if ! command_exists npm; then
        echo "❌ Error: Node.js/npm is not installed"
        exit 1
    fi
fi

# Switch to the specified environment
switch_environment $ENV

# Execute the command
case $COMMAND in
    "setup")
        echo "Setting up the application..."
        if [ "$ENV" = "local" ]; then
            # Install backend dependencies
            echo "Installing backend dependencies..."
            cd backend
            pip install -r requirements.txt
            cd ..
            
            # Install frontend dependencies
            echo "Installing frontend dependencies..."
            cd frontend
            npm install
            cd ..
            
            # Start Docker services
            echo "Starting Docker services..."
            docker-compose up -d
            
            # Wait for services to be ready
            echo "Waiting for services to be ready..."
            sleep 10
            
            # Run database setup and migrations
            echo "Setting up database and running migrations..."
            cd backend
            export PYTHONPATH=$PYTHONPATH:$(pwd)
            # Initialize database using our setup script
            if ! python -m db.setup; then
                echo "❌ Database setup failed. Check the logs for details."
                exit 1
            fi
            cd ..
            
            echo "✅ Setup completed! You can now run './build.sh local start' to start the application."
        else
            echo "❌ Error: Setup command is only available for local environment"
            exit 1
        fi
        ;;
    "start")
        echo "Starting the application..."
        if [ "$ENV" = "local" ]; then
            # Stop any running application processes
            stop_running_app
            
            # Check if services are running
            if ! docker-compose ps | grep -q "Up"; then
                echo "❌ Error: Docker services are not running. Run './build.sh local setup' first."
                exit 1
            fi
            
            # Ensure local environment variables are set
            export REACT_APP_ENVIRONMENT=local
            export REACT_APP_API_URL=http://localhost:8000
            
            # Start backend
            echo "Starting backend..."
            if ! start_backend; then
                echo "❌ Failed to start backend. Check the logs for details."
                exit 1
            fi
            
            # Start frontend
            echo "Starting frontend..."
            cd frontend
            npm start &
            FRONTEND_PID=$!
            cd ..
            
            # Wait for frontend to be ready
            echo "Waiting for frontend to be ready..."
            if ! wait_for_service localhost 3000; then
                echo "❌ Frontend failed to start"
                kill $BACKEND_PID 2>/dev/null || true
                kill $FRONTEND_PID 2>/dev/null || true
                exit 1
            fi
            
            echo "✅ All services started successfully!"
            echo "Backend running on http://localhost:8000"
            echo "Frontend running on http://localhost:3000"
            
            # Wait for user interrupt
            trap 'echo "Shutting down..."; kill $BACKEND_PID 2>/dev/null || true; kill $FRONTEND_PID 2>/dev/null || true; exit 0' INT
            wait
        else
            echo "❌ Error: Start command is only available for local environment"
            exit 1
        fi
        ;;
    "stop")
        echo "Stopping the application..."
        if [ "$ENV" = "local" ]; then
            stop_running_app
            echo "✅ Application stopped"
        else
            echo "❌ Error: Stop command is only available for local environment"
            exit 1
        fi
        ;;
    "test")
        echo "Running tests..."
        if [ "$ENV" = "local" ]; then
            # Run backend tests
            echo "Running backend tests..."
            cd backend
            python -m pytest
            cd ..
            
            # Run frontend tests
            echo "Running frontend tests..."
            cd frontend
            npm test
            cd ..
            
            echo "✅ Tests completed!"
        else
            echo "❌ Error: Test command is only available for local environment"
            exit 1
        fi
        ;;
    "deploy")
        if [ "$ENV" = "prod" ]; then
            echo "Deploying to production..."
            # Ensure production environment variables are set
            export REACT_APP_ENVIRONMENT=prod
            # Get API URL from .env.prod file
            if [ -f .env.prod ]; then
                export REACT_APP_API_URL=$(grep REACT_APP_API_URL .env.prod | cut -d '=' -f2)
                if [ -z "$REACT_APP_API_URL" ]; then
                    echo "❌ Error: REACT_APP_API_URL not found in .env.prod file"
                    exit 1
                fi
            else
                echo "❌ Error: .env.prod file not found"
                exit 1
            fi
            
            # Add production deployment steps here
            cd infrastructure
            npm install
            npm run build
            npx cdk deploy
            cd ..
        else
            echo "❌ Error: Deploy command is only available for production environment"
            exit 1
        fi
        ;;
    *)
        echo "❌ Error: Invalid command '$COMMAND'"
        show_usage
        exit 1
        ;;
esac

echo "✅ Command '$COMMAND' completed successfully!" 