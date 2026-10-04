# AegisGov AI: New Team Member Onboarding & Architectural Briefing
*A Data & Platform Engineer's Guide to our Google Cloud AI Builder Cup 2026 Solution*

---

## 🎯 Executive Summary (The 2-Minute Briefing)

**Project Name:** AegisGov AI  
**Team Identity:** Team AegisGov  
**Competition Track:** Google Cloud AI Builder Cup 2026 (JAPAC) — *Future of Work & Enterprise Productivity*  
**Core Problem Statement:** Generative AI copilots and autonomous financial agents are entering institutional banking, but **compliance policies are written in human legal language**, while **data systems run on code**. Because agents operate in milliseconds without built-in guardrails, banks face massive regulatory fines, PII exfiltration, prompt injections, and catastrophic unapproved fund movements.  
**Our Solution:** An end-to-end **Policy-as-Code (PaC) & Multi-Agent Safety Harness Platform** built specifically for regulated BFSI institutions across JAPAC (Singapore, India, Japan, Australia). It bridges legal regulations directly to the data layer by:
1. Translating natural language banking policies into machine-executable **Data Contracts**.
2. Enforcing contracts across a **Medallion Lakehouse** (Bronze $\rightarrow$ Silver $\rightarrow$ Gold + Quarantine).
3. Wrapping internal AI copilots in a deterministic **5-Stage Defense Harness** with human-in-the-loop (HITL) maker-checker approval.

---

## 🏛️ Why We Chose This Use Case & Domain

### 1. The "Policy-to-Code" Chasm
In traditional banking, regulatory teams write 100-page compliance manuals (MAS Notice 644, MAS FEAT, RBI Digital Lending, Singapore PDPA, India DPDP Act). Meanwhile, data engineers build pipelines and software teams build AI copilots. There is **zero programmatic link** between legal mandates and the underlying lakehouse tables or agent APIs.

### 2. High-Stakes Regulatory Urgency in JAPAC
* **Singapore's Shared Responsibility Framework (SRF):** Banks now face direct financial liability for scam restitution if unauthorized digital transfers bypass anti-phishing or anti-mule controls.
* **MAS Notice 644 & FEAT Principles:** Autonomous AI agents are strictly forbidden from executing high-value financial actions ($> \text{S}\$ 10,000$) without an auditable **Four-Eyes Principle (Dual-Control)** maker-checker review.
* **India DPDP Act 2023 & RBI Digital Lending:** Prohibits storing raw national identity documents (PAN, Aadhaar) in cleartext across analytical and reporting tiers.

---

## 📊 Business Metrics & Hard ROI Targeted

When presenting this project to judges and executives, we focus on hard quantitative outcomes, not just "AI accuracy":

| Use Case & Risk Category | Traditional Banking Baseline | With AegisGov AI | Business Metric / ROI Targeted |
| :--- | :--- | :--- | :--- |
| **Cross-Rail Scam & Mule Ring Bypass** | Manual L1 AML review queues; days of delay; banks absorb scam restitution. | Real-time Ingress Guard + Lakehouse Quarantine isolates mule payloads instantly. | **Saves ~$2.8M** in Level-1 AML operational headcount; **$0 scam liability** under Singapore SRF. |
| **SME Commercial Credit / Lease Payout** | Multi-day email/paper underwriting; 5 business days turnaround. | Deterministic Circuit Breaker escalates disbursements $> \text{S}\$ 10\text{k}$ to HITL in seconds. | **45-second decisioning** (down from 5 days); 100% adherence to MAS Notice 644. |
| **Fiduciary Wealth Advisory (Suitability)** | Undetected rogue AI portfolio recommendations; mis-selling lawsuits. | Dynamic RBAC/ABAC blocks speculative advice from unlicensed junior analysts. | **Eliminates $1M+ regulatory fines** under MAS FEAT; 0% mis-selling liability. |
| **National PII Exfiltration (NRIC / PAN)** | Plaintext PII ingested into LLM context windows; PDPA breach penalties. | Dynamic cryptographic tokenization vault replaces identifiers with synthetic tokens. | **100% PII containment**; compliant with Singapore PDPA and India DPDP 2023. |
| **Financial Hallucinations & Governance** | LLMs hallucinate portfolio balances or transaction volumes. | AI copilots are grounded strictly against certified **Gold Lakehouse** tables. | **Zero financial hallucinations**; 100% mathematically verified audit metrics. |

