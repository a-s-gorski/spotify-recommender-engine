# ---- STAGE 1: Build the application ----
FROM maven:3.9.5-eclipse-temurin-17 AS builder

# Set work directory
WORKDIR /app

# Copy pom.xml and download dependencies (leverage Docker layer caching)
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy the rest of the source code
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# ---- STAGE 2: Create minimal runtime image ----
FROM eclipse-temurin:17-jre-alpine

# Set environment variable for JVM
ENV JAVA_OPTS=""

# Create non-root user
RUN addgroup -S spring && adduser -S spring -G spring

# Set working directory
WORKDIR /app

# Copy only the JAR from the previous stage
COPY --from=builder /app/target/*.jar app.jar

# Use a non-root user
USER spring:spring

# Expose port (optional – only for documentation)
EXPOSE 8080

# Run the application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
