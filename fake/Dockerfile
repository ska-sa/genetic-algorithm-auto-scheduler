# Use Node as base Image
FROM node:alpine

# Set working dir
WORKDIR /app

# Copy obs_data.json file
COPY obs_data.json ./

# Install json-server globaly using npm
RUN npm install -g json-server

# Exposing json-server port
EXPOSE 3000

# Command to start json-server
CMD ["json-server", "--watch", "obs_data.json", "--host", "0.0.0.0"]