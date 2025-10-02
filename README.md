# OCPP Backend (Django + DRF + OCPP 1.6)

This project is a backend module for managing Electric Vehicle (EV) chargers over **OCPP 1.6 JSON**.  
It includes a **WebSocket OCPP Central System server**, a **Django + DRF REST API**, database persistence, JWT authentication, Prometheus monitoring, and Swagger API docs.

---

## 🚀 Features

- OCPP 1.6 Central System server (async websockets)
- Handles **BootNotification, Heartbeat, Authorize, Start/StopTransaction**
- Supports backend control: **RemoteStartTransaction** and **RemoteStopTransaction**
- REST API (Django REST Framework) for:
  - Listing chargers, transactions, logs
  - Triggering remote commands
  - Viewing active charger sessions
- JWT authentication (SimpleJWT)
- Swagger (`/swagger/`) & ReDoc (`/redoc/`) docs
- Prometheus metrics at `/metrics/`
- Minimal dashboard at `/dashboard/`
- 100% test coverage with pytest

---

## 🛠 Setup

Choose one of the following setup methods:

### Option A: 🐳 Docker Setup (Recommended)

#### 1. Clone the repository
```bash
git clone https://github.com/amgad-23/ocpp_backend.git
cd ocpp-backend
```

#### 2. Create environment file
Create a `.env` file in the project root:
```ini
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-change-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*

# Database Configuration (for Docker)
DB_HOST=db
DB_PORT=5432
DB_NAME=ocpp
DB_USER=ocpp
DB_PASSWORD=ocpp

# OCPP WebSocket Server Configuration
OCPP_WS_HOST=0.0.0.0
OCPP_WS_PORT=9000
```

#### 3. Start all services with Docker Compose
```bash
# Build and start all services (PostgreSQL, Django API, OCPP WebSocket server)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

#### 4. Create Django superuser (optional)
```bash
docker-compose exec web python manage.py createsuperuser
```

### Option B: 🐍 Local Python Setup

#### 1. Clone the repository
```bash
git clone https://github.com/<your-user>/ocpp-backend.git
cd ocpp-backend
```

#### 2. Create virtual environment & install dependencies
```bash
python3 -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### 3. Configure environment variables
Create a `.env` file in the project root:
```ini
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-change-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*

# Database Configuration (for local PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ocpp
DB_USER=postgres
DB_PASSWORD=password

# OCPP WebSocket Server Configuration
OCPP_WS_HOST=0.0.0.0
OCPP_WS_PORT=9000
```

#### 4. Setup PostgreSQL database
Make sure you have PostgreSQL installed and running, then create the database:
```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE ocpp;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ocpp TO postgres;
```

#### 5. Run Django migrations
```bash
python manage.py migrate
```

#### 6. Create Django superuser
```bash
python manage.py createsuperuser
```

#### 7. Start the Django API server
```bash
python manage.py runserver
```

#### 8. Start OCPP WebSocket server (in separate terminal)
```bash
# Activate virtual environment first
python ocpp_server/server.py
```

### 🌐 Access the Application
- Admin → http://localhost:8000/admin/
- API → http://localhost:8000/api/
- Swagger → http://localhost:8000/swagger/
- ReDoc → http://localhost:8000/redoc/
- Dashboard → http://localhost:8000/dashboard/
- Prometheus metrics → http://localhost:8000/metrics/
## 📋 API Endpoints

### Public Endpoints
- **GET** `/api/chargers/` → List all registered chargers
- **GET** `/api/chargers/active/` → Currently connected chargers
- **GET** `/api/transactions/` → Recent transactions
- **GET** `/api/logs/` → Recent event logs

### Protected Endpoints (JWT Required)
- **POST** `/api/chargers/{id}/start/` → Remote start charging
- **POST** `/api/chargers/{id}/stop/` → Remote stop charging

### Authentication
- **POST** `/api/token/` → Obtain JWT token
- **POST** `/api/token/refresh/` → Refresh JWT token

### Example API Usage
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Start charging (with JWT token)
curl -X POST http://localhost:8000/api/chargers/EVSE-001/start/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_tag": "RFID123"}'
```

---

## 🧪 Testing & Development

### Running Tests
```bash
# For Docker setup
docker-compose exec web pytest

# For local Python setup
pytest

# With coverage report
pytest --cov=.
```

### Testing OCPP Connection
You can test the OCPP WebSocket server using an OCPP simulator or simple WebSocket client:

```bash
# Test WebSocket connection
wscat -c ws://localhost:9000/EVSE-TEST -s ocpp1.6

# Send BootNotification (after connection)
[2,"unique-id","BootNotification",{"chargePointModel":"TestModel","chargePointVendor":"TestVendor"}]
```

### Development Commands
```bash
# For Docker setup
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic

# For local Python setup
python manage.py shell
python manage.py migrate
python manage.py collectstatic
```

### Troubleshooting

#### Docker Issues
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs web
docker-compose logs ocpp
docker-compose logs db

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Database Issues
```bash
# Reset database (Docker)
docker-compose down -v
docker-compose up -d

# Reset database (Local)
python manage.py flush
python manage.py migrate
```

#### OCPP Connection Issues
- Ensure WebSocket server is running on port 9000
- Check firewall settings
- Verify OCPP client uses subprotocol `ocpp1.6`
- Check logs for connection errors

---
## 📈 Monitoring
Prometheus metrics are available at `/metrics/`.
Configure Prometheus to scrape this endpoint for monitoring.
---
## 📝 API Documentation
Swagger UI: `/swagger/`
ReDoc: `/redoc/`
---

## 🖥 Dashboard
A minimal dashboard is available at `/dashboard/` for quick insights into charger status and activity.
---
## 🤝 Contributing
Contributions are welcome! Please open issues or pull requests for improvements or bug fixes.
---
## ⚖️ License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
---
## 🙏 Acknowledgements
Thanks to the open-source community for the libraries and tools that made this project possible!
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

## Project Structure
```
ocpp-backend/
├── ocpp_backend/          # Main Django project
│   ├── settings.py       # Django settings
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── chargers/             # Chargers app
│   ├── apps.py         # Chargers app config
│   ├── repositories.py  # Charger repositories
│   ├── services.py      # Charger services
│   ├── models.py        # Charger models
│   ├── views.py         # Charger views
│   ├── admin.py         # Charger admin
│   ├── tests.py         # Charger tests
│   ├── api/
│   │   ├── views.py     # API views
│   │   ├── serializers.py  # API serializers
│   │   └── urls.py      # API URLs
│   ├── migrations/      # Database migrations
│   └── templates/      # Charger templates
├── ocpp_server/
│   ├── app_django.py  # ASGI app for OCPP server
│   ├── charge_point.py  # ChargePoint class
│   ├── registry.py    # ChargePoint registry
│   └── server.py   # WebSocket server


