# ---------------------------------------------------------
# STAGE 1: Builder
# ---------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Enable corepack for pnpm/yarn/npm support, but let's assume npm workspace
# Copy root package.json and lockfile if using turborepo
COPY package*.json ./
COPY apps/web/package*.json ./apps/web/

RUN npm ci

# Copy full application
COPY . .

# Build the web application leveraging next.js standalone output
WORKDIR /app/apps/web
RUN npm run build

# ---------------------------------------------------------
# STAGE 2: Runner
# ---------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Set the correct permissions
COPY --from=builder /app/apps/web/public ./public

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Note: server.js is created by next build from the standalone output
CMD ["node", "server.js"]
