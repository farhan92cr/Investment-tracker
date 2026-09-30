# Investment Tracker

A production-ready web application for tracking and managing investment portfolios, transactions, and portfolio data through a modern web interface.

The application is deployed on **Oracle Cloud** with containerized services, automated CI/CD, centralized monitoring, health checks, and operational alerting.

---

## 🔗 Project Links

* **GitHub Repository:** https://github.com/farhan92cr/Investment-tracker
* **Live Investment Tracker:** http://130.210.42.159
* **Live Monitoring Dashboard:** http://132.226.189.195:3000/public-dashboards/baf9c5ba69ed43d482f08284a1cda3e3

> The monitoring dashboard is provided as a client-view dashboard and does not require a Grafana username or password.

---

## 📌 Project Overview

Investment Tracker provides a structured platform for managing investment-related information through a web-based application.

The system is designed with a clear separation between the frontend, backend API, and database while incorporating automated deployment and production monitoring.

### Key capabilities

* Investment and portfolio data management
* Transaction management
* REST API backend
* Web-based frontend
* PostgreSQL database
* Containerized deployment
* Reverse proxy with Nginx
* Automated GitHub Actions deployment
* Application health monitoring
* Server and container monitoring
* API metrics and performance monitoring
* Production alerting
* Database and monitoring backups

---

# 🏗️ Architecture

                         ┌─────────────────────────┐
                         │        Client           │
                         │   Web Browser / User    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │        Nginx            │
                         │     Reverse Proxy       │
                         │        Port 80           │
                         └────────────┬────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                ┌─────────────────┐       ┌─────────────────┐
                │    Frontend     │       │     Backend     │
                │   React / Vite  │       │ FastAPI / API   │
                │    Port 5173    │       │    Port 8000    │
                └─────────────────┘       └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │   PostgreSQL    │
                                          │    Database     │
                                          │    Port 5432    │
                                          └─────────────────┘


        ┌────────────────────────────────────────────────────┐
        │                Monitoring VM                        │
        │                                                    │
        │  Prometheus ───────► Grafana                       │
        │       │                 │                          │
        │       ├── Node Exporter│                          │
        │       ├── cAdvisor     │                          │
        │       ├── API Metrics  │                          │
        │       └── Blackbox     │                          │
        │                                                    │
        └────────────────────────────────────────────────────┘


---

# ☁️ Infrastructure

The production application is hosted on **Oracle Cloud Infrastructure (OCI)**.

### Production environment

* Oracle Cloud VM
* Ubuntu Linux
* Docker
* Docker Compose
* Nginx
* PostgreSQL
* FastAPI
* React/Vite

### Monitoring environment

Monitoring is hosted separately from the production application.

This separation allows monitoring services to remain independent from the application environment.

Monitoring components include:

* Prometheus
* Grafana
* Blackbox Exporter

Production metrics are collected using:

* Node Exporter
* cAdvisor
* FastAPI Prometheus instrumentation

---

# 🐳 Containerized Application

The application is composed of independent containers:

| Service    | Purpose                          |
| ---------- | -------------------------------- |
| Frontend   | Web application interface        |
| Backend    | FastAPI application and REST API |
| PostgreSQL | Persistent application database  |

Docker Compose manages the application services and their dependencies.

This provides:

* Consistent deployment
* Service isolation
* Easier maintenance
* Repeatable deployments
* Simplified application recovery

---

# 🖥️ Frontend

The frontend is built using:

* React
* Vite
* Modern JavaScript tooling

The frontend communicates with the backend API and provides the primary user interface for the Investment Tracker.

Nginx handles incoming HTTP requests and routes traffic to the appropriate application service.

---

# ⚙️ Backend

The backend is implemented using **FastAPI**.

It provides:

* REST API endpoints
* Authentication-related endpoints
* Investment and stock data operations
* Buy transaction management
* Sold transaction management
* Portfolio/dashboard functionality
* Health endpoint
* Prometheus metrics endpoint

