# frameworks/node/templates/Dockerfile.j2
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build (if needed)
RUN npm run build || true

EXPOSE 3000

CMD ["npm", "start"]