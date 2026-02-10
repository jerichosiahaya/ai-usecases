# Stage 1: Build the application
FROM node:22-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application source code
COPY . .

# Run the build script
RUN npm run build

# Stage 2: Production environment
FROM node:22-alpine

WORKDIR /app

# Copy the build output from the builder stage
COPY --from=builder /app/.output .

# Expose the port the app runs on
EXPOSE 3000

# Set the command to start the server
CMD [ "node", "./server/index.mjs" ]
