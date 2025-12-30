# Stage 1: Build Flutter Web App
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

# Copy pubspec files
COPY pubspec.yaml pubspec.lock ./

# Get dependencies
RUN flutter pub get

# Copy source code
COPY . .

# Build web app with release mode
RUN flutter build web --release --base-href /diagnostic/

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built web app
# Copy built web app to subdirectory matching base-href
COPY --from=build /app/build/web /usr/share/nginx/html/diagnostic

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
