# Investment Tracker

A containerized investment-tracking application deployed on **Oracle Cloud**, with automated **CI/CD**, PostgreSQL, Nginx, Prometheus, Grafana, application metrics, infrastructure monitoring, health checks, alerting, and backup/recovery planning.

The project was built as a practical **DevOps learning and portfolio project**. It covers the complete journey from running an application with Docker Compose to deploying it on a cloud VM and building a separate monitoring system around it.

---

## 📌 Project Overview

Investment Tracker is a web application for managing investment-related information such as stocks, prices, buy transactions, sold transactions, and portfolio/dashboard information.

The application is separated into three main components:

* **Frontend** — user interface
* **Backend** — FastAPI application/API
* **PostgreSQL** — persistent application database

The application is containerized with Docker and deployed on an **Oracle Cloud Infrastructure (OCI)** virtual machine.

A second Oracle Cloud VM is used specifically for monitoring.

The final infrastructure therefore consists of:

```text
                           Internet
                              │
                              ▼
                    ┌──────────────────┐
                    │   Oracle Cloud   │
                    │  Production VM   │
                    │ 130.210.42.159   │
                    └─────────┬────────┘
                              │
                         Nginx :80
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
             Frontend :5173       Backend :8000
                                        │
                                        ▼
                                  PostgreSQL :5432


                    ┌─────────────────────────┐
                    │    Monitoring VM        │
                    │   132.226.189.195       │
                    ├─────────────────────────┤
                    │ Prometheus :9090        │
                    │ Grafana :3000           │
                    │ Blackbox Exporter :9115 │
                    └───────────┬─────────────┘
                                │
                 ┌──────────────┼───────────────┐
                 │              │               │
                 ▼              ▼               ▼
           Node Exporter    cAdvisor       Application
                 │              │            Metrics
                 └──────────────┼───────────────┘
                                │
                                ▼
                         Production VM
```

---

# 🏗️ Architecture

The project uses two Oracle Cloud virtual machines.

### Production VM

The production VM runs the actual application:

```text
Production VM
│
├── Nginx
│
├── Frontend container
│
├── Backend container
│
├── PostgreSQL container
│
├── Node Exporter
│
└── cAdvisor
```

### Monitoring VM

The monitoring VM is dedicated to monitoring the production environment:

```text
Monitoring VM
│
├── Prometheus
├── Grafana
└── Blackbox Exporter
```

Separating monitoring from production provides an important advantage:

> If the production application or production VM becomes unavailable, the monitoring system can still remain available to detect and report the failure.

---

# 🖥️ Infrastructure

## Production VM

| Property     | Value                       |
| ------------ | --------------------------- |
| Cloud        | Oracle Cloud Infrastructure |
| Region       | Mumbai (`ap-mumbai-1`)      |
| Shape        | `VM.Standard.E2.1.Micro`    |
| OS           | Ubuntu 22.04.5 LTS          |
| Public IP    | `130.210.42.159`            |
| Private IP   | `10.0.0.221`                |
| Architecture | x86_64                      |

## Monitoring VM

| Property   | Value                                    |
| ---------- | ---------------------------------------- |
| Cloud      | Oracle Cloud Infrastructure              |
| Shape      | `VM.Standard.E2.1.Micro`                 |
| OS         | Ubuntu 22.04 Minimal                     |
| Public IP  | `132.226.189.195`                        |
| Monitoring | Prometheus + Grafana + Blackbox Exporter |

Both VMs use Oracle Cloud Always Free eligible resources.

---

# 🧩 Application Architecture

The application consists of:

```text
Browser
   │
   ▼
Nginx
   │
   ├──────────────► Frontend
   │
   └──────────────► Backend API
                         │
                         ▼
                    PostgreSQL
```

## Frontend

The frontend provides the user interface.

It runs in a Docker container and listens internally on:

```text
5173
```

The frontend communicates with the backend API.

---

## Backend

The backend is implemented using **FastAPI**.

It provides API endpoints for application functionality including:

* authentication
* stocks
* buy transactions
* sold transactions
* prices
* dashboard
* health checking
* Prometheus metrics

The backend listens on:

```text
8000
```

---

## PostgreSQL

