# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy project file first
COPY *.csproj ./

# Restore dependencies
RUN dotnet restore

# Copy everything else
COPY . ./

# Build
RUN dotnet build -c Release --no-restore

# Publish
RUN dotnet publish -c Release -o /app/publish --no-restore

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Copy published app
COPY --from=build /app/publish .

EXPOSE 8080

ENTRYPOINT ["dotnet", "test-dotnet-webapp.dll"]
