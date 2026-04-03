FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine

# Copy the built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Default for local docker-compose network; override in Railway frontend variables.
ENV BACKEND_URL=http://backend:8000

# Render nginx config from template at container startup via official nginx entrypoint.
COPY nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