PostgreSQL is used as the application's relational database.

The database runs in its own Docker container.

The database uses a Docker named volume so that database data is not lost when the container is recreated.

The application connects to PostgreSQL using the Docker Compose service name:

```text
db
```

rather than the public IP address.

This allows Docker's internal network to handle communication between the containers.

---

# 🐳 Docker

Docker packages the application's components into isolated containers.

The production environment currently contains:

```text
investment-tracker-frontend-1
investment-tracker-backend-1
investment-tracker-db-1
node-exporter
cadvisor
```

Docker Compose is used to define and manage the application services.

Typical commands:

```bash
docker compose ps
```

View running containers:

```bash
docker ps
```

View logs:

```bash
docker compose logs
```

View backend logs:

```bash
docker compose logs backend
```

Restart services:

```bash
docker compose restart
```

Build and start:

```bash
docker compose up -d --build
```

---

# 🌐 Nginx

Nginx is used as the **reverse proxy**.

### What is a reverse proxy?

A reverse proxy is a server that receives requests from users and forwards those requests to the correct internal application.

Instead of users directly accessing:

```text
:5173
:8000
```

they access the normal HTTP endpoint:

```text
http://130.210.42.159
```

Nginx decides where the request should go.

### Current routing

```text
/                         → Frontend :5173

/auth                     → Backend :8000
/stocks                   → Backend :8000
/buy-transactions         → Backend :8000
/sold-transactions        → Backend :8000
/prices                   → Backend :8000
/dashboard                → Backend :8000
/health                   → Backend :8000
```

This gives the application a cleaner public interface and prevents users from needing to know the internal container ports.

---

# 🔄 CI/CD

The project uses **GitHub Actions** for automated deployment.

## What is CI/CD?

**CI/CD** stands for Continuous Integration and Continuous Delivery/Deployment.

In simple terms:

> Code is pushed to GitHub → GitHub Actions connects to the production server → the latest code is deployed automatically.

The deployment workflow runs when changes are pushed to:

```text
main
```

---

## Deployment flow

```text
Developer
    │
    ▼
Git push
    │
    ▼
GitHub
    │
    ▼
GitHub Actions
    │
    ▼
SSH connection
    │
    ▼
Production VM
    │
    ├── git fetch
    ├── git reset
    ├── docker compose build
    ├── docker compose up
    │
    ▼
API health check
    │
    ▼
Deployment successful
```

---

## GitHub Secrets

The deployment workflow uses GitHub Secrets instead of putting sensitive credentials directly into the repository.

Current secrets include:

```text
SSH_PRIVATE_KEY
SSH_USER
SERVER_HOST
```

The production host is:

```text
130.210.42.159
```

The SSH user is:

```text
ubuntu
```

---

## Deployment health check

After deployment, GitHub Actions checks:

```text
http://127.0.0.1:8000/health
```

The deployment is considered successful when the API responds correctly.

The health endpoint returns:

```json
{
  "status": "ok"
}
```

If the API does not become ready within the configured waiting period, the workflow reports a failure.

This prevents a deployment from being marked successful simply because Docker started the containers.

---

# 📊 Monitoring Architecture

Monitoring is intentionally separated from the production VM.

```text
                     Monitoring VM
                          │
                  ┌───────┴────────┐
                  │                │
             Prometheus         Grafana
                  │
       ┌──────────┼───────────────┐
       │          │               │
       ▼          ▼               ▼
Node Exporter  cAdvisor      Backend Metrics
       │          │               │
       └──────────┼───────────────┘
                  │
                  ▼
             Production VM
```

Blackbox Exporter independently checks the application's public health endpoint.

---

# 🔎 Prometheus

## What is Prometheus?

**Prometheus is a monitoring and metrics collection system.**

In simple terms:

> Prometheus regularly asks different systems for numerical information and stores that information so it can later be queried and displayed.

Examples of metrics:

```text
CPU usage
Memory usage
Disk usage
Network traffic
HTTP requests
HTTP errors
Container memory
Container CPU
Server availability
```

Prometheus runs on the monitoring VM:

```text
9090
```

---

# 📈 Metrics

## What are metrics?

Metrics are numerical measurements describing the state or activity of a system.

For example:

