# 🖥️ Frontend - Briefcase Document Sharing

Modern React frontend for the Briefcase secure document sharing platform, built with Next.js 15 and featuring a professional UI with comprehensive document management capabilities.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start
```

**Development Server**: http://localhost:3000

## 📦 Technology Stack

### Core Framework
- **Next.js 15.5.0** - React framework with App Router
- **React 19.1.0** - Latest React with concurrent features
- **TypeScript 5** - Type-safe development
- **Turbopack** - Ultra-fast bundler for development and production

### UI & Styling
- **shadcn/ui** - High-quality React components
- **Tailwind CSS v4** - Utility-first CSS framework
- **Radix UI** - Accessible component primitives
- **Lucide React** - Beautiful SVG icons
- **next-themes** - Theme switching support

### State & Data Management
- **TanStack Query v5** - Server state management and caching
- **TanStack Form** - Type-safe form handling
- **React Hook Form** - Performant form validation
- **Zod** - TypeScript-first schema validation

### Development Tools
- **ESLint** - Code linting and quality
- **TypeScript** - Static type checking
- **PostCSS** - CSS processing
- **Turbopack** - Fast development builds

## 🏗️ Project Structure

```
apps/frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Authentication routes
│   │   └── login/                # Login page
│   ├── admin/                    # Admin dashboard
│   │   ├── users/                # User management
│   │   ├── system/               # System monitoring
│   │   └── lifecycle/            # Document lifecycle
│   ├── documents/                # Document management
│   │   ├── [id]/                 # Individual document pages
│   │   ├── upload/               # Document upload
│   │   └── search/               # Document search
│   ├── components/               # React components
│   │   ├── auth/                 # Authentication components
│   │   ├── dashboard/            # Dashboard components
│   │   ├── documents/            # Document components
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── upload/               # Upload components
│   │   └── layout/               # Layout components
│   ├── hooks/                    # Custom React hooks
│   ├── lib/                      # Utility functions
│   ├── providers/                # React context providers
│   ├── types/                    # TypeScript type definitions
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Home page
├── public/                       # Static assets
├── package.json                  # Dependencies and scripts
├── next.config.ts                # Next.js configuration
├── tailwind.config.ts            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
└── README.md                     # This file
```

## 🎨 Component Architecture

### UI Components (shadcn/ui)
```
app/components/ui/
├── button.tsx           # Button variants
├── input.tsx            # Form inputs
├── dialog.tsx           # Modal dialogs
├── card.tsx             # Content cards
├── dropdown-menu.tsx    # Dropdown menus
├── progress.tsx         # Progress indicators
├── badge.tsx            # Status badges
├── alert.tsx            # Alert messages
├── skeleton.tsx         # Loading skeletons
└── ...                  # Additional UI components
```

### Feature Components
```
app/components/
├── auth/
│   ├── LoginForm.tsx             # Login form
│   ├── RegistrationForm.tsx      # User registration
│   └── ProtectedRoute.tsx        # Route protection
├── dashboard/
│   ├── DashboardLayout.tsx       # Main dashboard layout
│   ├── DocumentList.tsx          # Document listing
│   ├── DocumentCard.tsx          # Document preview cards
│   └── BulkActions.tsx           # Bulk operation controls
├── documents/
│   ├── DocumentViewer.tsx        # Document preview
│   ├── DocumentActions.tsx       # Document actions menu
│   ├── DocumentSearch.tsx        # Advanced search
│   └── DocumentAnalytics.tsx     # Usage analytics
├── upload/
│   ├── DocumentUpload.tsx        # File upload interface
│   ├── FileDropZone.tsx          # Drag & drop zone
│   ├── UploadProgress.tsx        # Upload progress
│   └── RecipientSelector.tsx     # User selection
└── layout/
    ├── AppHeader.tsx             # Application header
    ├── Navigation.tsx            # Main navigation
    └── Footer.tsx                # Application footer
```

## 🔧 Configuration

### Environment Variables
Create `.env.local` for local development:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key

# Optional: Analytics
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
```

