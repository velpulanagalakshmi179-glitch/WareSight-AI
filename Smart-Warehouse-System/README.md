# Smart Warehouse Operations & Order Fulfillment System

> An intelligent warehouse platform that turns inventory and fulfillment data into real-time operational decisions.

---

## 🚀 What Makes Our Solution Different

Traditional warehouse management systems (WMS) focus primarily on data entry and passive information display (CRUD operations). Our solution goes further by actively helping warehouse operators and managers make key fulfillment decisions. 

Rather than just reporting numbers, this platform converts live warehouse events into actionable operational decisions:
- **Dynamic Order Prioritization**: Calculates real-time priority scores based on customer tier, SLA status, time-to-deadline, and product constraints.
- **Inventory Allocation Logic**: Evaluates competing demands and decides how available stock is distributed.
- **Low-Stock & Reorder Alerts**: Instantly triggers reorder-level alerts and flags stockout risks before they disrupt workflows.
- **Exception ➔ Decision ➔ Resolution Engine**: Manages pipeline anomalies (damaged items, missing products, quality fails) by presenting alternative action paths to humans.
- **Route Optimization**: Displays picker path sequencing metrics to decrease zone congestion.
- **Mini KPIs & Operational Analytics**: Provides workforce performance, dispatch status, bottleneck analysis, and exception trends directly to managers.

---

## 🛠️ Core Modules

### 🗃️ Inventory Management
- **Live Stock Levels**: Real-time tracking of available, reserved, allocated, missing, and damaged units.
- **Product Visualizations**: Displays high-fidelity product images and thumbnails with full upload and modal zoom interactions.
- **Reorder alerts**: Triggers automated reorder and safety stock indicators.

### 📦 Order Management
- **Dynamic Allocations**: Manages manual and automated order entries.
- **Shortage Scenarios**: Handles complex scenarios (e.g. an urgent SLA order requesting 10 units when only 7 are available) by identifying donor packages and executing recovery plans.

### 👷 Role-Based Workflows
- **Picking**: A priority-sorted picking task list showing zone/bin numbers, route indexing, product photos, and route optimization metrics.
- **Packing**: Checklist-driven package assembly and checklist verification.
- **Quality Control (QC)**: Verification dock supporting pass/fail actions and logging failure causes.
- **Dispatch**: Outbound shipping queue managing courier assignments, tracking generation, and status updates.

---

## 📊 Operational Intelligence (Analytics)
The dashboard features integrated **Chart.js** data-driven graphs to evaluate warehouse performance:
- **Inventory Movement**: Comparison of received vs. dispatched items.
- **Orders Timeline**: Daily orders created trends.
- **Dispatch Metrics**: Track courier dispatches over time.
- **Priority & Category Distributions**: Clear breakdown of incoming demand and catalog valuation.
- **Workforce Performance**: Logs order fulfillment counts per worker to optimize picker/packer assignments.

---

## 👥 Role-Based Access Control (RBAC)

| Role | Username | Password | Responsibility |
|------|----------|----------|----------------|
| **Manager** | `demo_manager` | `demo123` | Dashboard metrics, Control Tower Twin, recovery decisions, and rules settings. |
| **Picker** | `demo_picker` | `demo123` | Dynamic picking tasks, Optimized Routes, and item verification. |
| **Packing Staff** | `demo_packer` | `demo123` | Order packaging checks and verification steps. |
| **QC Staff** | `demo_qc` | `demo123` | Quality checks, rejections handling, and dock inspections. |
| **Dispatch Staff** | `demo_dispatch` | `demo123` | Courier logistics, carrier assignment, and tracking validation. |

---

## 🔄 End-to-End Workflow

```
       Order Created
             ↓
    Priority Determined
             ↓
     Inventory Checked
             ↓
    Inventory Allocated
             ↓
         Picking (Optimized Path)
             ↓
          Packing (Checklist)
             ↓
       Quality Check (Pass/Fail)
             ↓
         Dispatch (Outbound Courier)
             ↓
     Inventory / Analytics Updated
```

#### Exception Resolution Path:
```
  Exception Encountered (e.g., QC Fail / Insufficient Stock)
                           ↓
             Manager Alerted (Control Tower)
                           ↓
              Decision Option Presented
                           ↓
             Resolution Executed (SQLite Update)
                           ↓
               Standard Workflow Resumes
```

---

## 💻 Technology Stack & Architecture

- **Backend**: FastAPI (Python), SQLite
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+), Chart.js
- **Unit Tests**: pytest, starlette TestClient
- **Routing & Deployment**: Render configuration (`render.yaml`)

```
   [Browser Client] ➔ (JSON REST API) ➔ [FastAPI Backend] ➔ [SQLite DB]
```

---

## 📁 Project Structure

```
Smart-Warehouse-System/
├── backend/
│   ├── app.py              # FastAPI server, endpoints, and database seed
│   ├── requirements.txt    # Backend library requirements
│   └── warehouse.db        # SQLite database file
├── frontend/
│   └── index.html          # HTML, Tailwind theme, and Javascript modules
├── tests/
│   └── test_smoke.py       # pytest smoke testing suites
├── render.yaml             # Render deployment configuration
├── requirements.txt        # Root library requirements
├── start.bat               # Windows batch script
└── README.md               # Project documentation
```

---

## 🔧 Installation & Local Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Smart-Warehouse-System/Smart-Warehouse-System
   ```

2. **Configure environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Server**:
   ```bash
   python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
   ```
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🧪 Testing

Execute the automated test suite containing **22 integration test points**:
```bash
python -m pytest
```

---

## 🚀 Render Deployment Setup

To deploy the application successfully online using **Render**:

1. **Create Web Service**: Set up a new Python Web Service on Render and point it to your repository.
2. **Configure Commands**:
   - **Build Command**: 
     ```bash
     pip install --upgrade pip && pip install --prefer-binary --only-binary=:all: -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     python -m uvicorn backend.app:app --host 0.0.0.0 --port $PORT
     ```
3. **Configure Environment Variables**:
   - `PYTHON_VERSION`: `3.10.12` (or your target python version)
   - `WAREHOUSE_DB`: `backend/warehouse.db`
4. **Health Check Path**: Point the Render healthCheckPath parameter to `/api/health`.

### 🛡️ Troubleshooting PyPI 502 / Rust Compilation Errors
If the installation fails while building `pydantic-core` from source, the `--only-binary=:all:` flag forces Pip to search exclusively for precompiled wheels. This prevents pip from attempting Rust-based builds on Render's ephemeral containers.

### 💾 SQLite Persistence Note on Render
Please note that Render web services run on ephemeral disks. Any file writes to `warehouse.db` at runtime (such as newly registered users, updated inventory levels, or QC pass/fail state transitions) will be reset when the server restarts or goes to sleep. For production persistence, configure Render Persistent Disk storage mounts.

---

## 🔮 Future Enhancements (Roadmap)
- **Predictive Demand Forecasting**: Machine Learning models forecasting stockouts based on temporal factors.
- **Computer Vision QC**: Real-time camera feeds automatically identifying damaged boxes or packaging tear.
- **IoT Sensors**: Zone and shelf humidity/temperature tracking integrated into the Control Tower Digital Twin.
