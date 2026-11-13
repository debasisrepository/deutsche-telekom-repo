# Multi-stage build for Deutsche Telekom Procurement Frontend
FROM node:22 AS builder

WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Runtime stage with nginx
FROM nginx:alpine

# Set backend host as build arg with default
ARG BACKEND_HOST=backend
ENV BACKEND_HOST=${BACKEND_HOST}

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx template configuration
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Expose port 80
EXPOSE 80

# Start nginx (will process template with envsubst)
CMD ["nginx", "-g", "daemon off;"]