---

## 🏗️ End-to-End Architecture: A Data & Platform Engineer's View

As a platform and data engineer, you will immediately recognize the core architectural pillars:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                    JAPAC INGRESS RAILS                                │
│                   (Singapore FAST / PayNow, India UPI / IMPS, SWIFT)                   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     LAYER 1: POLICY-AS-CODE COMPILER (AGENT 1)                         │
│  Input: Natural Language Policy (e.g. MAS Notice 644 / RBI Digital Lending)            │
│  Output: Machine-Readable Data Contracts (Pydantic / JSON Schema with Masking Rules)  │
│  Governance Gate: PENDING_APPROVAL ──► Compliance Officer Sign-off ──► ACTIVE_ENFORCING│
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     LAYER 2: MEDALLION LAKEHOUSE PIPELINE (AGENT 2)                    │
│                                                                                        │
│   ┌────────────────────────┐         ┌────────────────────────┐                        │
│   │   1. BRONZE (Raw Lake) │         │   3. QUARANTINE VAULT  │                        │
│   │   Raw cleartext NRIC,  │         │   Negative amounts,    │                        │
│   │   PAN, dirty schemas   │ ──────► │   corrupted payloads,  │                        │
│   │   [PoLP: Data Engineer │         │   breaches isolated    │                        │
│   │    Access ONLY]        │         └────────────────────────┘                        │
│   └───────────┬────────────┘                                                           │
│               │ (Schema Validation & Dynamic Vault Tokenization)                       │
│               ▼                                                                        │
│   ┌────────────────────────┐         ┌────────────────────────┐                        │
│   │   2. SILVER (Curated)  │         │   4. GOLD (Certified)  │                        │
│   │   Pseudonymized PII,   │ ──────► │   Audited aggregates,  │ ──► Downstream Copilot │
│   │   FX normalized (SGD)  │         │   AI-ready analytics   │     & BI Reporting     │
│   └────────────────────────┘         └────────────────────────┘                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               LAYER 3: AGENTIC AI 5-STAGE DEFENSE HARNESS (AGENT 3)                    │
│                                                                                        │
│  1. Ingress Guard     ──► Prompt injection scanner + PII tokenization                  │
│  2. Identity Auth     ──► RBAC (Role) + ABAC (Jurisdiction) + TBAC (30-min TTL)       │
│  3. Circuit Breaker   ──► Deterministic trigger (> S$ 10,000 / > ₹ 5 Lakhs)            │
│  4. HITL Center       ──► Four-Eyes Maker-Checker Review (Risk Officer Sign-Off)       │
│  5. Egress DLP        ──► Secret/key interception + Tamper-Evident SHA-256 Ledger      │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               LAYER 4: REGRESSION GUARDIAN & QA VAULT (AGENT 4)                        │
│  Automated test catalog ensuring prompt or logic tweaks never re-introduce regressions │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Engineering Concepts to Know

### 1. Dynamic Data Contracts (Not Just Static Pydantic Schemas)
* **What it is:** Instead of hardcoding data contracts in code, our **Policy Compiler Agent** reads regulatory text and compiles a `DataContract` object containing:
  - Governing regulation (`MAS Notice 644`, `RBI Digital Lending`)
  - Target Lakehouse Tier (`SILVER`)
  - Column rules: `column_name`, `data_type`, `nullable`, `pii_type`, `masking_strategy`
