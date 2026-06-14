# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
# Install dependencies
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve the static files with Nginx
FROM nginx:alpine

# Copy the custom nginx configuration into the image
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build files from Stage 1 to the Nginx html folder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