### TypeScript Configuration
The project uses strict TypeScript configuration with path aliases:

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "strict": true,
    "paths": {
      "@/*": ["./app/*"]
    }
  }
}
```

## 📱 Features & Pages

### Authentication
- **Login Page**: JWT-based authentication with form validation
- **Registration Modal**: User signup with real-time validation
- **Protected Routes**: Automatic redirection for unauthorized access
- **Role-Based Access**: Different UI based on user roles (Admin, User)

### Document Management
- **Dashboard**: Document listing with search and filters
- **Upload Interface**: Drag & drop with progress tracking
- **Document Viewer**: In-browser PDF/image viewing with security features
- **Bulk Operations**: Multi-select actions (delete, share, download)
- **Advanced Search**: Full-text search with date/type filters
- **Analytics**: Document usage statistics and access patterns

### Admin Features
- **System Dashboard**: Health monitoring and metrics
- **User Management**: User roles and permissions
- **Lifecycle Management**: Automated cleanup configuration
- **Document Administration**: System-wide document oversight

### User Experience
- **Responsive Design**: Mobile, tablet, and desktop optimized
- **Dark/Light Themes**: Automatic and manual theme switching
- **Real-time Updates**: Live status updates via polling
- **Accessibility**: WCAG AA compliant with keyboard navigation
- **Progressive Loading**: Optimized performance with lazy loading

## 🔌 API Integration

### Backend Communication
The frontend communicates with the FastAPI backend using RESTful APIs:

- **Authentication**: JWT-based auth with automatic token refresh
- **Documents**: Upload, download, search, and management
- **Permissions**: Role-based access control and sharing
- **Admin**: System management and monitoring
- **Real-time**: Polling-based updates for live data

### TanStack Query Integration
- **Caching**: Smart caching with automatic background updates
- **Optimistic Updates**: Immediate UI feedback for better UX
- **Error Handling**: Comprehensive error handling with retries
- **Background Sync**: Keep data fresh with intelligent refetching

## 📱 Mobile & Responsive Design

### Breakpoints
- **Mobile**: `< 768px` - Stacked layouts, touch-friendly controls
- **Tablet**: `768px - 1024px` - Adaptive layouts with collapsible sidebars
- **Desktop**: `> 1024px` - Full-featured layouts with multi-column designs

### Touch Interactions
- **Swipe Gestures**: Document navigation and actions
- **Long Press**: Context menus and multi-select
- **Pinch Zoom**: Document viewer interactions
- **Pull to Refresh**: Content updates

## ♿ Accessibility Features

### WCAG AA Compliance
- **Keyboard Navigation**: Full keyboard access to all features
- **Screen Reader Support**: Proper ARIA labels and semantic HTML
- **Focus Management**: Clear focus indicators and logical tab order
- **Color Contrast**: High contrast ratios for all text and UI elements
- **Alternative Text**: Descriptive alt text for images and icons

## 📋 Available Scripts

```bash
# Development
npm run dev              # Start development server with Turbopack
npm run build            # Build for production with Turbopack
npm run start            # Start production server
npm run lint             # Run ESLint
npm run lint:fix         # Fix auto-fixable lint issues
npm run typecheck        # TypeScript type checking
npm run check            # Run lint and typecheck together
npm run vercel-build     # Build optimized for Vercel
```

## 🚀 Deployment

### Vercel Deployment (Recommended)
The project is configured for seamless deployment on Vercel:

```bash
# Automatic deployment via Git
git push origin main

# Manual deployment
npm run vercel-build
```

### Environment Setup
```env
# Production environment variables
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_URL=https://yourdomain.com
NEXTAUTH_URL=https://yourdomain.com
NEXTAUTH_SECRET=your-production-secret
```

## 🔍 Troubleshooting

### Common Issues

**Build Errors**
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**TypeScript Errors**
```bash
# Check TypeScript configuration
npm run typecheck

# Update TypeScript definitions
npm update @types/node @types/react @types/react-dom
```

**Styling Issues**
```bash
# Restart development server
npm run dev

# Clear browser cache or disable cache in dev tools
```

## 📚 Additional Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **React Documentation**: https://react.dev
- **shadcn/ui Components**: https://ui.shadcn.com
- **Tailwind CSS**: https://tailwindcss.com/docs
- **TanStack Query**: https://tanstack.com/query/latest

## 🤝 Contributing

See the main project [README.md](../../README.md) for contribution guidelines.

---

**Built with modern web technologies for a secure, performant document sharing experience.**
