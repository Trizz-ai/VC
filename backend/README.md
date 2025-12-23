# Verified Compliance Backend

## Quick Start

1. **Install dependencies**
   ```bash
   cd backend
   poetry install
   ```

2. **Set up environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   poetry run alembic upgrade head
   ```

5. **Start the server**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## API Documentation

- **Development**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Development Guidelines

- **Import Rules**: ONLY single-line imports allowed
- **Testing Rules**: NO mocks, simulations, or hardcoded responses
- **Code Quality**: 80%+ test coverage required
- **Security**: All inputs validated with Pydantic schemas
