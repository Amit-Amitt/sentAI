FROM oven/bun:1.3.14 AS base

WORKDIR /app

COPY package.json bun.lock turbo.json tsconfig.json components.json ./
COPY apps ./apps
COPY packages ./packages

RUN bun install
RUN bun run --cwd apps/web build

EXPOSE 3000

CMD ["bun", "run", "--cwd", "apps/web", "start"]
