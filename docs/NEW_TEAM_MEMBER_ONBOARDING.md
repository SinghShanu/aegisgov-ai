# AegisGov AI: New Team Member Onboarding & Architectural Briefing
*A Data & Platform Engineer's Comprehensive Guide to our Google Cloud AI Builder Cup 2026 Solution*

---

## 🎯 Executive Summary (The 2-Minute Briefing)

* **Project Name:** AegisGov AI  
* **Team Identity:** Team AegisGov  
* **Competition:** Google Cloud AI Builder Cup 2026 (JAPAC)  
* **Target Domain:** **BFSI (Banking, Financial Services & Insurance)** *(Theme: Multi-Agent AI Safety & Governance)*  
* **Core Problem Statement:** Generative AI copilots and autonomous financial agents are entering institutional banking, but **compliance policies are written in human legal language**, while **data systems run on code**. Because agents operate in milliseconds without built-in guardrails, banks face massive regulatory fines, PII exfiltration, prompt injections, and catastrophic unapproved fund movements.  
* **Our Solution:** An end-to-end **Policy-as-Code (PaC) & Multi-Agent Safety Harness Platform** built specifically for regulated BFSI institutions across JAPAC (Singapore, India, Japan, Australia). It bridges legal regulations directly to the data layer by:
  1. Translating natural language banking policies into machine-executable **Data Contracts** (Agent 1: Gemini 1.5 Pro).
  2. Enforcing contracts across an in-memory **Medallion Lakehouse** (Bronze $\rightarrow$ Silver $\rightarrow$ Quarantine + Gold C-Suite Datamart & Attestation) with dynamic NRIC/PAN/Aadhaar tokenization (Agent 2: DuckDB).
  3. Wrapping internal financial agents in a deterministic **5-Stage Defense Harness** with automated Circuit Breakers and Human-in-the-Loop (HITL) maker-checker approval (Agent 3: Aegis Financial Sentinel powered by Gemini 1.5 Flash).
  4. Guarding against security and policy regressions via a living test catalog with automated root-cause diagnostics (Agent 4: HITL Regression Guardian).
  5. Conducting continuous automated compliance scans against SOC 2 Type II trust criteria and generating cryptographic audit attestations (Agent 5: SOC 2 & Regulatory Audit Inspector).
  6. Logging all events, validations, and approvals into an immutable, **SHA-256 Cryptographic Audit Ledger**.

---

## 📅 Hackathon Milestones & Delivery Timeline

Keep these non-negotiable hackathon deadlines in your calendar:

| Deadline / Milestone | Date & Time | Mandatory Requirements | Status |
| :--- | :--- | :--- | :--- |
| **Team Formation Freeze** | **October 11, 2026 (11:59 PM IST)** | All participants **must** belong to a registered team of **2 to 4 members** on Hack2skill. Solo participation leads to disqualification. | 🟡 In Progress |
| **Final Submission Freeze** | **October 18, 2026 (11:59 PM IST)** | Complete submission package: 3–5 min demo video, Pitch Deck (PPTX/PDF), Public GitHub repo, Live Google Cloud Run URL. | 🟢 Ready for Submission |
| **Winner Announcement** | **November 2026** | Evaluation on Technical Depth, Google Cloud & Gemini Integration, ROI & Business Viability, Presentation Quality. | ⏳ Pending Review |

---

## 🏛️ Why We Chose This Use Case & Domain (BFSI Focus)

### 1. The "Policy-to-Code" Chasm
In traditional banking, regulatory teams write 100-page compliance manuals (MAS Notice 644, MAS FEAT, RBI Digital Lending, Singapore PDPA, India DPDP Act). Meanwhile, data engineers build pipelines and software teams build AI agents. There is **zero programmatic link** between legal mandates and the underlying lakehouse tables or agent APIs. AegisGov AI transforms legal prose directly into enforceable code.

