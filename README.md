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

### 1. Clone
```bash
git clone https://github.com/<your-user>/ocpp-backend.git
cd ocpp-backend
```
### 2. Create virtualenv & install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3. Configure environment variables
Create a `.env` file in the project root:
```ini
SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
OCPP_WS_HOST=0.0.0.0
OCPP_WS_PORT=9000

DB_HOST=localhost
DB_PORT=5432
DB_NAME=ocpp
DB_USER=postgres
DB_PASSWORD=password
```

### 4. Setup database
Make sure you have PostgreSQL running and a database created. Then run:
```bash
python manage.py migrate
```
### 5. Create superuser
```bash
python manage.py createsuperuser
```

### 6. Run the server
```bash
python manage.py runserver
```


### 7. Start OCPP WebSocket server
In a separate terminal, run:
```bash
python manage.py run_ocpp_server
```

### 8. Access the app
- Admin → http://localhost:8000/admin/
- API → http://localhost:8000/api/
- Swagger → http://localhost:8000/swagger/
- ReDoc → http://localhost:8000/redoc/
- Dashboard → http://localhost:8000/dashboard/
- Prometheus metrics → http://localhost:8000/metrics/
API
- GET /api/chargers/ → list all chargers (DB)
- GET /api/chargers/active/ → currently connected chargers
- POST /api/chargers/{id}/start/ → remote start (JWT required)
- POST /api/chargers/{id}/stop/ → remote stop (JWT required)
- GET /api/transactions/ → recent transactions
- GET /api/logs/ → recent logs
Auth
- POST /api/token/ → obtain JWT 
- POST /api/token/refresh/ → refresh JWT

---
## 🧪 Testing
Run tests with pytest:
```bash
pytest
```
Coverage report:
```bash
pytest --cov=.
```
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


