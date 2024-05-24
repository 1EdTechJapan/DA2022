# Use an official OpenJDK runtime as a parent image
FROM openjdk:11-jre-slim

# Set the working directory to /app
WORKDIR /app

# Copy the executable JAR file into the container at /app/app.jar
COPY target/spring-security-lti13-demo-1.0-SNAPSHOT.jar app.jar
COPY config config

# Expose port 8080 to the Docker host
EXPOSE 8443

# Run the JAR file when the container launches
ENTRYPOINT ["java", "-jar", "app.jar"]