```text
CPU usage = 6.5%
Memory usage = 55%
Disk usage = 28.4%
```

Prometheus stores these measurements over time.

This allows us to answer questions such as:

> What was the server's CPU usage five minutes ago?

or:

> Is the disk usage continuously increasing?

---

# 🖥️ Node Exporter

## What is Node Exporter?

**Node Exporter collects operating-system and hardware-related metrics from a Linux server.**

It provides information such as:

* CPU
* RAM
* disk
* filesystem
* network
* system uptime
* load
* filesystem capacity

Node Exporter runs on the **production VM**.

Prometheus collects its metrics from:

```text
10.0.0.221:9100
```

The port is bound to the production VM's **private IP**, rather than publicly exposing it.

---

# 🐳 cAdvisor

## What is cAdvisor?

**cAdvisor collects resource-usage information about containers.**

It helps answer questions such as:

* How much CPU is a container using?
* How much memory is a container using?
* When did a container start?
* How much network traffic is a container generating?

cAdvisor runs on the production VM.

It is available internally at:

```text
10.0.0.221:8080
```

It is also bound to the private IP rather than being publicly exposed.

---

# 🛰️ Blackbox Exporter

## What is Blackbox Exporter?

Blackbox Exporter checks a service from the outside.

Instead of asking:

> "What CPU are you using?"

it asks:

> "Can I actually reach this application and does it respond correctly?"

For this project, Blackbox Exporter checks:

```text
http://130.210.42.159/health
```

The monitoring flow is:

```text
Blackbox Exporter
       │
       ▼
Production /health
       │
       ▼
HTTP response
       │
       ▼
probe_success
```

A value of:

```text
1
```

means the probe succeeded.

---

# 🚀 Application Metrics

The FastAPI backend has been instrumented using:

```text
prometheus-fastapi-instrumentator
```

The application exposes Prometheus-compatible metrics through:

```text
/metrics
```

Prometheus collects them from:

```text
130.210.42.159:8000/metrics
```

This allows the monitoring system to observe application-level information rather than only server-level information.

For example:

```text
HTTP request rate
HTTP response status
HTTP 5xx errors
request processing information
```

---

# ❤️ Application Health Check

The backend provides:

```text
/health
```

A healthy response is:

```json
{
  "status": "ok"
}
```

This endpoint is used by:

1. CI/CD deployment verification
2. Blackbox monitoring
3. Operational troubleshooting

This makes `/health` an important part of the application's reliability design.

---

# 📊 Grafana

## What is Grafana?

**Grafana is a visualization and dashboard platform.**

Prometheus stores the metrics.

Grafana turns those metrics into:

* graphs
* panels
* statistics
* dashboards
* visual monitoring information

The monitoring VM runs Grafana on:

```text
3000
```

The main dashboard is:

```text
Investment Tracker Monitoring
```

---

# 📋 Grafana Dashboard

The dashboard contains panels for important production metrics.

Current monitoring includes:

### Disk Usage

Shows production filesystem usage.

Current verified usage during setup:

```text
~28.4%
```

---

### Docker Monitoring

Shows resource usage associated with Docker containers.

---

### Docker Container Memory

Shows container memory consumption.

---

### Docker Container Start Time

Shows when containers started.

---

### API Request Rate

Shows the rate of HTTP requests received by the API.

---

### API 5xx Errors

Monitors server-side HTTP errors.

No data can be a normal result when there have been no 5xx responses.

This is important:

> "No data" on an error-rate panel does not automatically mean monitoring is broken. It can simply mean there have been no matching errors.

---

### Health / Blackbox

Shows whether the production application's health endpoint is responding successfully.

Current healthy value:

```text
probe_success = 1
```

---

### CPU

Shows production CPU utilization.

---

### Memory

Shows production memory utilization.

---

### Uptime

Shows how long the monitored system has been running.

---

### Network Traffic

Shows production network activity.

---

# 🚨 Alerting

Prometheus evaluates alerting rules defined in:

```text
prometheus/alerts.yml
```

The project intentionally keeps the alerting system small and focused.

There are currently **three production alerts**.

---

## 1. ProductionServerDown

This alert monitors the production Node Exporter.

Condition:

