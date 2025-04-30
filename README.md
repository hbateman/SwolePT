# SwolePT

A comprehensive personal training and workout management application.

## Project Structure

```
swolePT/
├── frontend/          # React frontend application
├── backend/           # Python backend application
├── infrastructure/    # Infrastructure as Code (Terraform)
├── .env              # Environment variables template
├── switch-env.sh     # Environment switching script
├── build.sh          # Build and deployment script
└── setup_env.sh      # Initial environment setup script
```

## Environment Management

The application supports multiple environments (development and production) with a flexible environment switching system.

### Environment Variables

Environment variables are managed through a single `.env` file that contains all necessary configuration for both frontend and backend services. The file is structured to support multiple environments:

```bash
# Development Environment
DEV_FRONTEND_URL=http://localhost:3000
DEV_BACKEND_URL=http://localhost:8000
DEV_DATABASE_URL=postgresql://user:password@localhost:5432/swolept_dev

# Production Environment
PROD_FRONTEND_URL=https://app.swolept.com
PROD_BACKEND_URL=https://api.swolept.com
PROD_DATABASE_URL=postgresql://user:password@prod-db:5432/swolept_prod
```

### Switching Environments

The `switch-env.sh` script allows you to easily switch between development and production environments:

```bash
# Switch to development environment
./switch-env.sh dev

# Switch to production environment
./switch-env.sh prod
```

This script:
1. Updates environment variables for both frontend and backend
2. Configures the appropriate database connections
3. Sets up the correct API endpoints
4. Updates any environment-specific configurations

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/swolept.git
   cd swolept
   ```

2. Run the initial setup script:
   ```bash
   ./setup_env.sh
   ```

3. Switch to development environment:
   ```bash
   ./switch-env.sh dev
   ```

## Development Workflow

1. Start the development servers:
   ```bash
   # Start backend server
   cd backend
   python manage.py runserver

   # Start frontend development server
   cd frontend
   npm run dev
   ```

2. Make your changes and test in the development environment

3. When ready to deploy to production:
   ```bash
   ./switch-env.sh prod
   ./build.sh
   ```

## Build and Deployment

The `build.sh` script handles the build and deployment process. Before running the build script, ensure you have:

1. Prerequisites installed:
   - Node.js (v16 or higher)
   - Python 3.8 or higher
   - AWS CLI configured with appropriate credentials
   - PostgreSQL (for local development)
   - AWS CDK CLI (`npm install -g aws-cdk`)

2. Environment setup:
   ```bash
   # Install backend dependencies
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cd ..

   # Install frontend dependencies
   cd frontend
   npm install
   cd ..

   # Install infrastructure dependencies
   cd infrastructure
   npm install
   cd ..
   ```

3. Build process:
   ```bash
   # Switch to the desired environment
   ./switch-env.sh dev  # or prod

   # Run the build script
   ./build.sh
   ```

The build script performs the following steps:
1. Validates environment variables and configuration
2. Builds the frontend application
3. Runs backend tests and linting checks
4. Builds and deploys infrastructure (if needed)
5. Deploys the application to the appropriate environment

### Infrastructure Deployment

If you need to deploy or update infrastructure:

```bash
cd infrastructure
npm run build
npx cdk deploy
```

### Database Migrations

To run database migrations:

```bash
cd backend/migrations
./setup_local_db.sh  # For local development
./run_migrations.sh  # For production
```

### Testing

Run tests before deployment:

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test

# Infrastructure tests
cd infrastructure
npm test
```

## Infrastructure

The `infrastructure/` directory contains Terraform configurations for managing cloud resources. This includes:
- Database instances
- Compute resources
- Networking configuration
- Security groups and IAM roles

## Local Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.8 or higher
- Node.js 14 or higher
- PostgreSQL client (optional, for direct database access)

### Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/swolept.git
   cd swolept
   ```

2. Copy the environment file:
   ```bash
   cp .env.example .env.local
   ```

3. Update the environment variables in `.env.local` with your local configuration.

4. Use the build script to set up and start the local environment:
   ```bash
   # Setup local environment (first time only)
   ./build.sh local setup

   # Start the application
   ./build.sh local start
   ```

This will:
- Start LocalStack and PostgreSQL containers
- Set up local AWS services
- Install all dependencies
- Run database migrations
- Start the backend and frontend servers

### Accessing the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- LocalStack: http://localhost:4566
- PostgreSQL: localhost:5432

### Development Workflow
1. **Frontend Development**:
   - Make changes to React components
   - Changes are hot-reloaded
   - API calls go to local backend

2. **Backend Development**:
   - Modify Lambda functions in `backend/functions/`
   - Changes are reflected in `local_server.py`
   - Test API endpoints directly

3. **Database Development**:
   - Connect to local PostgreSQL
   - Run migrations if needed
   - Test database changes

### Testing AWS Services Locally
- S3: Use AWS CLI with `--endpoint-url http://localhost:4566`
- Cognito: Configured through LocalStack
- API Gateway: Handled by local server

### Troubleshooting
1. **LocalStack Issues**:
   ```bash
   docker-compose logs localstack
   ```

2. **Database Issues**:
   ```bash
   docker-compose logs postgres
   ```

3. **Backend Issues**:
   - Check `local_server.py` logs
   - Verify environment variables
   - Ensure database is running

4. **Frontend Issues**:
   - Check browser console
   - Verify API endpoints
   - Check environment variables

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test in development environment
4. Submit a pull request

## License

[Your chosen license] 