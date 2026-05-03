# 🚀 PyChrono — Distributed Task Scheduler (Python + NATS)

PyChrono is a **distributed task scheduler** built using Python and NATS (JetStream).
It allows you to schedule jobs, dispatch them via a message broker, and execute them using distributed workers.

---

## 🧠 Architecture

```
Client (Script/API)
        ↓
   Scheduler Service
        ↓
 NATS (JetStream Broker)
        ↓
     Workers
        ↓
  Task Execution
```

---

## ⚙️ Tech Stack

* Python (asyncio)
* NATS (JetStream)
* Redis (job storage)
* nats-py (client library)

---

## 📁 Project Structure

```
pychrono/
│
├── core/
│   ├── nats_client.py
│   ├── models.py
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
├── scripts/
│   ├── start_scheduler.py
│   ├── start_worker.py
│   └── add_job.py
│
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repo

---

### 2. Install dependencies

```
pip install nats-py redis
```

---

### 3. Start Infrastructure

#### ▶️ Start NATS (JetStream enabled)

```
docker run -p 4222:4222 -p 8222:8222 nats -js
```

#### ▶️ Start Redis

```
docker run -p 6379:6379 redis
```

---

## ▶️ Running the System

⚠️ Always run commands using `-m` from project root.

---

### 1. Start Scheduler

```
python -m scripts.start_scheduler
```

---

### 2. Start Worker

```
python -m scripts.start_worker
```

---

### 3. Add a Job

```
python -m scripts.add_job
```

---

## 🧪 Example Job

A job looks like:

```python
Job(
    id="uuid",
    task="print",
    payload={"msg": "Hello World"},
    run_at=time.time() + 5
)
```

---

## 🎯 Expected Output

### Scheduler:

```
Dispatching job: <job_id>
```

### Worker:

```
Executing job <job_id> with payload {'msg': 'Hello World'}
```

---

## 🧠 Key Concepts

* Message brokers (NATS)
* Distributed workers
* Job scheduling using Redis sorted sets
* Async processing with asyncio

---

## ⚠️ Common Issues

### ❌ ModuleNotFoundError

Always run using:

```
python -m scripts.<script_name>
```

---

### ❌ Worker not receiving jobs

* Ensure NATS is running
* Ensure scheduler is running
* Check subject: `tasks.execute`

---

### ❌ Redis connection error

Make sure Redis container is running:

```
docker ps
```

---

Happy building 🚀
