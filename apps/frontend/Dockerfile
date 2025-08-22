# Frontend Dockerfile for Briefcase application
FROM node:20-alpine as base

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Development stage
FROM base as development

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Set environment variables for development
ENV NODE_ENV=development
ENV NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
CMD ["npm", "run", "dev"]

# Build stage
FROM base as builder

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine as production

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=http://backend:8000

# Start the application
CMD ["node", "server.js"]