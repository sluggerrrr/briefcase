# Briefcase - Secure Document Sharing

Briefcase is a production-ready secure document sharing application built as a monorepo with complete frontend and backend services. The project follows story-driven development with comprehensive testing and multiple deployment configurations.

## Project Structure

```
file-sharing-app/
├── apps/
│   ├── frontend/           # Next.js 15 frontend application (React 19)
│   │   ├── app/            # App Router with auth, dashboard, upload
│   │   ├── components/     # Reusable UI components (shadcn/ui)
│   │   ├── tests/          # Playwright E2E tests
│   │   ├── package.json    # Frontend dependencies & scripts
│   │   └── CLAUDE.md       # Frontend-specific documentation
│   └── backend/            # FastAPI backend with PostgreSQL
│       ├── app/            # Application code (models, API, services)
│       ├── alembic/        # Database migrations
│       ├── tests/          # Pytest test suite
│       ├── pyproject.toml  # Python dependencies
│       └── CLAUDE.md       # Backend-specific documentation
├── docs/                   # Architecture & PRD documentation
├── stories/                # Story-driven development tracking
├── scripts/                # Database initialization scripts
├── docker-compose.yml      # Local development environment
├── docker-compose.prod.yml # Production Docker configuration
├── railway.toml            # Railway deployment config
└── CLAUDE.md              # This file
```

## Architecture & Features

### Frontend (Next.js 15)
- **Framework**: Next.js 15.5.0 with App Router and Turbopack
- **Runtime**: React 19.1.0
- **Language**: TypeScript 5 (strict mode)
- **Styling**: Tailwind CSS v4 with custom components
- **UI Library**: Radix UI components with shadcn/ui
- **State Management**: TanStack Query for server state
- **Features**:
  - 🔐 User authentication (login/register)
  - 📄 Document dashboard with card-based UI
  - ⬆️ File upload with progress tracking
  - 👥 Document sharing and permissions
  - 🔧 Bulk operations (delete, share)
  - 🎨 Dark/light theme support
  - ♿ Accessibility improvements
  - 📱 Responsive design

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt hashing
- **Encryption**: AES document encryption
- **Features**:
  - 👤 User management and authentication
  - 📁 Document storage with metadata
  - 🔒 Role-based access control
  - 📊 Activity logging and audit trails
  - ⏰ Automated document lifecycle management
  - 🔧 Admin dashboard functionality
  - 🧪 Comprehensive test coverage

## Getting Started

### Prerequisites
- Node.js (latest LTS version recommended)
- Python 3.12+
- PostgreSQL
- Docker (optional, for containerized development)
- uvx (for running MCP tools like context7 and semgrep-mcp)

### Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repository>
   cd file-sharing-app
   ```

2. **Frontend Development**:
   ```bash
   cd apps/frontend
   npm install
   npm run dev        # Start with Turbopack
   ```

3. **Backend Development**:
   ```bash
   cd apps/backend
   uv sync            # Install dependencies
   uv run uvicorn app.main:app --reload
   ```

4. **Docker Development** (Alternative):
   ```bash
   docker-compose up  # Starts all services
   ```

5. **Development Tools**:
   ```bash
   # Use context7 MCP server for fresh code practices and standards
   uvx context7-mcp
   
   # Run security vulnerability scanning
   uvx semgrep --config=auto .
   
   # Playwright is available for browser automation and testing
   # (accessible via MCP tools for web interactions)
   ```

## Available Commands

### Frontend Commands
```bash
npm run dev          # Start development server with Turbopack
npm run build        # Build for production with Turbopack
npm run start        # Start production server
npm run lint         # Run ESLint
npm run typecheck    # Run TypeScript type checking
npm run check        # Run both lint and typecheck
npm run test:e2e     # Run Playwright E2E tests
npm run test:e2e:ui  # Show Playwright test report
```

### Backend Commands
```bash
uv run uvicorn app.main:app --reload  # Development server
uv run pytest                        # Run test suite
uv run pytest -v                     # Verbose test output
uv run alembic upgrade head          # Apply database migrations
```

## MCP Tools & Best Practices

### Context7 MCP Server
Use the context7 MCP server for all coding tasks to ensure adherence to fresh code practices and current development standards. Context7 provides up-to-date coding patterns, best practices, and modern development approaches:
```bash
uvx context7-mcp
```

**Recommended Usage**: Always consult context7 before implementing new features, refactoring code, or when unsure about modern coding patterns and architectural decisions.

### Security Scanning
Regularly run semgrep to identify and eliminate security vulnerabilities:
```bash
uvx semgrep --config=auto .
```

This will scan the codebase for common security issues including:
- Container security misconfigurations
- Code vulnerabilities
- Insecure patterns and practices

### Playwright Browser Automation
Playwright is available as an MCP tool for browser automation, testing, and web interactions:
- Navigate to URLs and interact with web pages
- Take screenshots and snapshots
- Automate form submissions and clicks
- Perform end-to-end testing scenarios

## Development Workflow

### Story-Driven Development
The project follows a structured story-based approach:
- Stories are organized by sprints in the `stories/` directory
- Each story represents a complete feature or improvement
- Progress is tracked with completion status

### Quality Assurance Pipeline

Before committing changes, ensure you:
1. Run `npm run check` (lint + typecheck) in the frontend directory
2. Run `uv run pytest` in the backend directory  
3. Run `uvx semgrep --config=auto .` to check for security vulnerabilities
4. Use `uvx context7-mcp` for code practice guidance and modern development patterns

### Testing Strategy
- **Frontend**: Playwright E2E tests with comprehensive UI coverage
- **Backend**: Pytest with fixtures and test isolation
- **Integration**: API testing with realistic data scenarios

## Deployment

The application supports multiple deployment platforms:

### Railway (Production)
- Configured with `railway.toml`
- Automatic builds from git commits
- Environment variable management

### Vercel (Frontend)
- Next.js optimized deployment
- Automatic preview deployments
- Build configuration in `vercel.json`

### Docker
- Multi-stage builds for production
- Docker Compose for local development

## Git Commit Guidelines

Include LLM version in commit footer:
```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Current Status & Completion

### ✅ Completed Features
- Complete authentication system (login/register/JWT)
- Document upload and storage with encryption
- Document dashboard with card-based UI
- Role-based permissions and access control
- User management and admin functionality
- Responsive design with dark/light themes
- Accessibility improvements
- E2E testing with Playwright
- Database migrations and lifecycle management

### 🔧 Known Issues to Address
- Some Playwright accessibility tests failing
- Build optimization opportunities

### 🚀 Deployment Status
- Backend: Deployed on Railway
- Frontend: Deployable on Vercel
- Database: PostgreSQL with migrations

This is a mature, production-ready application with sophisticated document sharing capabilities, comprehensive security measures, and modern development practices.