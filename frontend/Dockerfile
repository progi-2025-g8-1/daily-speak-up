# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Add build arguments
ARG VITE_API_DOMAIN
ARG VITE_WEBSITE_DOMAIN
ARG VITE_API_BASE_URL
ARG VITE_ROOT_ADMIN_EMAIL
ARG VITE_ROOT_ROLE
ARG VITE_ADMIN_ROLE
ARG VITE_MODERATOR_ROLE
ARG VITE_USER_ROLE

COPY package*.json ./

RUN npm install

COPY . .

# Create the runtime config before build
RUN echo "window.ENV = { \
    VITE_API_DOMAIN: '${VITE_API_DOMAIN}', \
    VITE_WEBSITE_DOMAIN: '${VITE_WEBSITE_DOMAIN}', \
    VITE_API_BASE_URL: '${VITE_API_BASE_URL}', \
    VITE_ROOT_ADMIN_EMAIL: '${VITE_ROOT_ADMIN_EMAIL}', \
    VITE_ROOT_ROLE: '${VITE_ROOT_ROLE}', \
    VITE_ADMIN_ROLE: '${VITE_ADMIN_ROLE}', \
    VITE_MODERATOR_ROLE: '${VITE_MODERATOR_ROLE}', \
    VITE_USER_ROLE: '${VITE_USER_ROLE}' \
};" > public/env.js

RUN npm run build

# Production stage
FROM node:22-alpine

WORKDIR /app

RUN npm install -g serve && \
    apk add --no-cache curl

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
