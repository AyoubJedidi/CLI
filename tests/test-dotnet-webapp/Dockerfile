# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src


# Copy all project folders containing csproj files

# Restore dependencies
RUN dotnet restore

# Copy everything else and build
COPY . .
WORKDIR /src
RUN dotnet build --configuration Release --no-restore

# Publish
RUN dotnet publish --configuration Release --output /app/publish --no-build

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

COPY --from=build /app/publish .

# Expose port
EXPOSE 8080

# Set environment variables
ENV ASPNETCORE_URLS=http://+:8080

ENTRYPOINT ["dotnet", "test-dotnet-webapp.dll"]

