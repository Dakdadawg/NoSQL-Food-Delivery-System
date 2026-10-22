# FoodDash: Distributed Food Delivery Management System

A full-stack food delivery operations platform engineered to manage the transactional lifecycle across customers, restaurant kitchens, and delivery logistics partners. The system utilizes a document-oriented architecture implemented in MongoDB and interfaces through a reactive, multi-tenant dashboard built with Streamlit.

---

## Technical Overview

The platform addresses high-concurrency read/write operations by migrating traditional Third Normal Form (3NF) relational models to an embedded document structure.

* **Elimination of Multi-Table Relational Joins:** Normalized one-to-many relationships (order line items, menu structures, and multivalued contact directories) are embedded directly within parent documents as BSON arrays, reducing query latency during transactional reads.
* **State Synchronization:** Atomic update operations (`$set`, `$push`) maintain state consistency across customer order placements, kitchen preparation queues, and driver pickups without deadlocks.
* **NoSQL Analytical Pipelines:** Core database operations leverage MongoDB aggregation pipelines (`$group`, `$lookup`, `$unwind`, `$project`) to compute real-time operational metrics and historical performance indicators.

---

## System Modules

### 1. Customer Interface
* **Dynamic Identity Onboarding:** Handles new user registrations capturing composite physical addresses and multivalued contact numbers without static seeding.
* **Menu Exploration & Stock Constraints:** Reads active restaurant collections with client-side verification of item availability flags.
* **Transaction Engine:** Manages session-based cart state, calculates sub-totals and order tier classifications (Small, Medium, Large), and generates simulated transactional records with tracking identifiers.
* **Feedback Loop:** Provides two-way rating mechanisms for restaurant food preparation and logistics performance following completed deliveries.

### 2. Restaurant Operations Interface
* **Kitchen Order Queue:** Tracks incoming orders through structured operational states (`Received` -> `Preparing` -> `Ready for Pickup` -> `Dispatched`).
* **Catalog Management:** Enables direct inventory controls to toggle dish availability (`is_available`) or append new items to embedded menu arrays.
* **Merchant Onboarding:** Provisions new restaurant entries with custom regional cuisines, operational metadata, and menu definitions.

### 3. Logistics Partner Interface
* **Pickup Dispatch Pool:** Exposes unassigned orders meeting kitchen preparation criteria to active delivery partners.
* **Assignment Workflow:** Binds driver IDs to specific delivery sub-documents atomically to prevent duplicate dispatches.
* **Fulfillment Tracking:** Manages order transitions to final delivery, logs completion timestamps, and reconciles cash-on-delivery payment statuses.
* **Driver Onboarding:** Registers delivery personnel with identity verification details and contact records.

### 4. Database Analytics & Auditing
* **Real-Time KPIs:** Computes gross platform revenue and average order value via grouping aggregations.
* **Distribution Reports:** Evaluates order volumes and gross merchandise value (GMV) per restaurant entity using multi-stage lookups.
* **End-to-End System Audit:** Performs cross-collection joins between orders, customers, and restaurants to provide a single-pane-of-glass administrative audit log.

---

## Technology Stack

* **Frontend:** Streamlit, Pandas
* **Backend:** Python 3.10+, PyMongo Driver
* **Database:** MongoDB Community Server (v6.0+)
* **Environment:** Virtualenv / Git

---

## Schema Architecture

```text
food_delivery_da3/
|-- customers/
|   |-- customer_id (PK)
|   |-- name (first, middle, last)
|   |-- dob, email
|   |-- address { street, city, state, pin }
|   \-- mobile_numbers [ string ]
|
|-- restaurants/
|   |-- restaurant_id (PK)
|   |-- name, cuisine, email, phone_num
|   |-- address { street, city, state, pin }
|   \-- menu [ { item_id, item_name, description, price, is_available } ]
|
|-- delivery_riders/
|   |-- rider_id (PK)
|   |-- name, email, license_num, avg_rating
|   \-- phone_numbers [ string ]
|
\-- orders/
    |-- order_id (PK)
    |-- customer_id (FK), restaurant_id (FK)
    |-- order_date, order_time, total_amt, kitchen_status
    |-- items [ { item_id, item_name, qty, unit_price, sub_total } ]
    \-- delivery { rider_id, delivery_time, is_completed, payment_status, ratings }
```

---

## Installation & Execution

### 1. Prerequisites
* Python 3.10 or higher
* Local MongoDB daemon running on default port `27017`

### 2. Repository Setup
```bash
git clone https://github.com/Dakdadawg/NoSQL-Food-Delivery-System.git
cd fooddash-dbms
```

### 3. Environment Configuration
```bash
# Set up virtual environment
python -m venv venv

# Activate environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install project dependencies
pip install -r requirements.txt
```

### 4. Database Initialization
Seed the initial restaurant catalogs and active driver pools:
```bash
python db_setup.py
```

### 5. Application Launch
```bash
streamlit run app.py
```
Access the application dashboard via the local URL: `http://localhost:8501`.
