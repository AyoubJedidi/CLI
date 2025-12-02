# Build stage
FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /app

# Copy Gradle wrapper
COPY gradle gradle
COPY gradlew ./
COPY build.gradle ./
COPY settings.gradle ./

# Copy source
COPY src ./src

# Build
RUN ./gradlew build -x test --no-daemon

# Runtime stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Copy JAR
COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
