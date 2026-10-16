FROM node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

ENV PORT=80 API_UPSTREAM=http://api:8000
RUN apk add --no-cache ca-certificates
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY 15-upstream-resolver.sh /docker-entrypoint.d/15-upstream-resolver.sh
RUN chmod +x /docker-entrypoint.d/15-upstream-resolver.sh
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80