```text
up{job="node-exporter"} == 0
```

The alert fires after the condition remains true for:

```text
2 minutes
```

Purpose:

> Detect when Prometheus can no longer reach the production server's Node Exporter.

---

## 2. InvestmentTrackerAPIDown

This alert monitors the backend API metrics endpoint.

Condition:

```text
up{job="investment-tracker-api"} == 0
```

It fires after:

```text
2 minutes
```

Purpose:

> Detect when Prometheus cannot reach the Investment Tracker API.

---

## 3. ProductionDiskUsageHigh

This alert monitors the production root filesystem.

Threshold:

```text
> 85%
```

Duration:

```text
10 minutes
```

Purpose:

> Detect sustained high disk usage before the production server runs out of storage.

---

# 🔧 PromQL

## What is PromQL?

**PromQL is Prometheus Query Language.**

It is used to retrieve and calculate information from Prometheus metrics.

For example, a query can calculate filesystem usage:

```text
100 * (
  1 -
  (
    available space /
    total space
  )
)
```

PromQL is used by:

* Grafana panels
* Prometheus queries
* alerting rules
* troubleshooting

---

# 🔌 Prometheus HTTP API

Prometheus also provides an HTTP API.

For example:

```bash
curl -s http://localhost:9090/api/v1/rules
```

This retrieves information about loaded Prometheus rules.

Another endpoint is:

```text
/api/v1/query
```

which can execute a PromQL query through the HTTP API.

Conceptually:

```text
curl
  │
  ▼
HTTP GET request
  │
  ▼
Prometheus API
  │
  ▼
PromQL
  │
  ▼
JSON result
```

This is different from an alerting rule.

For example:

```text
alerts.yml
      │
      ▼
Alerting Rule
      │
      ▼
Prometheus evaluates condition
```

while:

```text
curl
      │
      ▼
Prometheus HTTP API
      │
      ▼
PromQL query
      │
      ▼
Result
```

---

# 🔐 Security and Network Configuration

Security was considered during the monitoring migration.

## Production monitoring ports

The following monitoring ports are **not intended to be public application endpoints**:

```text
9100 → Node Exporter
8080 → cAdvisor
```

They are bound to the production private IP:

```text
10.0.0.221
```

This prevents them from being unnecessarily exposed through the production public interface.

---

## Production public services

The intended public application endpoint is:

```text
HTTP :80
```

SSH is available for administration:

```text
SSH :22
```

The host firewall also contains rules restricting unwanted inbound traffic.

---

# 🔒 Why private monitoring ports matter

Docker-published ports can sometimes bypass traditional host firewall expectations depending on how Docker networking is configured.

Therefore, simply assuming:

> "The firewall will protect this port"

is not always sufficient.

Binding monitoring services directly to:

```text
10.0.0.221
```

provides an additional layer of protection.

---

# 🔐 SSH Access

SSH is used for:

* server administration
* CI/CD deployment
* troubleshooting
* maintenance

GitHub Actions uses a dedicated SSH private key stored as a GitHub Secret.

The production VM also uses an SSH deploy key for GitHub repository access.

This avoids relying on GitHub password authentication.

---

# ☁️ Oracle Cloud

The application is deployed on:

**Oracle Cloud Infrastructure (OCI)**.

OCI provides the virtual machines used for:

```text
Production
Monitoring
```

The project uses the Always Free eligible VM shape:

```text
VM.Standard.E2.1.Micro
```

This makes the environment useful as a low-cost DevOps practice and portfolio infrastructure.

---

# 💾 Backup Strategy

Backups were considered for both application and monitoring infrastructure.

## Monitoring backups

The monitoring VM contains backups for:

### Grafana

```text
grafana-backup-20260929-101104.tar.gz
```

This contains Grafana data including dashboard/database information.

### Prometheus configuration

```text
prometheus-config-20260929-101619.tar.gz
```

This preserves important configuration such as:

```text
prometheus.yml
alerts.yml
```

### Prometheus historical data

```text
prometheus-data-20260929-102000.tar.gz
```

This preserves Prometheus's stored historical metrics.

---

# 🗄️ Production database

The PostgreSQL database is part of the production application's backup/recovery considerations.

