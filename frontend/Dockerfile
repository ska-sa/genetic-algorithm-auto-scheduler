# Step 1: Build the Angular application
FROM node:lts-alpine AS builder

WORKDIR /app

# Copy only package.json and package-lock.json first for better caching
COPY package*.json ./

# Install Dependecies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Angular application
RUN npm run build -- --output-path=/usr/src/app/dist/frontend

# Step 2: Serve the application using Nginx
FROM nginx:alpine

# Remove the default Nginx index.html file
RUN rm -rf /usr/share/nginx/html/*

# Copy the build output from the builder stage to the Nginx html directory
COPY --from=builder /usr/src/app/dist/frontend/ /usr/share/nginx/html/

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Start Nginx directly
CMD ["nginx", "-g", "daemon off;"]