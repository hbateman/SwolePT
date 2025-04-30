#!/bin/bash

# Exit on error
set -e

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

# Function to stop running application processes
function stop_running_app {
    echo "Checking for running application processes..."
    
    # Check for running backend server
    if pgrep -f "python.*local_server.py" > /dev/null; then
        echo "Stopping backend server..."
        pkill -f "python.*local_server.py"
        sleep 2
    fi
    
    # Check for running frontend server
    if pgrep -f "node.*react-scripts" > /dev/null; then
        echo "Stopping frontend server..."
        pkill -f "node.*react-scripts"
        sleep 2
    fi
    
    echo "✅ All application processes stopped"
}

# Check if environment and command arguments are provided
if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

# Get the environment and command arguments
ENV=$1
CMD=$2

# Function to switch environment
function switch_environment {
    local env=$1
    case $env in
        "local")
            echo "Setting up local development environment..."
            if [ -f .env.local ]; then
                cp .env.local .env
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
case $CMD in
    "setup")
        if [ "$ENV" = "local" ]; then
            echo "Setting up local development environment..."
            
            # Stop any existing containers
            echo "Stopping existing containers..."
            docker-compose down -v || true
            
            # Start Docker services
            echo "Starting Docker services..."
            docker-compose up -d
            
            # Check service health
            check_service_health postgres || exit 1
            check_service_health localstack || exit 1
            
            # Install dependencies
            echo "Installing Python dependencies..."
            pip install -r backend/requirements.txt
            pip install flask localstack-client
            
            # Setup local AWS services
            echo "Setting up local AWS services..."
            if [ -f backend/local_setup.py ]; then
                python backend/local_setup.py
            else
                echo "❌ Error: backend/local_setup.py not found"
                exit 1
            fi
            
            # Run database migrations
            echo "Running database migrations..."
            if [ -f backend/migrations/setup_local_db.sh ]; then
                cd backend/migrations
                ./setup_local_db.sh
                cd ../..
            else
                echo "❌ Error: backend/migrations/setup_local_db.sh not found"
                exit 1
            fi
            
            echo "✅ Local development environment setup complete!"
        else
            echo "❌ Error: Setup command is only available for local environment"
            exit 1
        fi
        ;;
    "build")
        echo "Building the application..."
        if [ "$ENV" = "local" ]; then
            # Build backend
            cd backend
            pip install -r requirements.txt
            cd ..
            
            # Build frontend
            cd frontend
            npm install
            npm run build:local
            cd ..
        else
            # Production build
            cd frontend
            npm install
            npm run build:prod
            cd ..
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
            
            # Start backend server
            cd backend
            python local_server.py &
            BACKEND_PID=$!
            cd ..
            
            # Start frontend
            cd frontend
            npm start &
            FRONTEND_PID=$!
            cd ..
            
            # Wait for processes
            wait $BACKEND_PID $FRONTEND_PID
        else
            echo "❌ Error: Start command is only available for local environment"
            exit 1
        fi
        ;;
    "deploy")
        if [ "$ENV" = "prod" ]; then
            echo "Deploying to production..."
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
        echo "❌ Error: Invalid command '$CMD'"
        show_usage
        exit 1
        ;;
esac

echo "✅ Command '$CMD' completed successfully!" 