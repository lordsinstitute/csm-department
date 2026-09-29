# Vite dev server
FROM node:20-alpine

WORKDIR /app

# Install dependencies (cached layer). Use lockfile when available.
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy source files
COPY index.html ./
COPY vite.config.js ./
COPY public ./public
COPY src ./src

EXPOSE 3030

CMD ["npm", "run", "dev"]
