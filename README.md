# 🚀 PyChrono — Distributed Task Orchestration Platform

PyChrono is a distributed task orchestration platform built with Python, FastAPI, Redis, and NATS JetStream.

It enables delayed job execution, recurring cron jobs, distributed worker processing, retry mechanisms, dead-letter queue handling, and job monitoring through a web dashboard.

---

## 🧠 Architecture

```text
                    +----------------+
                    |    FastAPI     |
                    | Dashboard/API  |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    |     Redis      |
                    | Job Storage    |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    |   Scheduler    |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | NATS JetStream |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Distributed    |
                    | Worker Pool    |
                    +----------------+
```

---

## ✨ Features

### Job Scheduling

- Delayed job execution
- One-time jobs
- Recurring cron jobs
- Redis Sorted Set based scheduling

### Distributed Processing

- Event-driven architecture
- NATS JetStream messaging
- Horizontally scalable workers
- AsyncIO-based execution

### Reliability

- Automatic retry mechanism
- Configurable retry limits
- Dead Letter Queue (DLQ)
- Failure tracking and error storage

### Monitoring

- FastAPI REST APIs
- Interactive dashboard
- Job search and filtering
- Job status tracking
- Job details page
- Dead Letter Queue dashboard

### Deployment

- Dockerized services
- Docker Compose support
- One-command environment startup

---

## ⚙️ Tech Stack

### Backend

- Python 3.11
- FastAPI
- AsyncIO

### Messaging

- NATS JetStream

### Storage

- Redis

### Scheduling

- Croniter

### Containerization

- Docker
- Docker Compose

### UI

- Jinja2 Templates
- Bootstrap 5

---

## 📁 Project Structure

```text
pychrono/
│
├── api/
│   ├── main.py
│   └── schemas.py
│
├── core/
│   ├── models.py
│   └── nats_client.py
│
├── scheduler/
│   └── scheduler.py
│
├── worker/
│   └── worker.py
│
├── storage/
│   └── redis_store.py
│
├── templates/
│   ├── dashboard.html
│   ├── job_details.html
│   └── dead_letter.html
│
├── scripts/
│   ├── start_scheduler.py
│   └── start_worker.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Clone Repository

```bash
git clone <repository-url>
cd pychrono
```

---

## 🐳 Run Using Docker Compose

Start all services:

```bash
docker compose up --build
```

This starts:

- FastAPI
- Scheduler
- Worker
- Redis
- NATS JetStream

---

## 🌐 Dashboard

Open:

```text
http://localhost:8000/dashboard
```

Features:

- View all jobs
- Search jobs
- Filter by status
- Retry failed jobs
- View dead-letter queue
- View job details

---

## 📡 API Endpoints

### Create Job

```http
POST /jobs
```

Example:

```json
{
  "task": "print",
  "payload": {
    "message": "Hello World"
  },
  "delay_seconds": 10
}
```

---

### Get All Jobs

```http
GET /jobs
```

---

### Get Job

```http
GET /jobs/{job_id}
```

---

### Retry Failed Job

```http
POST /jobs/{job_id}/retry
```

---

### Get Statistics

```http
GET /stats
```

---

## ⏰ Cron Jobs

Create recurring jobs:

```json
{
  "task": "print",
  "payload": {
    "message": "Recurring Job"
  },
  "cron": "*/1 * * * *"
}
```

Examples:

```text
*/1 * * * *   -> Every minute
*/5 * * * *   -> Every 5 minutes
0 * * * *     -> Every hour
```

---

## 🔄 Job Lifecycle

Successful execution:

```text
PENDING
    ↓
DISPATCHED
    ↓
RUNNING
    ↓
COMPLETED
```

Failure flow:

```text
PENDING
    ↓
RUNNING
    ↓
RETRY
    ↓
PENDING
    ↓
RUNNING
    ↓
FAILED
    ↓
DEAD LETTER QUEUE
```

---

## 🧪 Example Use Cases

- Background email processing
- Scheduled notifications
- Report generation
- Data synchronization
- Recurring maintenance jobs
- Event-driven workflows

---

## 📈 Future Enhancements

- WebSocket-based live dashboard
- Job cancellation
- Execution history tracking
- Worker monitoring
- Authentication & RBAC
- Kubernetes deployment
- Metrics & observability

---