### Health endpoint

/health

The endpoint provides a lightweight application health check used by the monitoring system and deployment pipeline.

### Metrics endpoint

/metrics

The backend exposes Prometheus-compatible application metrics.

These metrics allow operational visibility into API activity and HTTP response behavior.

---

# 🗄️ Database

The application uses **PostgreSQL 16**.

The database runs as a dedicated Docker service with persistent Docker volume storage.

### Database characteristics

* PostgreSQL 16 Alpine
* Persistent database volume
* Health check using `pg_isready`
* Backend-to-database private container networking
* Database not exposed as a public application endpoint

This architecture keeps the database separated from direct public web traffic.

---

# 🌐 Nginx Reverse Proxy

Nginx provides the production HTTP entry point.

Its responsibilities include:

* Receiving client requests
* Routing frontend traffic
* Routing API requests
* Forwarding request headers
* Providing a clean public application endpoint

The application is therefore accessed through the web server rather than exposing the internal frontend and backend services directly to users.

---

# 🔄 CI/CD Automation

Deployment is automated through **GitHub Actions**.

The deployment workflow is triggered whenever changes are pushed to the `main` branch.

### Deployment flow

Developer
   │
   ▼
GitHub Repository
   │
   │ Push to main
   ▼
GitHub Actions
   │
   ▼
Secure SSH Connection
   │
   ▼
Oracle Production VM
   │
   ├── Fetch latest code
   ├── Reset to origin/main
   ├── Build/update containers
   ├── Start application
   └── Run API health check
