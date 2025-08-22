# 📁 Briefcase - Secure Document Sharing Platform

A professional, enterprise-grade document sharing platform built with security-first principles, featuring end-to-end encryption, role-based permissions, and automated lifecycle management.

## 🏗️ Architecture

Briefcase is built as a modern monorepo with separate frontend and backend services:

```
briefcase/
├── apps/
│   ├── frontend/      # Next.js 15 React application
│   └── backend/       # FastAPI Python service
├── stories/           # Development stories and requirements
└── README.md         # This file
```

## ✨ Key Features

### 🔐 Security First
- **AES-256 Encryption**: All documents encrypted at rest
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Granular permission system (Admin, Owner, Editor, Viewer)
- **Audit Trails**: Complete logging of all document interactions
- **Access Controls**: Time-based expiration and view limits

### 📄 Document Management
- **Multi-Format Support**: PDF, images, text documents, and archives
- **Bulk Operations**: Multi-select delete, share, and download
- **Advanced Search**: Full-text search with filters and date ranges
- **Document Analytics**: Usage patterns, access metrics, and engagement tracking
- **Lifecycle Management**: Automated cleanup and expiration handling

### 💼 Enterprise Features
- **Admin Dashboard**: Comprehensive system management and monitoring
- **User Management**: Role assignment and permission oversight
- **System Health**: Real-time monitoring and performance metrics
- **Bulk Sharing**: Share documents with multiple recipients
- **Permission Groups**: Organize users into permission groups

### 🎨 User Experience
- **Modern UI**: Clean, responsive interface built with shadcn/ui
- **Document Viewer**: In-browser viewing with zoom, navigation, and watermarks
- **Real-time Updates**: Live status updates and notifications
- **Mobile Responsive**: Optimized for desktop, tablet, and mobile devices
- **Accessibility**: WCAG AA compliant with keyboard navigation

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **PostgreSQL** (for production) or SQLite (for development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd briefcase
   ```

2. **Start the backend**
   ```bash
   cd apps/backend
   # See backend/README.md for detailed setup
   uv run uvicorn app.main:app --reload
   ```

3. **Start the frontend**
   ```bash
   cd apps/frontend
   # See frontend/README.md for detailed setup
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📚 Documentation

- **[Frontend Documentation](./apps/frontend/README.md)** - Next.js setup, components, and development
- **[Backend Documentation](./apps/backend/README.md)** - FastAPI setup, APIs, and database
- **[Stories](./stories/README.md)** - Development stories and feature specifications

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 15 with App Router
- **UI Library**: React 19 with shadcn/ui components
- **Styling**: Tailwind CSS v4
- **State Management**: TanStack Query for server state
- **Forms**: React Hook Form with Zod validation
- **Build Tool**: Turbopack for fast development

### Backend
- **Framework**: FastAPI with Python 3.9+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt hashing
- **Encryption**: AES-256 for document encryption
- **Testing**: pytest with comprehensive test coverage
- **Package Manager**: uv for fast dependency management

### Infrastructure
- **Deployment**: Vercel (frontend) + Railway/Docker (backend)
- **Database**: PostgreSQL for production, SQLite for development
- **Storage**: Local filesystem with planned cloud storage integration
- **Monitoring**: Built-in health checks and metrics endpoints

## 🔄 Development Workflow

### Sprint-Based Development
The project follows an agile development approach with feature stories organized by sprints:

- **Sprint 1**: Foundation (Auth, Database, Infrastructure)
- **Sprint 2**: Document Security (Encryption, Upload, Storage)
- **Sprint 3**: Access Control (Permissions, Lifecycle, Basic UI)
- **Sprint 4**: Advanced Features (Dashboard, Bulk Operations, Admin)
- **Sprint 5**: Enhanced UX (Viewer, Analytics, Mobile)

### Available Scripts

**Frontend:**
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run typecheck` - TypeScript type checking

**Backend:**
- `uv run uvicorn app.main:app --reload` - Start development server
- `uv run pytest` - Run test suite
- `uv run pytest --cov` - Run tests with coverage

## 🧪 Testing

### Backend Testing
- **Unit Tests**: Comprehensive test coverage for services and APIs
- **Integration Tests**: End-to-end testing of complete workflows
- **Security Tests**: Permission system and access control validation
- **Performance Tests**: Load testing for file operations

### Frontend Testing
- **Component Tests**: React component testing with Jest/RTL
- **E2E Tests**: User workflow testing with Playwright
- **Accessibility Tests**: WCAG compliance validation

## 📈 Performance & Scalability

- **File Handling**: Streaming for large files, base64 for smaller documents
- **Database**: Optimized queries with proper indexing
- **Caching**: Strategic caching for frequently accessed data
- **API Design**: RESTful APIs with efficient pagination
- **Frontend**: Code splitting and lazy loading for optimal performance

## 🔒 Security Considerations

- **Encryption**: AES-256 encryption for all stored documents
- **Authentication**: Secure JWT implementation with refresh tokens
- **Authorization**: Granular role-based access control (RBAC)
- **Input Validation**: Comprehensive validation on both client and server
- **Audit Logging**: Complete audit trails for compliance
- **Rate Limiting**: Protection against abuse and brute force attacks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following our coding standards
4. Write tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Message Format
Follow the conventional commit format:
```
type(scope): description

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/apps/frontend/README.md` and `/apps/backend/README.md`
- **Issues**: Create an issue on GitHub
- **Development**: See the `/stories` directory for feature specifications

## 🚀 Deployment

### Production Deployment
- **Frontend**: Deployed on Vercel with automatic builds
- **Backend**: Containerized with Docker for deployment on Railway, AWS, or similar
- **Database**: PostgreSQL with connection pooling
- **Environment**: Separate staging and production environments

### Environment Variables
See individual README files in `/apps/frontend` and `/apps/backend` for required environment variables.

---

**Built with ❤️ using modern web technologies for secure document collaboration.**