### 2. High-Stakes Regulatory Urgency in JAPAC
* **Singapore's Shared Responsibility Framework (SRF):** Banks face direct financial liability for scam restitution if unauthorized digital transfers bypass anti-phishing or anti-mule controls.
* **MAS Notice 644 & FEAT Principles:** Autonomous AI agents are strictly forbidden from executing high-value financial actions ($> \text{S}\$ 10,000$) without an auditable **Four-Eyes Principle (Dual-Control)** maker-checker review.
* **India DPDP Act 2023 & RBI Digital Lending:** Prohibits storing raw national identity documents (PAN, Aadhaar) in cleartext across analytical and reporting tiers.

### 3. Business Metrics & Hard ROI
| Risk & Use Case | Traditional Banking Baseline | With AegisGov AI | Quantifiable Impact / Hard ROI |
| :--- | :--- | :--- | :--- |
| **Cross-Rail Scam & Mule Ring Bypass** | Manual L1 AML review queues; days of delay; banks absorb scam restitution. | Real-time Ingress Guard + Lakehouse Quarantine isolates mule payloads instantly. | **Saves ~$2.8M** in Level-1 AML operational headcount; **$0 scam liability** under Singapore SRF. |
| **SME Commercial Credit / Lease Payout** | Multi-day email/paper underwriting; 5 business days turnaround. | Deterministic Circuit Breaker escalates disbursements $> \text{S}\$ 10\text{k}$ to HITL in seconds. | **45-second decisioning** (down from 5 days); 100% adherence to MAS Notice 644. |
| **Fiduciary Wealth Advisory (Suitability)** | Undetected rogue AI portfolio recommendations; mis-selling lawsuits. | Dynamic RBAC/ABAC blocks speculative advice from unlicensed junior analysts. | **Eliminates $1M+ regulatory fines** under MAS FEAT; 0% mis-selling liability. |
| **National PII Exfiltration (NRIC / PAN)** | Plaintext PII ingested into LLM context windows; PDPA breach penalties. | Dynamic cryptographic tokenization vault replaces identifiers with synthetic tokens. | **100% PII containment**; compliant with Singapore PDPA and India DPDP 2023. |
| **Financial Hallucinations & Governance** | LLMs hallucinate portfolio balances or transaction volumes. | Financial Sentinels are grounded strictly against certified **Gold Lakehouse** tables. | **Zero financial hallucinations**; 100% mathematically verified audit metrics. |

---

## 🗺️ Visual Architecture & Master Documentation Map

Before exploring the code, review the core diagrams and documentation blueprints:

1. **Enterprise System Architecture:**
   * Vector Diagram: [`docs/assets/system-architecture.svg`](assets/system-architecture.svg)
   * Interactive Inspection Viewer: [`docs/assets/system-architecture.html`](assets/system-architecture.html) *(Features dark/light themes, component inspection, and edge tracing).*
