# TruxTrace

**TruxTrace** is a powerful Linux user simulation tool designed to emulate realistic command-line behavior for single and multiple users. It enables analysts, developers, and educators to simulate Linux user activity, generate forensic artifacts, and test scenarios in a safe, controlled environment.

---

## 🐧 Why the Name?

- **Tux**: The Linux mascot, representing the open-source spirit and system TruxTrace is built for.
- **Trace**: Emphasizes the tool’s goal—simulating and tracing user behavior for deeper insight, testing, or forensic purposes.

---

## 🚀 Features

- Simulates single and multi-user Linux activity
- Supports command execution, file system interactions, and cron jobs
- Creates realistic artifacts (e.g., `.bash_history`, `/var/log` entries)
- User profiles: Admin, Developer, Sysadmin, General
- Docker and manual installation support
- Useful in digital forensics and education

---

## 📚 Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Manual](#manual-installation)
  - [Docker](#docker-installation)
- [Getting Started](#getting-started)
- [Single User Simulation](#single-user-simulation)
- [Multiple User Simulation](#multiple-user-simulation)
- [Generated Artifacts](#generated-artifacts)
- [User Profiles](#user-profiles)
- [FAQ](#faq)
- [Conclusion](#conclusion)

---

## 🧩 Prerequisites

### System Requirements

- Linux system (or WSL/macOS for limited support)
- Python 3.8+

### Software Dependencies

- Listed in `requirements.txt`  
  Install via:

  ```bash
  pip install -r requirements.txt
