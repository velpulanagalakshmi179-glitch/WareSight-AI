# WareSight AI

WareSight AI is a smart warehouse management and fulfillment platform that provides real-time visibility across inventory, orders, picking, packing, quality control, and dispatch operations.

---

## 🚀 Live Demo

You can access the live production deployment here:

👉 **[Open Live Demo (https://waresight-ai-8.onrender.com)](https://waresight-ai-8.onrender.com)**

---

## 💡 Problem Statement

Modern warehouses face significant coordination challenges, including:
- **Poor inventory visibility**: Keeping track of available, reserved, allocated, missing, or damaged units.
- **Manual order processing**: Delay in prioritizing critical shipments or VIP customers.
- **Picking inefficiency**: Pickers wasting time due to unordered queues or lack of route information.
- **Delayed workflows**: Bottlenecks during packing, quality control (QC), and courier dispatch stages.
- **Performance monitoring**: Difficulty measuring employee productivity and identifying fulfillment bottlenecks.
- **Lack of centralized analytics**: No real-time control tower to view inventory valuations, order lifecycles, and exception statuses.

---

## 🎯 Solution

WareSight AI provides a **centralized operational dashboard** and a **connected role-based warehouse workflow** that actively helps managers and operators coordinate tasks. By converting live events into actionable items, it optimizes paths, visualizes inventory metrics, manages exceptions (such as damaged items or stockouts), and tracks worker throughput.

---

## ✨ Key Features

### Dashboard & Analytics
- **Real-Time Operational KPIs**: Live tracking of total products, active orders, safety stock levels, and active exceptions.
- **Interactive Visualizations**: Embedded Chart.js graphs mapping sales trends, order status distribution, and hourly throughput.
- **Exception Monitoring**: Instant reporting on damaged products, picking exceptions, and delayed SLAs.

### Inventory Management
- **Product Hub**: Comprehensive list of warehouse SKUs, product photos, categories, and stock statistics.
- **Stock-Level Monitoring**: Real-time counters showing available, reserved, allocated, missing, and damaged units.
- **Reorder-Level Alerts**: Automated warnings for items falling below safety thresholds.

### Order Management
- **Order Tracking**: Comprehensive logging of customer orders, business importance, and priority tiers.
- **Fulfillment States**: Real-time status updates from order creation through dispatch.

### Warehouse Operations (Role-Based Workflows)
- **Picking Queue**: List of active picks sorted by dynamic priority, with zone/bin indicators and pick path sequence indices.
- **Packing Workstation**: Step-by-step checklist to verify picked units match order parameters before wrapping.
- **Quality Control (QC)**: Fail-safe verification step supporting one-click Pass/Fail actions and exception logging.
- **Dispatch Desk**: Outbound carrier assignments, tracking number generation, and courier shipping updates.

### End-to-End Fulfillment Flow
Status transitions are strictly tracked and routed through the operational pipeline:
```
  Orders ➔ Picking ➔ Packing ➔ Quality Control (QC) ➔ Ready for Dispatch ➔ Dispatch ➔ Completed
```

### Product Images
Supports high-fidelity image thumbnails and full upload dialogs to help operators visually identify SKUs (such as laptops, keyboards, monitors) rather than relying only on text names.

---

## 📊 Analytics Summary

| Analytics | Purpose |
|---|---|
| Inventory Movement | Tracks received vs dispatched stock levels |
| Orders Created | Daily order creation trends |
| Dispatch Trend | Outbound delivery/dispatch activity over time |
| Priority Distribution | Breakdowns of Critical, High, Normal, and Low priority demand |
| Category Distribution | Inventory count categorizations (electronics, accessories, etc.) |
| Low Stock Trend | Highlights SKUs running below safety stock margins |
| Warehouse Health | Computes overall operational and queue efficiency |
| Fulfillment Delays | Highlights orders at risk of missing customer SLAs |
| Workforce Performance | Leaderboards of worker task completion metrics |
| Exception Frequencies | Analyzes the occurrences of missing, damaged, or QC-failed units |

---

## 🏗️ System Architecture

The application is built on a decoupled modular architecture:

```
[Browser Client (HTML5/CSS3/JS)] ➔ [FastAPI Backend (REST API)] ➔ [SQLite Database (Persistence)]
```

*   **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+), Chart.js (Interactive graphs).
*   **Backend**: Python, FastAPI (Highly performant ASGI web framework).
*   **Database**: SQLite (SQL query validation, indexing, and transactional integrity).
*   **Deployment**: Hosted on Render.

---

## 🔐 User Roles & Credentials

WareSight AI enforces role-based user interfaces. Log in to the demo application using the following seeded credentials:

| Role | Username | Password | Responsibility |
|---|---|---|---|
| **Warehouse Manager** | `demo_manager` | `demo123` | Control Tower analytics, rule settings, exception approvals, and inventory master controls. |
| **Picker** | `demo_picker` | `demo123` | Picking tasks, optimized zone/bin routing, and barcode confirmations. |
| **Packing Staff** | `demo_packer` | `demo123` | Checklist packaging verification and box weight logs. |
| **QC Inspector** | `demo_qc` | `demo123` | Quality checks, pass/fail logs, and packaging audits. |
| **Dispatch Agent** | `demo_dispatch` | `demo123` | Outbound carrier assignment, tracking generation, and shipping sign-offs. |

---

## 🔄 Operational Workflow

1.  **Manager** creates an order or updates rules.
2.  **Order** is automatically prioritized.
3.  **Picker** processes items based on optimized paths.
4.  **Packer** packs the verified items into parcel boxes.
5.  **QC Inspector** audits the parcel (approves or triggers exception recovery).
6.  **Dispatch Agent** assigns a carrier and ships the box.
7.  **Dashboard** analytics update dynamically.

---

## 🧪 Testing

The codebase includes an automated unit and integration test suite to verify routing integrity, business calculations, and RBAC rules:

*   **Tests Implemented**: **22 passing integration tests**
*   **Testing Tool**: `pytest`

---

## 🛠️ Technology Stack

*   **Python**: `3.11.9`
*   **FastAPI**: `0.115.6`
*   **Uvicorn**: `0.34.0`
*   **Pydantic**: `2.10.4`
*   **PyJWT**: `2.10.1`
*   **pytest**: `8.3.4`
*   **python-multipart**: `0.0.19`
*   **email-validator**: `2.2.0`

---

## 🚀 Local Setup

Follow these steps to run the project locally on your machine:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/velpulanagalakshmi179-glitch/WareSight-AI.git
    cd WareSight-AI
    ```

2.  **Set Up a Python Virtual Environment**:
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Automated Tests**:
    ```bash
    python -m pytest
    ```

5.  **Start the Local Server**:
    ```bash
    python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
    ```

6.  **Access Local Host**:
    Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🌐 Production Deployment

The project is configured for automated deployments using Render Blueprints:

*   **Production Deployment URL**: [https://waresight-ai-8.onrender.com](https://waresight-ai-8.onrender.com)
*   **Health API Check Endpoint**: [https://waresight-ai-8.onrender.com/api/health](https://waresight-ai-8.onrender.com/api/health)
*   **OpenAPI Specifications**: [https://waresight-ai-8.onrender.com/openapi.json](https://waresight-ai-8.onrender.com/openapi.json)

---

## 📁 Project Structure

```
WareSight-AI/
├── backend/
│   ├── app.py              # FastAPI server, endpoints, and database seed
│   ├── requirements.txt    # Backend library requirements redirect
│   └── warehouse.db        # SQLite database file
├── frontend/
│   └── index.html          # Frontend HTML, CSS styles, and JS dashboard logic
├── tests/
│   └── test_smoke.py       # Integration and regression test suites
├── .env.example            # Environment configurations blueprint
├── .gitignore              # Git ignore filters (build logs, cache files)
├── .python-version         # Enforces Python 3.11.9 build runtime
├── render.yaml             # Render infrastructure-as-code Blueprint
├── requirements.txt        # Root application requirements
├── runtime.txt             # Backup python runtime specifier
├── walkthrough.md          # Implementation log walkthrough
└── README.md               # Project documentation
```

---

## 🖼️ Screenshots / Demo

*Note: Visual walkthroughs and screenshots demonstrating dashboard panels and role-specific interfaces can be added here or reviewed live via the demo link.*

---

## 🏆 Hackathon Highlights

*   **Connected Multi-Role Lifecycle**: Simulates realistic, interconnected operations across picking, packing, quality control, and dispatch desks.
*   **Operational Intelligence (OI) Twin**: Real-time graphs using Chart.js to visually expose bottlenecks, exceptions, and workforce efficiency.
*   **Visual-First Operations**: Leverages image thumbnails for SKUs and workflow tasks, optimizing worker verification workflows.
*   **Production-Ready Quality**: High test coverage with 22 automated integration tests running continuously on deployment pushes.

---

## 🔮 Future Improvements

- **Predictive Demand Forecasting**: Machine Learning models forecasting stockouts based on temporal factors and sales histories.
- **Computer Vision QC**: Real-time camera feeds automatically identifying parcel damage or packaging tears at inspection docks.
- **WebSocket Synchronization**: Enable real-time, bi-directional screen updates between different warehouse role dashboards.
- **Cloud Database Migration**: Shift from SQLite to PostgreSQL for concurrent multi-write operations.

---

## 👥 Demo Instructions

1.  **Open the Live URL**: Navigate to [https://waresight-ai-8.onrender.com](https://waresight-ai-8.onrender.com).
2.  **Log in as Manager**: Use `demo_manager` / `demo123`. Explore the charts, inventory levels, active exceptions, and order grids.
3.  **Log out & Log in as Picker**: Use `demo_picker` / `demo123`. Pick an assigned item using the optimized route.
4.  **Log out & Log in as Packer**: Use `demo_packer` / `demo123`. Verify the package contents from the checklist.
5.  **Log out & Log in as QC**: Use `demo_qc` / `demo123`. Audit the packed box and hit **Pass**.
6.  **Log out & Log in as Dispatch**: Use `demo_dispatch` / `demo123`. Select a carrier, sign off, and dispatch.
7.  **Return to Manager**: View updated analytics and dispatch charts demonstrating completed fulfillment logs.

---

## 📌 Project Status

*   **Production Live Status**: `LIVE`
*   **Fulfillment Pipeline**: `FUNCTIONAL`
*   **Testing Status**: `22/22 PASSED`

---

## 🤝 Contribution

This project was built for hackathon evaluation. Contributions, feedback, and forks are welcome!

---

## 📄 License

This project is open-source. For terms of usage or licensing permissions, please refer to the project repository metadata.