* **Change Management Lifecycle (SOC 2 CC8.1):** When generated, a contract enters `PENDING_APPROVAL`. Only a user with `COMPLIANCE_OFFICER` or `RISK_OFFICER` role can review and approve it. Once approved, it transitions to `ACTIVE_ENFORCING`, triggers an automated lakehouse inspection cycle, records telemetry, and logs to the cryptographic ledger.

### 2. Principle of Least Privilege (PoLP) on the Bronze Layer
* **The Problem:** Many data lakehouses accidentally grant broad read access to the raw Bronze tier, exposing unmasked customer NRICs, PANs, and bank accounts to analysts and AI models.
* **Our Solution:** The backend API (`/api/medallion/tier/BRONZE`) enforces **strict PoLP tier-gating**:
  - Only **Alex Wong (Principal Data Platform Engineer)** with `view_bronze_raw` clearance can inspect raw Bronze cleartext data.
  - Junior Analysts, Wealth Advisors, and Compliance Auditors receive an immediate `HTTP 403 Forbidden` and an institutional **Zero-Trust Access Blocked Banner** directing them to curated Silver or Gold tiers.

### 3. Cryptographic SHA-256 Audit Ledger (Tamper-Evident Chain)
* Every prompt, security denial, policy compilation, HITL ticket resolution, and stream burst is logged into a sequential, hash-chained ledger (`AuditLedger`).
* Each block contains `previous_hash`, `timestamp`, `user_id`, `decision`, and its own `entry_hash`.
* **Privacy Hardening:** Prior to hashing, all action strings automatically pass through `pii_vault.scan_and_sanitize_text()`, ensuring that **zero cleartext customer PII is ever sealed into the immutable chain**.

### 4. Continuous QA Regression Guardian (Agent 4)
* A specialized agent pre-seeded with 6 certified baseline security test scenarios.
* When developers or testers discover subtle prompt injection vulnerabilities or RBAC edge cases, they can click `[🛡️ Save to QA Vault]` to permanently retain the verbatim prompt, expected status, and discovery notes.
* The 1-click **Regression Runner** executes the suite, benchmarking latency, evaluating keyword assertions, and computing a **Regression Risk Level**.

---

## 🛠️ The Tech Stack & GCP Infrastructure

| Layer / Component | Technology Used | Why We Chose It |
| :--- | :--- | :--- |
| **Frontend UI** | React 18, TypeScript, Tailwind CSS, Lucide Icons, Vite | Single-page application compiled into a single static distribution; fast, zero lag. |
| **Backend API** | Python 3.11, FastAPI, Uvicorn, Pydantic v2 | High-throughput asynchronous REST API; native OpenAPI docs; strict schema typing. |
| **In-Memory Lakehouse** | DuckDB (Embedded OLAP) + BigQuery compatibility | Blazing-fast SQL analytics on Parquet/JSON streams without heavy cluster overhead. |
| **Generative AI Core** | Google GenAI SDK (`google-genai`), Gemini 2.0 Flash & Gemini 1.5 Pro | Sub-second agentic reasoning, structured JSON Schema extraction, enterprise SLA. |
| **Cloud Hosting** | Google Cloud Run (`asia-southeast1` Singapore) | Serverless container execution; scale-to-zero ($0 idle cost); capped at 2 instances (Free Tier). |
| **Cloud CI/CD** | Google Cloud Build + Artifact Registry | Automated cloud packaging; CIS Docker Benchmark 4.1 non-root container (`appuser`). |
| **Security & Privacy** | Custom PII Vault Tokenizer, SHA-256 Hash Chain, OWASP Defense Headers | Bank-grade zero-trust perimeter defense; compliant with PDPA, DPDP, and MAS TRM. |

---

## 🚦 How to Run & Demo the System (5-Minute Quickstart)

### 1. Start the Local Server
```bash
cd /Users/shanusingh/Google_AI_Builder_Cup_2026
source backend/venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 --reload
```
Open your browser at **`http://localhost:8080`**.

