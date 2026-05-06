FROM node:22-alpine

WORKDIR /app

# Install chromium for tests if needed, but run app as node user
RUN apk add --no-cache chromium
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser

COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

COPY . .

# Ensure permissions for node user
# RUN chown -R node:node /app

# USER node

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
