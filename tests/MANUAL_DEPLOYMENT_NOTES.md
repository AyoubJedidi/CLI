# Manual Deployment Notes

## Node.js (Port 3000)
```bash
cd test-node-app
npm install
npm start
# Opens firewall: sudo ufw allow 3000
```

## Python/Flask (Port 5000)
```bash
cd test-flask-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
# Or: gunicorn -b 0.0.0.0:5000 app:app
# Opens firewall: sudo ufw allow 5000
```

## Java/Maven (Port 8080)
```bash
cd test-java-maven
./mvnw clean package -DskipTests
java -jar target/*.jar
# Opens firewall: sudo ufw allow 8080
```

## Java/Gradle (Port 8082)
```bash
cd test-java-gradle
./gradlew clean build -x test
java -Dserver.port=8082 -jar build/libs/*.jar
# Opens firewall: sudo ufw allow 8082
```

## .NET (Port 5001)
```bash
cd test-dotnet-webapp
dotnet build
dotnet run --urls "http://localhost:5001"
# Opens firewall: sudo ufw allow 5001
```

## Nginx Setup
```bash
sudo apt-get install -y nginx
sudo cp test-apps.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/test-apps /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Ansible Tasks to Create

1. Install runtime (node, python, java, dotnet, nginx)
2. Create app directories
3. Copy application files
4. Install dependencies
5. Configure service files (systemd)
6. Start services
7. Configure nginx
8. Open firewall ports