The project also maintains the existing PostgreSQL backup arrangement rather than unnecessarily recreating the backup process during the monitoring migration.

---

# 🧠 Understanding the backups

Different backups protect different things.

```text
Grafana backup
      │
      └── How monitoring is displayed/configured

Prometheus config
      │
      └── How monitoring works

Prometheus data
      │
      └── Historical monitoring information

PostgreSQL backup
      │
      └── Application data
```

A monitoring system can therefore be rebuilt even if the monitoring VM is lost, provided the important configuration and backups are available.

---

# 🔄 Complete Deployment Flow

The complete application deployment process is:

```text
Developer changes code
        │
        ▼
Git commit
        │
        ▼
Git push
        │
        ▼
GitHub
        │
        ▼
GitHub Actions
        │
        ▼
SSH to Oracle VM
        │
        ▼
git fetch origin main
        │
        ▼
git reset --hard origin/main
        │
        ▼
docker compose up -d --build
        │
        ▼
Wait for backend
        │
        ▼
/health check
        │
        ├── Success → Deployment successful
        │
        └── Failure → Deployment fails
```

---

# 🔍 Complete Monitoring Flow

Once the application is running:

```text
Production Server
│
├── Node Exporter
│      │
│      └── Server metrics
│
├── cAdvisor
│      │
│      └── Container metrics
│
└── FastAPI
       │
       └── Application metrics
              │
              ▼
         Prometheus
              │
              ├── Stores metrics
              ├── Evaluates alerts
              │
              ▼
           Grafana
              │
              ▼
        Monitoring Dashboard
```

Separately:

```text
Blackbox Exporter
        │
        ▼
Production /health
        │
        ▼
probe_success
```

---

# 🛠️ Useful Production Commands

## Check containers

```bash
docker ps
```

## Check Compose services

```bash
docker compose ps
```

## View logs

```bash
docker compose logs
```

## View backend logs

```bash
docker compose logs backend
```

## Follow backend logs

```bash
docker compose logs -f backend
```

## Restart application

```bash
docker compose restart
```

## Rebuild application

```bash
docker compose up -d --build
```

## Check API health

