<![CDATA[<div align="center">

# 🏠 Easykirai

### Rent Smart. Study Hard.

**Dehradun's #1 Student Rental Platform**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Razorpay](https://img.shields.io/badge/Razorpay-02042B?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

*A full-stack web application that connects students in Dehradun with local retailers, enabling affordable monthly rentals of furniture, electronics, and study essentials — eliminating the burden of buying expensive items for short-term use.*

</div>

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution](#-solution)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Database Schema](#-database-schema)
- [API Routes](#-api-routes)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Problem Statement

Students relocating to Dehradun for education face a recurring challenge — they need essential items like **furniture, electronics, and study gear** for the duration of their course, but **buying them is expensive and impractical** for short-term stays. On the other hand, local retailers have inventory that sits idle without a streamlined channel to reach student customers.

## 💡 Solution

**Easykirai** bridges the gap between students and local retailers through a **rental marketplace** that allows:

- **Students** to browse, request, and rent items on a **monthly basis** at affordable rates
- **Retailers** to list their products, manage incoming rental requests, and track earnings — all from a dedicated dashboard

The platform handles the entire lifecycle: **discovery → request → approval → payment → tracking**.

---

## ✨ Key Features

### 🎓 Student Portal
| Feature | Description |
|---------|-------------|
| **Smart Home Dashboard** | View active rentals, monthly spending, nearby dealers, and savings at a glance |
| **Product Browsing** | Filter products by category — Furniture, Electronics, Study essentials |
| **Product Details** | View detailed descriptions, pricing, and retailer info before renting |
| **Rental Requests** | Send rental requests with custom duration (in months) |
| **My Rentals Tracker** | Track orders across all states — Pending, Active, Completed, Rejected |
| **Secure Payments** | Pay via Razorpay integration (INR) |
| **User Profile** | View rental history, total spend, and account details |
| **Wishlist & Messages** | Save favorite items and communicate (future feature placeholders) |

### 🏪 Retailer Portal
| Feature | Description |
|---------|-------------|
| **Business Dashboard** | Monitor total products, orders, active rentals, and earnings |
| **Product Management** | Full CRUD — Add, Edit, Delete products with category, price, images |
| **Order Management** | Accept or reject incoming student requests with notes & delivery estimates |
| **Earnings Tracking** | Automatically calculated from active paid rentals |

### 🔐 Authentication & Security
- Separate registration and login flows for **Students** and **Retailers**
- Password hashing using **Werkzeug** (PBKDF2-SHA256)
- Session-based authentication with role-based access control
- Decorator-based route protection (`@student_login_required`, `@retailer_login_required`)

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Flask (Python) | Web framework, routing, business logic |
| **ORM** | Flask-SQLAlchemy | Database models and queries |
| **Database** | SQLite | Lightweight relational storage |
| **Auth** | Werkzeug Security | Password hashing & verification |
| **Payments** | Razorpay Python SDK | Payment gateway integration |
| **Frontend** | Jinja2 Templates | Server-side HTML rendering |
| **Styling** | Custom CSS | Responsive UI with sidebar layout |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                         │
│   Landing Page  │  Student Portal  │  Retailer Portal           │
└────────┬────────┴────────┬─────────┴────────┬───────────────────┘
         │                 │                  │
         ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FLASK APPLICATION (app.py)                  │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐  │
│  │ Auth Module   │  │ Student Routes│  │  Retailer Routes     │  │
│  │ ─ Login       │  │ ─ /home       │  │  ─ /retailer/dash    │  │
│  │ ─ Register    │  │ ─ /products   │  │  ─ /retailer/products│  │
│  │ ─ Logout      │  │ ─ /my-rentals │  │  ─ /retailer/orders  │  │
│  │ ─ Decorators  │  │ ─ /profile    │  │  ─ CRUD operations   │  │
│  └──────────────┘  └───────────────┘  └──────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                  Payment Module (Razorpay)               │    │
│  │    /payment/create/:id  ─►  /payment/verify              │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              SQLAlchemy ORM + SQLite Database                    │
│   ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐      │
│   │ Students │  │ Retailers │  │ Products │  │  Orders  │      │
│   └──────────┘  └───────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### Entity Relationship

```
Students ──< Orders >── Products ──> Retailers
                │                       │
                └───────────────────────┘
                    (retailer_id FK)
```

### Models

#### `Student`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key |
| `full_name` | String(120) | Not Null |
| `father_name` | String(120) | Not Null |
| `phone` | String(30) | Unique, Not Null |
| `aadhaar_number` | String(20) | Not Null |
| `city` | String(100) | Default: "Dehradun" |
| `password_hash` | String(255) | Not Null |
| `created_at` | DateTime | Auto-generated |

#### `Retailer`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key |
| `contact_name` | String(120) | Not Null |
| `phone` | String(30) | Unique, Not Null |
| `shop_name` | String(120) | Not Null |
| `gstin` | String(20) | Not Null |
| `business_address` | Text | Not Null |
| `city` | String(100) | Default: "Dehradun" |
| `password_hash` | String(255) | Not Null |
| `created_at` | DateTime | Auto-generated |

#### `Product`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key |
| `retailer_id` | Integer | Foreign Key → Retailers |
| `name` | String(120) | Not Null |
| `category` | String(80) | Not Null (Furniture / Electronics / Study) |
| `description` | Text | Not Null |
| `price_per_month` | Numeric(10,2) | Default: 0 |
| `status` | String(20) | Default: "AVAILABLE" |
| `image_url` | String(255) | Nullable |
| `created_at` | DateTime | Auto-generated |

#### `Order`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary Key |
| `student_id` | Integer | Foreign Key → Students |
| `product_id` | Integer | Foreign Key → Products |
| `retailer_id` | Integer | Foreign Key → Retailers |
| `duration_months` | Integer | Not Null |
| `status` | String(20) | PENDING / ACTIVE / REJECTED / COMPLETED / CANCELLED |
| `retailer_note` | Text | Nullable |
| `expected_delivery` | String(120) | Nullable |
| `razorpay_order_id` | String(100) | Nullable |
| `payment_status` | String(20) | UNPAID / PAID |
| `created_at` | DateTime | Auto-generated |

---

## 🌐 API Routes

### Public Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Landing page (role-based redirect) |

### Student Routes (🔒 Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/student/login` | Student login |
| `GET/POST` | `/student/register` | Student registration |
| `GET` | `/home` | Student dashboard |
| `GET` | `/products` | Browse products (with category filter) |
| `GET` | `/product/<id>` | Product detail page |
| `POST` | `/request/<id>` | Send rental request |
| `GET` | `/my-rentals` | View all rental orders |
| `GET` | `/profile` | Student profile |
| `GET` | `/wishlist` | Wishlist (placeholder) |
| `GET` | `/messages` | Messages (placeholder) |
| `GET` | `/settings` | Settings (placeholder) |
| `GET` | `/logout` | Logout |

### Retailer Routes (🔒 Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/retailer/login` | Retailer login |
| `GET/POST` | `/retailer/register` | Retailer registration |
| `GET` | `/retailer/dashboard` | Business dashboard |
| `GET` | `/retailer/products` | Manage products listing |
| `GET/POST` | `/retailer/products/add` | Add new product |
| `GET/POST` | `/retailer/products/<id>/edit` | Edit product |
| `POST` | `/retailer/products/<id>/delete` | Delete product |
| `GET` | `/retailer/orders` | View all orders |
| `POST` | `/retailer/orders/<id>/accept` | Accept order |
| `POST` | `/retailer/orders/<id>/reject` | Reject order |

### Payment Routes (🔒 Auth Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/payment/create/<order_id>` | Create Razorpay payment order |
| `POST` | `/payment/verify` | Verify payment completion |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** installed on your system
- **pip** (Python package manager)
- A **Razorpay** account (optional — app works with mock payments)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Easykirai.com.git
   cd Easykirai.com
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Razorpay keys** *(optional)*

   Open `app.py` and replace the placeholder keys with your Razorpay credentials:
   ```python
   RAZORPAY_KEY_ID = "your_key_id"
   RAZORPAY_KEY_SECRET = "your_key_secret"
   ```
   > **Note:** The app includes a fallback mock payment flow, so it works even without valid Razorpay keys.

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open in browser**
   ```
   http://127.0.0.1:5000/
   ```

---

## 📁 Project Structure

```
Easykirai.com/
│
├── app.py                  # Main Flask application (routes, models, logic)
├── init_db.py              # Database initialization script
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
├── instance/
│   └── easykirai.db        # SQLite database (auto-generated)
│
├── static/
│   └── css/
│       └── style.css       # Custom stylesheet (responsive sidebar layout)
│
└── templates/
    ├── base.html                # Base layout (sidebar + topbar + content)
    │
    ├── landing.html             # Landing page (role selection)
    ├── student_login.html       # Student login form
    ├── student_register.html    # Student registration form
    ├── retailer_login.html      # Retailer login form
    ├── retailer_register.html   # Retailer registration form
    │
    ├── home.html                # Student dashboard (stats + products)
    ├── products.html            # Product catalog with category filter
    ├── product_detail.html      # Individual product page
    ├── my_rentals.html          # Student rental tracking
    ├── profile.html             # Student profile page
    ├── wishlist.html            # Wishlist (placeholder)
    ├── messages.html            # Messages (placeholder)
    ├── settings.html            # Settings (placeholder)
    │
    ├── retailer_dashboard.html  # Retailer business dashboard
    ├── retailer_products.html   # Retailer product management
    ├── retailer_product_form.html # Add/Edit product form
    └── retailer_orders.html     # Retailer order management
```

---

## 📸 Screenshots

| Landing Page | Student Dashboard | Product Catalog |
|:---:|:---:|:---:|
| Role selection for Student/Retailer | Stats, featured products, quick actions | Browse & filter by category |

| Retailer Dashboard | Order Management | Product Detail |
|:---:|:---:|:---:|
| Earnings, orders, product summary | Accept/reject with notes & delivery | Full info, pricing, request rental |

---

## 🔮 Future Enhancements

- [ ] **Image Uploads** — Allow retailers to upload product images (currently URL-based)
- [ ] **Real-time Messaging** — In-app chat between students and retailers
- [ ] **Wishlist Functionality** — Save and track favorite products
- [ ] **Search & Advanced Filters** — Search by name, price range, location
- [ ] **Email/SMS Notifications** — Order status updates via email/SMS
- [ ] **Multi-city Expansion** — Support for cities beyond Dehradun
- [ ] **Admin Panel** — Platform admin to manage users, disputes, and analytics
- [ ] **Rating & Reviews** — Students can rate retailers and products
- [ ] **Responsive Mobile UI** — PWA or dedicated mobile app
- [ ] **Environment Variables** — Move secrets (SECRET_KEY, Razorpay keys) to `.env`

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---



---

<div align="center">

**Built with ❤️ for students in Dehradun**

*Easykirai — Making student life affordable, one rental at a time.*

</div>