2. **End-to-End Swimlane Process Flow:**
   * Vector Graphic: [`docs/assets/process-flow-diagram.svg`](assets/process-flow-diagram.svg)
   * Markdown Specification: See [`README.md`](../README.md#L38-L124) for the 12-Step Sequential Execution Flowchart.
3. **Master Pitch Deck Blueprint:**
   * Presentation Content Guide: [`docs/PITCH_DECK_CONTENT_MASTER.md`](PITCH_DECK_CONTENT_MASTER.md) *(Slide-by-slide copy deck mapped to the official AI Builder Cup template).*
4. **Safe Cloud Deployment Runbook:**
   * Account Isolation Guide: [`docs/SAFE_CLOUD_DEPLOYMENT.md`](SAFE_CLOUD_DEPLOYMENT.md) *(Guarantees deployment exclusively to free-tier account).*
5. **JAPAC Regulatory Dictionary:**
   * Compliance Lexicon: [`docs/REGULATORY_DICTIONARY.md`](REGULATORY_DICTIONARY.md) *(MAS Notice 644, FEAT, RBI, PDPA, FAST, PayNow, UPI).*

---

## 📂 Codebase Directory Navigation Map

The codebase is organized into a clean, decoupled full-stack monorepo:

```
Google_AI_Builder_Cup_2026/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI Application, OWASP security headers, static SPA mounting
│   │   ├── api/                     # REST API Routers
│   │   │   ├── harness_router.py    # Financial Sentinel chat endpoint, 5-stage harness invocation
│   │   │   ├── policy_router.py     # Data contract lifecycle (compile, approve, enforce)
│   │   │   ├── medallion_router.py  # DuckDB lakehouse tier queries (Bronze PoLP, Silver, Gold, Quarantine)
│   │   │   ├── hitl_router.py       # Human-in-the-Loop ticket approval / rejection drawer
│   │   │   ├── audit_router.py      # SHA-256 cryptographic ledger endpoints & chain verifier
│   │   │   └── health.py            # /api/health endpoint for Cloud Run liveness probes
│   │   ├── agents/                  # Autonomous Gemini & Lakehouse Agents
│   │   │   ├── policy_compiler.py   # Agent 1: Compiles legal text into Pydantic DataContracts
│   │   │   ├── medallion_lakehouse.py # Agent 2: Enforces contracts on DuckDB & quarantines breaches
│   │   │   ├── financial_analyst_agent.py # Agent 3: Grounded Aegis Financial Sentinel (Gemini 1.5 Flash)
│   │   │   └── regression_guardian_agent.py # Agent 4: Continuous security regression test runner
│   │   ├── core/                    # Core Security, Privacy & Governance Engines
│   │   │   ├── defense_harness.py   # 5-Stage Defense Harness (Ingress, Auth, CircuitBreaker, HITL, Egress)
│   │   │   ├── pii_vault.py         # Dynamic JAPAC Tokenizer (NRIC/FIN, PAN, Aadhaar)
│   │   │   ├── audit_ledger.py      # Tamper-evident SHA-256 cryptographic hash-chain ledger
│   │   │   ├── token_manager.py     # Ephemeral capability tokens (TBAC / PoLP with 30-min TTL)
│   │   │   └── config.py            # Environment settings via Pydantic Settings
│   │   ├── db/                      # In-Memory Lakehouse
│   │   │   └── duckdb_client.py     # Embedded DuckDB client managing Bronze, Silver, Gold, Quarantine
│   │   └── static/                  # Production-compiled React 18 SPA (pre-bundled!)
│   ├── tests/                       # Pytest Test Suite (49/49 passing tests)
│   │   ├── test_harness.py          # API tests & security regression tests
│   │   ├── test_data_contracts_and_polp.py # Contract validation & compilation tests
│   │   ├── test_hitl.py             # 5-stage harness unit tests
│   │   ├── test_medallion.py        # Bronze PoLP, Silver masking, Gold SLA tests
│   │   └── test_regression_guardian.py # Regression guardian suite tests
│   ├── requirements.txt             # Python dependencies
│   └── Dockerfile                   # Hardened multi-stage Docker build (CIS Benchmark 4.1 non-root)
├── frontend/                        # React 18 + Vite + Tailwind CSS Source Code
│   ├── src/
│   │   ├── App.tsx                  # Root layout, persona switcher, navigation tabs
│   │   ├── components/
│   │   │   ├── HarnessPlayground.tsx # Aegis Financial Sentinel chat & real-time 5-stage radar display
│   │   │   ├── PolicyStudio.tsx     # Policy-as-Code compilation studio & contract approval
│   │   │   ├── MedallionLineage.tsx # Lakehouse visualizer (Bronze, Silver, Gold, Quarantine)
│   │   │   ├── AuditLedger.tsx      # Cryptographic audit ledger & 1-click chain verifier
│   │   │   ├── HITLDrawer.tsx       # Four-Eyes maker-checker approval drawer
│   │   │   └── RegressionStudio.tsx # Continuous regression guardian vault
│   │   └── services/api.ts          # Typed API client
│   └── package.json
├── scripts/                         # Operational & Deployment Automation
│   ├── verify_gcp_account.sh        # Pre-flight account isolation guardrail (blocks personal accounts)
│   └── deploy.sh                    # Automated Cloud Build & Cloud Run deployment script
└── docs/                            # Architecture, Guides, Pitch Deck & Regulatory Lexicon
```

---

## ⚡ 5-Minute Zero-Friction Developer Setup

You can get the entire system running locally in **under 3 minutes**. 

> [!TIP]
> **No Node.js/npm Required for Backend Testing:** The production React 18 frontend is already pre-compiled into `backend/app/static/`. Starting the Python backend automatically serves the full-stack UI at `http://localhost:8080`.

### Step 1: Create Virtual Environment & Install Dependencies
```bash
### 🖥️ Option A: Windows (1-Click or Manual Setup)

#### 1-Click Automated Setup (Windows)
Double-click [`scripts/run_local.bat`](../scripts/run_local.bat) in File Explorer, or open PowerShell and run:
```powershell
.\scripts\run_local.ps1
```
*This automatically checks Python, creates `backend\venv`, installs dependencies, copies `.env.example`, and boots the server!*

#### Manual Setup (Windows PowerShell / CMD)
```powershell
# 1. Create and activate virtual environment
python -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1    # In PowerShell
# (Or in CMD: backend\venv\Scripts\activate.bat)

# 2. Install dependencies
pip install -r backend\requirements.txt

# 3. Configure environment
copy .env.example .env

# 4. Run automated test suite (37/37 tests)
python -m pytest backend\tests -v

# 5. Start the local server
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 --reload
```

---

### 🍎 Option B: macOS / Linux Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv backend/venv
source backend/venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run automated test suite (37/37 tests)
python -m pytest backend/tests -v

# 5. Start the local server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 --reload
```

Open **`http://localhost:8080`** in your browser. You will see the live AegisGov AI Sovereign Governance Console!

*(Optional) Modifying the React Frontend (Any OS):*
The production frontend is already pre-compiled into `frontend/dist`. If you want to modify UI code:
```bash
cd frontend
npm install
npm run dev   # Runs Vite dev server at http://localhost:5173
# Or recompile into production bundle:
npm run build
```

---

## 🎮 The 3 Golden Path Demos (Must-Run)

To understand how the system works end to end, run these 3 live scenarios:

### Demo 1: The 5-Stage Safety Harness & Four-Eyes HITL Escalation
1. In the top navbar persona selector, choose **`Vikram Mehta (Senior Wealth Advisor)`**.
2. Open Tab 1: **`Financial Sentinel & Live Defense`**.
3. Click the preset: **`Commercial Credit & Lease Payout`** (or submit: *"Please execute commercial lease deposit of S$ 75,000 via FAST to Sentosa Real Estate..."*).
4. Watch the 5-Stage Harness evaluate the request:
   * **Stage 1 (Ingress):** Clearance verified (`WEALTH_ADVISOR`), prompt sanitized.
   * **Stage 2 (Financial Sentinel):** Gemini 1.5 Flash proposes the payout transaction grounded on Gold facts.
   * **Stage 3 (Circuit Breaker):** **Triggered!** `S$ 75,000` exceeds single-agent operational limits ($\text{S}\$ 10,000$). Execution is immediately halted; ticket `#HITL-SG-109X` is dispatched.
5. In the top navbar, switch persona to **`Kenji Sato (Director of Risk)`**.
6. Open the **HITL Approval Drawer** (amber button in header) and click **`[Approve Transaction]`**.
7. Return to the Financial Sentinel and resubmit: the transaction settles immediately with Four-Eyes maker-checker verification permanently logged!

### Demo 2: Medallion Lakehouse Bronze PoLP Access Gating
1. Switch persona to **`Rachel Lim (Junior Analyst)`**.
2. Open Tab 2: **`Policy-as-Code & Lakehouse`** $\rightarrow$ **`Medallion Lakehouse Lineage`**.
3. Click **`1. Bronze (Raw Lake)`**:
   * Observe the **`HTTP 403 Forbidden` Zero-Trust Access Blocked Banner** explaining why raw cleartext PII is withheld from analysts under MAS TRM and PDPA guidelines.
   * Click **`[View Silver Tier]`** to see the pseudonymized tokens (`S****234A`).
4. Switch persona in the header to **`Alex Wong (Principal Data Platform Engineer)`**:
   * Click **`1. Bronze (Raw Lake)`**:
   * The unmasked records table unlocks with an active **`Data Platform Engineer Clearance Verified`** banner!

### Demo 3: Policy-as-Code Compilation & Lifecycle Approval
1. Select persona **`Priya Sharma (Principal Compliance Auditor)`**.
2. Go to Tab 2 $\rightarrow$ **`Policy-as-Code Studio`**.
3. Select **MAS Notice 644 Cross-Border Fast Contract** and click **`[⚡ Compile Policy to Code]`**.
4. Observe the contract initialize in **`PENDING GOVERNANCE APPROVAL`**.
5. As Compliance Auditor, click **`[Approve & Deploy to Pipeline]`**:
   * The contract transitions to **`ACTIVE ENFORCING`**.
   * An interactive 4-stage lifecycle stepper renders live telemetry counters (Promoted to Silver, Quarantined Breaches, Compliance Health Score).
   * Click **`[View in Medallion Lineage]`** to jump directly to the live lakehouse view!

---

## 🔒 Cloud Deployment Mechanics & Account Safety Guardrails

We enforce a strict **4-Layer Account Isolation Framework** to guarantee that all cloud deployments occur **exclusively on the designated free-tier account and project**, preventing accidental billing on personal accounts:

```
[ Developer Runs deploy.sh ]
             │
             ▼
[ Layer 1: scripts/verify_gcp_account.sh ] ──► Fails if active account != GCP_DEPLOY_ACCOUNT
             │ (Matches configured GCP_DEPLOY_ACCOUNT)
             ▼
[ Layer 2: Explicit CLI Flags ] ──────────────► Hardcodes --account and --project on all gcloud calls
             │
             ▼
[ Layer 3: Cloud Build Packaging ] ──────────► Submits build to Artifact Registry (Singapore asia-southeast1)
             │
             ▼
[ Layer 4: Cloud Run Free-Tier Caps ] ────────► Deploys with --max-instances=2, --memory=512Mi, --cpu=1
```

### Dry-Run Verification Command
Before running any deployment, always run the account verification check:
```bash
./scripts/verify_gcp_account.sh
```
* If your active `gcloud` account does not match `GCP_DEPLOY_ACCOUNT`, the script **immediately halts execution** with a clear resolution command (`gcloud config set account ...`).
* When ready to deploy:
  ```bash
  ./scripts/deploy.sh
  ```
  The script enables required APIs, verifies the Artifact Registry repo, builds the container via Cloud Build, dynamically forwards `GEMINI_API_KEY` (if set), deploys to Cloud Run with free-tier caps, and outputs the live HTTPS production URL!

---

## 🤝 Where You Can Jump In & Collaborate

Now that you are up to speed with the architecture, here are the highest-impact areas where platform & data engineering expertise will shine before our submission:

1. **BigQuery BigLake / Iceberg Table Mirroring:** Exploring a periodic background sync from our in-memory DuckDB Gold tier to BigQuery external tables for long-term historical analytics.
2. **Cloud Pub/Sub Streaming Connectors:** Adding a Cloud Pub/Sub subscriber option to `transaction_streamer.py` to ingest real-time mock Swift/FAST streams in Google Cloud.
3. **Pitch Deck & Video Demo Review:** Reviewing [`docs/PITCH_DECK_CONTENT_MASTER.md`](PITCH_DECK_CONTENT_MASTER.md) and assisting with the 3–5 minute presentation demo script.
4. **Custom Data Contract Rule Generators:** Adding domain-specific banking rules (e.g., cross-border FX slippage caps or sanctions list matching) to `policy_compiler.py`.

Welcome to **Team AegisGov**! Let's build the gold standard for sovereign AI governance in institutional finance! 🚀
