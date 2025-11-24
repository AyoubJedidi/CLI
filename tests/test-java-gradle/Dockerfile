# Build stage
FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /app

# Copy Gradle wrapper and build files
COPY gradle gradle
COPY gradlew build.gradle settings.gradle ./

# Download dependencies
RUN ./gradlew dependencies --no-daemon || true

# Copy source code
COPY src ./src

# Build application
RUN ./gradlew bootJar -x test --no-daemon

# Runtime stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Copy artifact from build stage
COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
