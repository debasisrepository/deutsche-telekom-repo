# Multi-stage Dockerfile for Deutsche Telekom IT Procurement Frontend
FROM node:22-slim AS base

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json ./

# Install dependencies stage
FROM base AS dependencies

RUN npm ci --ignore-scripts

# Build stage
FROM base AS build

# Copy installed dependencies
COPY --from=dependencies /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Runtime stage with nginx
FROM nginx:alpine AS runtime

# ARG/ENV for backend host configuration
ARG BACKEND_HOST=backend
ENV BACKEND_HOST=${BACKEND_HOST}

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx template
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Expose port
EXPOSE 80

# Nginx will automatically process templates in /etc/nginx/templates/
CMD ["nginx", "-g", "daemon off;"]
