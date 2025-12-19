# Use a lightweight base image
FROM aleixmt/bmde-linux:latest

# Copy entrypoint ans test materials into image container
COPY entrypoint.sh  /app/
RUN chmod +x /app/entrypoint.sh
COPY ./test.zip /app/

# Set working directory into /app dir
WORKDIR /app

# Install unzip dependency
RUN apt-get update && \
    apt-get install -y unzip coreutils

# Unzip test files
RUN unzip test.zip

# Run test
ENTRYPOINT ["/app/entrypoint.sh"]