```bash
curl -fsS http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

---

# 📊 Useful Monitoring Commands

## Check Prometheus containers

```bash
docker ps
```

## Check Prometheus rules

```bash
curl -s http://localhost:9090/api/v1/rules
```

## Check Prometheus targets

Open:

```text
http://localhost:9090/targets
```

when connected through the SSH tunnel.

## Query Prometheus

Example:

```bash
curl -s --get 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=up'
```

---

# 💻 SSH Tunnel for Grafana

The monitoring VM does not expose Grafana directly to the public internet.

Grafana can be accessed through an SSH tunnel.

From Windows PowerShell:

```powershell
ssh -i "C:\Users\Admin\Downloads\ssh-key-2026-09-28 (1).key" -L 3000:127.0.0.1:3000 ubuntu@132.226.189.195
```

Then open:

```text
http://localhost:3000
```

This forwards the local Windows port:

```text
localhost:3000
```

to Grafana running on the monitoring VM.

---

# 🧪 Monitoring Verification

The monitoring environment was tested end-to-end.

Verified:

* Production Node Exporter responds
* Production cAdvisor responds
* FastAPI `/metrics` responds
* `/health` responds
* Blackbox health probe succeeds
* Prometheus sees production targets
* Grafana receives Prometheus data
* Dashboard panels update
* CPU metrics update
* memory metrics update
* disk metrics update
* network metrics update
* container metrics update
* API request metrics update
* alerting rules load successfully

Prometheus currently reports the important production targets as healthy:

```text
prometheus                         UP
investment-tracker-api             UP
investment-tracker-health         UP
node-exporter                      UP
cadvisor                           UP
```

---

# 🧯 Troubleshooting

## API is not responding

Check:

```bash
docker compose ps
```

Then:

```bash
docker compose logs backend
```

Then:

```bash
curl -fsS http://127.0.0.1:8000/health
```

---

## Frontend is not loading

Check:

```bash
docker compose ps
```

Then:

```bash
docker compose logs frontend
```

Check Nginx:

```bash
sudo nginx -t
```

---

## PostgreSQL is not healthy

Check:

```bash
docker compose ps
```

Then:

```bash
docker compose logs db
```

---

## Prometheus target is DOWN

First check the target directly from the monitoring VM.

Node Exporter:

```bash
curl -s http://10.0.0.221:9100/metrics | head
```

cAdvisor:

```bash
curl -s http://10.0.0.221:8080/metrics | head
```

API:

```bash
curl -s http://130.210.42.159:8000/metrics | head
```

Health:

```bash
curl -s http://130.210.42.159/health
```

If the direct request fails, investigate networking or the production service.

If the direct request succeeds but Prometheus reports DOWN, investigate the Prometheus configuration and target definition.

---

# 🧩 Important DevOps Concepts Demonstrated

This project demonstrates practical experience with:

### Linux

* Ubuntu administration
* SSH
* processes
* networking
* filesystem usage
* permissions
* services

### Docker

* Dockerfiles
* Docker images
* containers
* volumes
* Docker networking
* Docker Compose
* container health checks

### Cloud

* Oracle Cloud Infrastructure
* cloud VMs
* public/private IP addresses
* cloud networking
* SSH access

### CI/CD

* GitHub
* GitHub Actions
* SSH-based deployment
* GitHub Secrets
* automated builds
* automated health checks

### Web infrastructure

* Nginx
* reverse proxy
* HTTP
* application routing

### Backend

* FastAPI
* REST APIs
* health endpoints
* Prometheus instrumentation

### Monitoring

* Prometheus
* PromQL
* Grafana
* Node Exporter
* cAdvisor
* Blackbox Exporter
* alerting
* application metrics
* infrastructure metrics

### Reliability

* health checks
* automatic deployment verification
* monitoring separation
* alerts
* backups
* private monitoring endpoints

---

# 📚 Simple Terminology

| Term                      | Simple explanation                                                                   |
| ------------------------- | ------------------------------------------------------------------------------------ |
| **API**                   | A way for software applications to communicate with each other.                      |
| **Backend**               | The server-side part of an application that processes requests and data.             |
| **Frontend**              | The user-facing part of the application.                                             |
| **Container**             | An isolated environment used to run an application and its dependencies.             |
| **Docker**                | A platform for building and running containers.                                      |
| **Docker Compose**        | A tool for defining and running multiple Docker containers together.                 |
| **Image**                 | A packaged template used to create a Docker container.                               |
| **Volume**                | Persistent storage used by containers.                                               |
| **Nginx**                 | A web server and reverse proxy.                                                      |
| **Reverse Proxy**         | A server that receives requests and forwards them to internal services.              |
| **CI/CD**                 | Automation for integrating, building, testing and deploying software.                |
| **GitHub Actions**        | GitHub's automation platform used here for deployment.                               |
| **Prometheus**            | A system that collects and stores numerical monitoring metrics.                      |
| **PromQL**                | The query language used by Prometheus.                                               |
| **Grafana**               | A platform used to visualize metrics through dashboards.                             |
| **Node Exporter**         | Collects Linux server metrics such as CPU, memory, disk and network information.     |
| **cAdvisor**              | Collects resource usage information from containers.                                 |
| **Blackbox Exporter**     | Tests whether an external service or endpoint is reachable and responding.           |
| **Metric**                | A numerical measurement describing system activity or health.                        |
| **Alert**                 | A notification condition triggered when a monitoring rule is satisfied.              |
| **Health Check**          | A test used to determine whether an application is functioning.                      |
| **Endpoint**              | A specific URL through which an application provides functionality or information.   |
| **SSH**                   | A secure protocol used to remotely access Linux servers.                             |
| **VM**                    | Virtual Machine; a virtual computer running inside a cloud or physical server.       |
| **Public IP**             | An IP address reachable from the public internet.                                    |
| **Private IP**            | An internal network IP used for private communication.                               |
| **Repository**            | A project stored and version-controlled by Git.                                      |
| **Deployment**            | The process of putting application code into a running environment.                  |
| **Prometheus Target**     | A system or service from which Prometheus collects metrics.                          |
| **Scrape**                | The process where Prometheus retrieves metrics from a target.                        |
| **Dashboard**             | A visual collection of monitoring panels and graphs.                                 |
| **Stateful Application**  | An application that needs persistent data, such as PostgreSQL.                       |
| **Stateless Application** | An application where individual instances do not need to keep permanent local state. |

---

# 🏛️ Why the Architecture Was Designed This Way

The project evolved from a simple application deployment into a more realistic DevOps environment.

Instead of putting everything on one VM:

```text
One VM
├── Application
├── Database
├── Prometheus
├── Grafana
└── Monitoring
```

the final architecture separates production and monitoring:

```text
Production VM
├── Application
├── Database
├── Node Exporter
└── cAdvisor

