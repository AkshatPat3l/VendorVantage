# THE VENDOR VANTAGE | Pro Analytics Master

### Advanced Supplier Intelligence for the Modern Retail Ecosystem

[![Live on Render](https://img.shields.io/badge/Live%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://your-app-name.onrender.com)
[![Docker Ready](https://img.shields.io/badge/Containerized-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

---

## Project Overview

Vendor Vantage is a high performance retail analytics dashboard designed to solve the data noise problem for suppliers. Built with a Star Schema architecture, it transforms raw inventory snapshots into actionable intelligence. It benchmarks prices against brand averages, tracks real time market share, and provides AI driven stock health insights.

This is not just an inventory list. It is an Intelligence Layer designed to help vendors make data driven decisions that protect margins and drive volume in a competitive retail environment.

---

## Key Intelligence Features

### 1. The Intelligence Sidebar (OLAP Concepts)

- **Live Market Share Percentage:** A real time analytical calculation that determines brand dominance based on current filtered value.
- **Supplier Vibe Check:** A simulated AI logic engine that analyzes inventory concentration and flags high risk supply chain dependencies.
- **Distribution Modeling:** Visual SKU share tracking using Chart.js to identify gaps in brand representation.

### 2. Relational Price Benchmarking

- Uses SQL Window Functions to calculate brand specific price averages in a single database pass.
- **Automated Flagging:** Automatically badges items as PREMIUM or VALUE based on a variance from the brand average.
- **Contextual UI:** High contrast info icons with lowercase styling provide different strategic insights for premium or value pricing on hover.

### 3. Star Schema Architecture

- **Fact Table:** fact_inventory_snapshots (Capturing price, rating, and date specific metrics).
- **Dimension Tables:** dim_products and dim_brands (Maintaining strict referential integrity for deep analytical joins).

---

## Tech Stack

- **Backend:** Python / Flask
- **Database:** PostgreSQL (Star Schema optimized)
- **Frontend:** HTML5 / CSS3 / JavaScript (Industrial Pro Theme)
- **Analytics:** Chart.js / SQL Aggregations
- **DevOps:** Docker (Containerized for seamless deployment)
- **Hosting:** Render (GCP TOR ZONE 1 Ready)

---

## Installation and Local Setup

1. **Clone the repository:**
   git clone https://github.com/AkshatPat3l/hd-vendor-vantage.git
2. **Build the container:**
   docker build -t vendor-vantage .
3. **Run the Sync Master:**
   docker run -p 5000:5000 vendor-vantage

---

## Developed By

**Akshat Patel**
Software Engineer | Full Stack Developer
Specializing in Data Driven Retail Analytics
