# ── Stage 1: Build ────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests first (layer cache optimisation)
# Only re-runs npm ci when package-lock.json changes
COPY package.json package-lock.json ./

RUN npm ci --prefer-offline

# Copy source and build
COPY public/ ./public/
COPY src/ ./src/

ARG REACT_APP_VERSION=1.0.0
ARG REACT_APP_ENV=production

ENV REACT_APP_VERSION=$REACT_APP_VERSION
ENV REACT_APP_ENV=$REACT_APP_ENV

RUN npm run build

# ── Stage 2: Serve ────────────────────────────────────────────────────────
FROM nginx:1.25-alpine AS production

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Custom nginx config for React SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:80/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
