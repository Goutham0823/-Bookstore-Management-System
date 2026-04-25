# 📚 Bookstore Management System — REST API

A production-ready RESTful API built with **Django REST Framework**, featuring JWT authentication, role-based access control, search/filtering, pagination, and auto-generated Swagger documentation.

---

## 🚀 Quick Start

### 1. Clone and enter the project
```bash
git clone https://github.com/Goutham0823/-Bookstore-Management-System.git
cd -Bookstore-Management-System
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run database migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (optional — for Django Admin)
```bash
python manage.py createsuperuser
```

### 6. Start the development server
```bash
python manage.py runserver
```

---

## 🌐 API Endpoints

### Authentication
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/register/` | Public | Register a new user |
| POST | `/api/login/` | Public | Login and get JWT tokens |
| GET | `/api/profile/` | Authenticated | Get current user profile |
| POST | `/api/token/refresh/` | Authenticated | Refresh access token |

### Books
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/books/` | Public | List all books (paginated, searchable) |
| GET | `/api/books/{id}/` | Public | Get book details |
| POST | `/api/books/` | Admin | Add a new book |
| PUT | `/api/books/{id}/` | Admin | Update a book |
| PATCH | `/api/books/{id}/` | Admin | Partially update a book |
| DELETE | `/api/books/{id}/` | Admin | Delete a book |

### Orders
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/orders/` | Admin | List all orders |
| POST | `/api/orders/` | Customer | Place a new order |
| GET | `/api/orders/{id}/` | Owner or Admin | Get order details |
| PUT | `/api/orders/{id}/status/` | Admin | Update order/payment status |

### Docs
| URL | Description |
|-----|-------------|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI JSON schema |
| `/admin/` | Django Admin |

---

## 🔍 Search & Filtering

Books support:
- `?search=<query>` — full-text search on title, author, genre
- `?genre=Technology` — exact genre filter
- `?min_price=10&max_price=50` — price range
- `?in_stock=true` — only in-stock books
- `?ordering=-price` — sort by field (prefix `-` for descending)
- `?page=2` — pagination (10 items per page)

---

## 🔐 Authentication

The API uses **JWT (JSON Web Token)** authentication via `djangorestframework-simplejwt`.

1. Login at `POST /api/login/` to receive `access` and `refresh` tokens.
2. Include the access token in the `Authorization` header:
   ```
   Authorization: Bearer <access_token>
   ```
3. Access tokens expire in **1 hour**; use `POST /api/token/refresh/` to renew.

---

## 👥 Roles

| Role | Capabilities |
|------|--------------|
| **CUSTOMER** | Browse books, place orders, view own orders |
| **ADMIN** | Full book CRUD, view all orders, update order status |

---

## 🧪 Running Tests

```bash
pytest
# With verbose output
pytest -v
# With coverage
pytest --tb=short
```

---

## 📮 Postman Collection

Import `postman_collection.json` into Postman:
1. Open Postman → **Import** → select the file
2. Set the `base_url` variable to `http://127.0.0.1:8000`
3. Run **"Login"** — access token is saved automatically
4. Use all other endpoints with auth handled via `{{access_token}}`

---

## 🖼 Screenshots

You can include project screenshots in `docs/screenshots/`.

Example markdown:

```md
![Swagger UI](docs/screenshots/swagger-ui.png)
![Books Endpoint](docs/screenshots/books-endpoint.png)
```

---

## 📁 Project Structure

```
book-management-system/
├── manage.py
├── requirements.txt
├── .env
├── pytest.ini
├── postman_collection.json
├── bookstore/          # Project settings
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── accounts/       # JWT auth, custom User model
│   ├── books/          # Book CRUD, search, filtering
│   └── orders/         # Order management
└── tests/              # pytest test suite
```

---

## 🛠 Tech Stack

- **Backend**: Python, Django 4.2, Django REST Framework
- **Auth**: JWT via `djangorestframework-simplejwt`
- **Database**: SQLite (dev) — easily switch to PostgreSQL via `.env`
- **Docs**: Swagger UI + ReDoc via `drf-spectacular`
- **Filtering**: `django-filter`
- **Testing**: `pytest-django`
