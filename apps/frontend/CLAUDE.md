# Frontend - Next.js File Sharing App

Next.js frontend for the file sharing application.

## Tech Stack

- **Framework**: Next.js 15.5.0 with App Router
- **Runtime**: React 19.1.0
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS v4
- **Linting**: ESLint with Next.js config
- **Build Tool**: Turbopack (for faster builds)

## Project Structure

```
apps/frontend/
├── app/                    # App Router directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout component
│   ├── page.tsx           # Home page
│   └── favicon.ico        # Favicon
├── public/                # Static assets
│   ├── *.svg             # SVG icons
│   └── ...
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── next.config.ts        # Next.js configuration
├── postcss.config.mjs    # PostCSS configuration
├── eslint.config.mjs     # ESLint configuration
└── CLAUDE.md            # This file
```

## Development

### Installation
```bash
npm install
```

### Development Server
```bash
npm run dev
```
- Runs on http://localhost:3000
- Uses Turbopack for faster hot reloading

### Building
```bash
npm run build    # Build for production
npm run start    # Start production server
```

### Linting
```bash
npm run lint
```

## Key Features to Implement

1. **File Upload Interface**
   - Drag and drop file upload
   - Progress indicators
   - File type validation
   - Size limits

2. **File Management**
   - File listing/grid view
   - Delete functionality
   - Download links
   - File sharing options

3. **User Interface**
   - Responsive design with Tailwind
   - Dark/light mode toggle
   - Loading states
   - Error handling

## API Integration

- Backend API calls will be made to the backend service
- Consider using Next.js API routes for backend proxy if needed
- Implement proper error handling for network requests

## Configuration Notes

- Uses App Router (not Pages Router)
- Turbopack enabled for development and build
- TypeScript strict mode enabled
- Tailwind CSS v4 configured with PostCSS