Monitoring VM
├── Prometheus
├── Grafana
└── Blackbox Exporter
```

This separation makes the monitoring system more independent from the application it monitors.

---

# 🔄 Migration Lessons

During development, the monitoring architecture was improved to avoid unnecessary duplication.

Initially, monitoring components were present on the monitoring VM as well as the production VM.

This created duplicate monitoring targets.

The final design keeps:

```text
Node Exporter → Production VM
cAdvisor      → Production VM
```

while the monitoring VM contains:

```text
Prometheus
Grafana
Blackbox Exporter
```

This provides a cleaner architecture.

---

# 🔐 Monitoring Security Improvement

cAdvisor had previously been exposed more broadly than necessary.

It was recreated with a private binding:

```text
10.0.0.221:8080
```

Node Exporter is similarly bound to:

```text
10.0.0.221:9100
```

This follows the principle:

> Monitoring endpoints should not be publicly exposed unless there is a specific reason to expose them.

---

# 📦 Current Production Containers

The production environment currently contains:

```text
node-exporter
investment-tracker-frontend-1
investment-tracker-backend-1
cadvisor
investment-tracker-db-1
```

All important application services were verified during the monitoring setup.

---

# 📦 Current Monitoring Containers

The monitoring environment contains:

```text
prometheus
grafana
blackbox-exporter
```

The monitoring VM intentionally does **not** run its own Node Exporter or cAdvisor because the goal is to monitor the production environment rather than duplicate production monitoring targets.

---

# 🚀 Future Improvements

The current project is intentionally not considered the final possible architecture.

Potential future improvements include:

* HTTPS/TLS
* domain name
* stronger secrets management
* centralized logging
* automated database backup verification
* off-site disaster recovery
* container image security scanning
* automated testing in CI
* infrastructure as code
* Terraform
* Ansible
* Kubernetes
* managed PostgreSQL
* Kubernetes-based autoscaling
* more advanced observability

---

# ☸️ Kubernetes — Future Direction

Kubernetes is intentionally **not part of the current deployment**.

It will be considered as a future stage after the current Docker/OCI architecture is fully documented and understood.

The current architecture provides the foundation for learning Kubernetes because the application already has separate:

```text
Frontend
Backend
Database
Monitoring
```

In a future Kubernetes architecture, the stateless application components could be represented by Kubernetes Deployments and Services, while stateful workloads such as PostgreSQL would require appropriate persistent storage and stateful architecture.

Possible future architecture:

```text
Kubernetes Cluster
│
├── Frontend Pods
│
├── Backend Pods
│
├── Services
│
├── Ingress
│
├── Persistent Storage
│
├── Monitoring
│
└── Autoscaling
```

Kubernetes would allow the project to explore:

* container orchestration
* automatic recovery
* service discovery
* rolling deployments
* horizontal scaling
* load balancing
* health probes
* persistent storage
* cluster monitoring

---

# 📝 Project Status

## Completed

* [x] Application containerization
* [x] Docker Compose deployment
* [x] PostgreSQL integration
* [x] Nginx reverse proxy
* [x] Oracle Cloud production VM
* [x] GitHub repository
* [x] SSH-based deployment
* [x] GitHub Actions CI/CD
* [x] Automated deployment
* [x] Deployment health check
* [x] FastAPI Prometheus instrumentation
* [x] Dedicated monitoring VM
* [x] Prometheus
* [x] Grafana
* [x] Blackbox Exporter
* [x] Node Exporter
* [x] cAdvisor
* [x] Production health monitoring
* [x] Application metrics
* [x] Infrastructure metrics
* [x] Docker/container monitoring
* [x] Grafana dashboard
* [x] Prometheus alerting
* [x] Production server alert
* [x] API availability alert
* [x] Disk usage alert
* [x] Monitoring security improvements
* [x] Grafana backup
* [x] Prometheus configuration backup
* [x] Prometheus historical data backup
* [x] Production monitoring backup preservation
* [x] Monitoring architecture verification

## Planned Later

* [ ] HTTPS
* [ ] Advanced logging
* [ ] Additional security hardening
* [ ] Infrastructure as Code
* [ ] Kubernetes
* [ ] Advanced disaster recovery

---

# 🎯 What This Project Demonstrates

This project demonstrates a practical DevOps workflow rather than simply running an application locally.

The final system covers:

```text
Code
 │
 ▼