```

### Automated deployment includes

1. Secure SSH authentication
2. Connection to the production server
3. Synchronization with the `main` branch
4. Docker Compose build/update
5. Application startup
6. API health verification
7. Deployment failure detection

This reduces manual deployment work and provides a repeatable release process.

---

# 🔐 Deployment Security

The deployment process uses SSH-based authentication rather than GitHub passwords.

Security measures include:

* Dedicated deployment SSH key
* GitHub repository deploy key
* GitHub Actions secret for deployment authentication
* Server-specific SSH configuration
* Database kept behind the application network
* Monitoring services separated from production
* Public access limited to required application services

Sensitive credentials and private keys are not stored in the repository.

---

# 📊 Monitoring & Observability

The production environment has dedicated monitoring infrastructure.

Monitoring is implemented using:

* Prometheus
* Grafana
* Blackbox Exporter
* Node Exporter
* cAdvisor
* FastAPI Prometheus instrumentation

---

## Grafana Dashboard

The monitoring dashboard provides a client-friendly view of production system status.

### Dashboard includes

* Production disk usage
* Docker monitoring
* Docker container memory
* Container start time
* API request activity
* API 5xx error rate
* Application health
* CPU usage
* Server uptime
* Memory usage
* Network activity

### Client monitoring dashboard

**Live Monitoring Dashboard:**

http://132.226.189.195:3000/public-dashboards/baf9c5ba69ed43d482f08284a1cda3e3

The dashboard is configured for external viewing and does not require a Grafana login.

---

# 📡 Prometheus Monitoring

Prometheus continuously collects metrics from the production environment.

Monitored targets include:

### Production server

Node Exporter provides infrastructure metrics including:

* CPU
* Memory
* Disk
* Network
* Uptime
* Filesystem statistics

### Docker containers

cAdvisor provides container-level information including:

* Container memory
* Container activity
* Container start time
* Container resource usage

### Application API

The FastAPI application exposes Prometheus metrics for:

* HTTP request activity
* Request rates
* HTTP status classes
* API operational behavior

### Application availability

Blackbox Exporter performs an external HTTP health check against the application health endpoint.

---

# 🚨 Production Alerts

The monitoring system currently contains three focused production alerts.

### 1. ProductionServerDown

Triggered when Prometheus cannot reach the production server's Node Exporter for the configured period.

**Severity:** Critical

### 2. InvestmentTrackerAPIDown

Triggered when the production API metrics endpoint becomes unavailable.

**Severity:** Critical

### 3. ProductionDiskUsageHigh

Triggered when production root filesystem usage remains above the configured threshold.

**Severity:** Warning

The alert configuration is intentionally focused on important operational conditions rather than generating unnecessary notifications.

---

# 🩺 Health Monitoring

The application exposes:

GET /health


The monitoring infrastructure checks this endpoint continuously.

A successful response confirms that the application health endpoint is reachable.

This provides an independent availability check in addition to server and container monitoring.

---

# 📈 API Error Monitoring

The backend exposes HTTP metrics through Prometheus.

API 5xx responses can be monitored through:

promql
sum(
  rate(http_requests_total{
    job="investment-tracker-api",
    status="5xx"
  }[5m])
)


This allows operational teams to identify server-side API error activity without requiring application logs to be manually inspected.

---

# 💾 Backup & Recovery

Backup procedures have been established for the production database and monitoring infrastructure.

Monitoring backups include:

* Grafana data
* Prometheus configuration
* Prometheus data

The production PostgreSQL database is also backed up.

Backup files are maintained separately from the active monitoring services to support recovery in case of infrastructure or service failure.

---

# 🛡️ Reliability

The deployment has been designed with operational reliability in mind.

Key measures include:

* Persistent PostgreSQL storage
* Dockerized services
* Separate monitoring infrastructure
* Automated deployment
* Automated API health verification
* Server monitoring
* Container monitoring
* Application monitoring
* Disk monitoring
* Production alerts
* Backup procedures
* Git-based version control

---

# 📁 Project Structure


Investment-tracker/
│
├── backend/
│   ├── application code
│   ├── API configuration
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── React application
│   ├── Vite configuration
│   └── Dockerfile
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# 🔧 Technology Stack

| Area                 | Technology                  |
| -------------------- | --------------------------- |
| Cloud                | Oracle Cloud Infrastructure |
| Operating System     | Ubuntu Linux                |
| Frontend             | React / Vite                |
| Backend              | FastAPI / Python            |
| Database             | PostgreSQL 16               |
| Web Server           | Nginx                       |
| Containers           | Docker                      |
| Orchestration        | Docker Compose              |
| CI/CD                | GitHub Actions              |
| Metrics              | Prometheus                  |
| Visualization        | Grafana                     |
| Black-box Monitoring | Blackbox Exporter           |
| Server Metrics       | Node Exporter               |
| Container Metrics    | cAdvisor                    |
| Version Control      | Git / GitHub                |

---

# 🎯 Operational Outcomes

The deployed solution provides:

* A production-accessible investment tracking application
* Persistent relational data storage
* Containerized application services
* Automated source-to-production deployment
* Automated post-deployment health validation
* Dedicated infrastructure monitoring
* Client-view system dashboard
* Application API monitoring
* Server and container visibility
* Production alerting
* Backup capability
* Version-controlled infrastructure and application code

The result is a maintainable production environment with application delivery, monitoring, and operational visibility integrated into one workflow.

---

# 🚀 Deployment Process

The normal release process is simple:


Code Change
    ↓
Git Commit
    ↓
Push to GitHub main
    ↓
GitHub Actions
    ↓
Production VM
    ↓
Docker Compose
    ↓
Health Check
    ↓
Production Release


No manual application deployment is required for normal code changes after the CI/CD pipeline is configured.

---

# 📞 Project Resources

### GitHub

https://github.com/farhan92cr/Investment-tracker

### Live Application

http://130.210.42.159

### Production Monitoring

http://132.226.189.195:3000/public-dashboards/baf9c5ba69ed43d482f08284a1cda3e3

---

# 📄 Project Status

**Status:** Production Deployment

The Investment Tracker is deployed with automated CI/CD, persistent database storage, centralized monitoring, health checks, production alerting, and backup procedures.

---
