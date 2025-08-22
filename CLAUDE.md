# Briefcase - Secure Document Sharing

Briefcase is a secure document sharing application built as a monorepo with separate frontend and backend services.

## Project Structure

```
briefcase/
├── apps/
│   ├── frontend/      # Next.js frontend application
│   └── backend/       # FastAPI backend with PostgreSQL
└── CLAUDE.md         # This file
```

## Getting Started

### Prerequisites
- Node.js (latest LTS version recommended)
- npm or yarn

### Development

1. **Frontend Development**:
   ```bash
   cd apps/frontend
   npm install
   npm run dev
   ```

2. **Backend Development**:
   ```bash
   cd apps/backend
   # Backend setup instructions to be added
   ```

## Architecture

- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, and React 19
- **Backend**: FastAPI with PostgreSQL and SQLAlchemy

## Available Commands

### Frontend
- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production with Turbopack
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Backend
- Commands to be added when backend is implemented

## Development Notes

- Frontend uses Turbopack for faster development builds
- TypeScript is configured across the frontend
- Tailwind CSS v4 is set up for styling
- ESLint is configured for code quality

## Git Commit Guidelines

Include LLM version in commit footer:
```
🤖 Generated with [Claude Code](https://claude.ai/code)(Claude Sonnet 4)
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Next Steps

1. Set up backend service
2. Define API contracts between frontend and backend
3. Implement file upload/download functionality
4. Add authentication and authorization
5. Set up database for file metadata