GitHub
 │
 ▼
CI/CD
 │
 ▼
Docker
 │
 ▼
Oracle Cloud
 │
 ├── Nginx
 ├── Frontend
 ├── Backend
 └── PostgreSQL
 │
 ▼
Monitoring
 │
 ├── Prometheus
 ├── Grafana
 ├── Node Exporter
 ├── cAdvisor
 └── Blackbox Exporter
 │
 ▼
Alerts + Dashboards
 │
 ▼
Backups + Recovery Planning
```

The project therefore demonstrates the complete basic lifecycle of a cloud-hosted application:

> **Develop → Version Control → Build → Deploy → Monitor → Alert → Troubleshoot → Backup → Improve**

---

# 👨‍💻 Project Purpose

This project was built as a hands-on DevOps learning project to gain practical experience with:

* Linux
* Docker
* Docker Compose
* Git/GitHub
* GitHub Actions
* CI/CD
* Oracle Cloud
* Nginx
* FastAPI
* PostgreSQL
* Prometheus
* Grafana
* Node Exporter
* cAdvisor
* Blackbox Exporter
* monitoring
* alerting
* backup and recovery
* cloud infrastructure

The goal is not only to make the application work, but to understand how an application can be **deployed, monitored, maintained, and improved like a real production system**.

---

## 📌 Final Architecture Summary

```text
                         ┌─────────────────────┐
                         │       GitHub        │
                         │   Source + Actions  │
                         └──────────┬──────────┘
                                    │
                               CI/CD SSH
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│                  ORACLE CLOUD                           │
│                                                         │
│  ┌─────────────────────────┐                            │
│  │     Production VM       │                            │
│  │     130.210.42.159      │                            │
│  │                         │                            │
│  │  ┌───────────────────┐  │                            │
│  │  │       Nginx       │  │                            │
│  │  │       :80         │  │                            │
│  │  └─────────┬─────────┘  │                            │
│  │            │            │                            │
│  │     ┌──────┴──────┐     │                            │
│  │     ▼             ▼     │                            │
│  │ Frontend       Backend  │                            │
│  │  :5173          :8000   │                            │
│  │                    │     │                            │
│  │                    ▼     │                            │
│  │               PostgreSQL │                            │
│  │                         │                            │
│  │ Node Exporter :9100     │                            │
│  │ cAdvisor      :8080     │                            │
│  └───────────────┬─────────┘                            │
│                  │                                      │
│                  │ Private network                      │
│                  │                                      │
│  ┌───────────────▼──────────────────────┐               │
│  │         Monitoring VM                │               │
│  │         132.226.189.195              │               │
│  │                                      │               │
│  │  Prometheus :9090                    │               │
│  │       │                              │               │
│  │       ├── Node Exporter              │               │
│  │       ├── cAdvisor                   │               │
│  │       └── FastAPI metrics            │               │
│  │                                      │               │
│  │  Blackbox Exporter                   │               │
│  │       │                              │               │
│  │       └── /health                    │               │
│  │                                      │               │
│  │  Grafana :3000                       │               │
│  └──────────────────────────────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ⭐ Final Result

The Investment Tracker is now more than a Dockerized application.

It is a cloud-hosted application with:

**automated deployment + containerization + database + reverse proxy + application metrics + infrastructure monitoring + dashboards + health checks + alerting + backups + security considerations.**

Kubernetes is intentionally left as the **next major DevOps learning stage**, rather than being added before the current architecture is fully understood.