### 2. Run the Automated Test Suite (37 / 37 Tests)
```bash
PYTHONPATH=. backend/venv/bin/pytest backend/tests -v
```
All 37 unit and integration tests execute in **< 1.0 second**.

### 3. Key Golden Paths to Demo

#### Demo 1: The 5-Stage Safety Harness & Four-Eyes HITL Escalation
1. In the top navbar, select **`Vikram Mehta (Senior Wealth Advisor)`**.
2. Go to Console 1: **`AI Copilot & Live Defense`**.
3. Click the preset: **`Commercial Credit & Lease Payout`** (or submit: *"Please execute commercial lease deposit of S$ 75,000 via FAST to Sentosa Real Estate..."*).
4. Watch the 5-Stage Harness execute:
   - Stage 1: Role authorized (`WEALTH_ADVISOR`).
   - Stage 2: Ingress clean.
   - Stage 3: **Circuit Breaker Triggers!** S$ 75,000 exceeds single-agent operational limits ($\text{S}\$ 10,000$).
   - Returns `PENDING_HITL_APPROVAL` and dispatches ticket `#HITL-SG-109X`.
5. Switch persona to **`Kenji Sato (Director of Risk)`** in the top navbar.
6. Open the **HITL Approval Center** (amber button in header) and click **`[Approve Transaction]`**.
7. Return to the Copilot and resubmit: the transaction settles immediately with Four-Eyes replay protection verified!

#### Demo 2: Medallion Lakehouse Bronze PoLP Access Gating
1. Switch persona to **`Rachel Lim (Junior Analyst)`**.
2. Navigate to Console 2: **`Policy-as-Code & Lakehouse`** $\rightarrow$ **`Medallion Lakehouse Lineage`**.
3. Click **`1. Bronze (Raw Lake)`**:
   - Notice the **`HTTP 403 Forbidden` Zero-Trust Access Blocked Banner** explaining why raw PII is hidden from analysts under MAS TRM guidelines.
   - Click **`[View Silver Tier]`** to see the pseudonymized tokens (`S****234A`).
4. Switch persona in the header to **`Alex Wong (Principal Data Platform Engineer)`**:
   - Click **`1. Bronze (Raw Lake)`**:
   - The unmasked records table unlocks with an active **`Data Platform Engineer Clearance Verified`** banner!

#### Demo 3: Policy-as-Code Compilation & Lifecycle Approval
1. Select persona **`Priya Sharma (Principal Compliance Auditor)`**.
2. Go to Console 2 $\rightarrow$ **`Policy-as-Code Studio`**.
3. Select **MAS Notice 644 Cross-Border Fast Contract** and click **`[⚡ Compile Policy to Code]`**.
4. Observe the contract initialize in **`PENDING GOVERNANCE APPROVAL`**.
5. As Compliance Auditor, click **`[Approve & Deploy to Pipeline]`**:
   - Watch the contract transition to **`ACTIVE ENFORCING`**.
   - An interactive 4-stage lifecycle stepper renders live telemetry counters (Promoted to Silver, Quarantined Breaches, Compliance Health Score).
   - Click **`[View in Medallion Lineage]`** to jump directly to the live lakehouse view!

---

## 🤝 Where You Can Jump In

Now that you understand the architecture, here are the highest-impact areas where platform & data engineering expertise shines:
1. **Streaming Rails Integration:** Extending `transaction_streamer.py` to connect directly to Google Cloud Pub/Sub topics for live multi-region ingestion.
2. **Lakehouse Connectors:** Adding a BigQuery BigLake Iceberg table sync to mirror our embedded DuckDB tiers directly into cloud storage.
3. **Advanced Data Contract Rules:** Adding custom anomaly detection or statistical schema-drift checks to the Policy Compiler Agent.
4. **Cloud Run Infrastructure:** Helping test and verify our automated deployment scripts (`./scripts/deploy.sh`) on Google Cloud Run.

Welcome to **Team AegisGov**! Let's build the future of autonomous, compliant banking! 🚀
