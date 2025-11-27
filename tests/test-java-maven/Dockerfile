# Build stage
FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /app

# Copy Maven files (if they exist)
COPY pom.xml .
COPY mvnw* ./
COPY .mvn* .mvn 2>/dev/null || true

# Install system Maven as fallback
RUN apk add --no-cache maven

# Download dependencies
RUN if [ -f "./mvnw" ]; then \
        ./mvnw dependency:go-offline -B; \
    else \
        mvn dependency:go-offline -B; \
    fi || true

# Copy source
COPY src ./src

# Build (use wrapper if available, otherwise system maven)
RUN if [ -f "./mvnw" ]; then \
        ./mvnw clean package -DskipTests -B; \
    else \
        mvn clean package -DskipTests -B; \
    fi

# Runtime stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]