# AegisGov AI: JAPAC BFSI Enterprise Policy-as-Code & Multi-Agent Safety Harness

[![Google Cloud AI Builder Cup 2026](https://img.shields.io/badge/Google%20Cloud-AI%20Builder%20Cup%202026-4285F4?logo=google-cloud&logoColor=white)](https://hack2skill.com)
[![Track](https://img.shields.io/badge/Track-Future%20of%20Work%20%26%20Enterprise%20Productivity-0ea5e9)](#)
[![Deployment](https://img.shields.io/badge/Deployed%20on-Google%20Cloud%20Run-34A853?logo=google-cloud&logoColor=white)](#)
[![Regionalization](https://img.shields.io/badge/Currencies-SGD%20%7C%20INR%20%7C%20JPY-F59E0B)](#)
[![Compliance](https://img.shields.io/badge/Regulatory-MAS%20FEAT%20%7C%20RBI%20%7C%20PDPA%20%7C%20DPDP-10B981)](#)

AegisGov AI is an enterprise-grade AI governance, data contract, and runtime safety platform engineered specifically for regulated financial institutions across the **JAPAC region (Singapore, India, Japan, Australia)**.

Built for the **Google Cloud AI Builder Cup 2026**, AegisGov AI bridges corporate compliance policies with technical execution. It compiles natural language regulations into machine-executable **Policy-as-Code (PaC)** across a **Medallion Data Architecture (Bronze &rarr; Silver &rarr; Gold)**, enforces **RBAC / ABAC / TBAC** least-privilege access controls, wraps agent communications in a **defense-in-depth safety harness**, and provides a zero-bypass **Human-in-the-Loop (HITL) Approval Center** for high-risk financial actions.

---

## 🏛️ Executive Problem Statement

Enterprise banks and financial services institutions across JAPAC face a trillion-dollar hurdle when deploying generative AI and autonomous agents:
1. **The Policy-to-Code Chasm:** Compliance mandates (MAS Notice 644, MAS FEAT principles, RBI Digital Lending, Singapore PDPA, and India DPDP Act) exist as hundreds of pages of legal text. Data engineering pipelines and internal AI agents have no automated way to enforce them.
2. **Data Leakage & Cross-Border Sovereign Violations:** Raw transactional records contain cleartext Singapore NRIC/FIN, Indian PAN, Aadhaar, and credit card numbers. Without dynamic tokenization, sensitive customer data leaks directly into internal LLM context windows.
3. **Unregulated Autonomous Actions:** Autonomous agents given API access to core banking or payment rails can initiate catastrophic high-value transactions or fall prey to prompt injections, context poisoning, and hallucinated financial advice.

**AegisGov AI solves this with a Tri-Agent Architecture and a multi-layered governance harness.**

---

## 📐 System Architecture

<p align="center">
  <a href="docs/assets/system-architecture.html">
    <img src="docs/assets/system-architecture.svg" alt="AegisGov AI Enterprise System Architecture" width="100%" />
  </a>
</p>

<p align="center">
  🔗 <em>Explore the interactive diagram with dark/light themes and component inspection: <strong><a href="docs/assets/system-architecture.html">Open Archify Interactive Diagram (HTML)</a></strong></em>
</p>

```mermaid
flowchart LR
    subgraph Inputs["1. JAPAC INGESTION & REGULATION"]
        direction TB
        Policies["📜 Regulatory Mandates<br/><i>(MAS FEAT · RBI · DPDP)</i>"]
        Streams["💳 Financial Streams<br/><i>(SGD PayNow · INR UPI/IMPS)</i>"]
        Users["👤 Enterprise Users<br/><i>(Compliance & Analysts)</i>"]
    end

    subgraph CompilerTier["2. POLICY COMPILER (AGENT 1)"]
        direction TB
        Agent1["🤖 Policy-to-Code Compiler<br/><b>Gemini 1.5 Pro</b>"]
        Contracts["📑 Machine Data Contracts<br/><i>(Pydantic & RBAC/TBAC Matrix)</i>"]
    end

    subgraph LakehouseTier["3. MEDALLION LAKEHOUSE (AGENT 2)"]
        direction TB
        Bronze[("🥉 Bronze Tier<br/><i>Raw Ingestion</i>")]
        Silver[("🥈 Silver Tier<br/><i>Masked & Vault-Tokenized</i>")]
        Gold[("🥇 Gold Tier<br/><i>Certified AI-Ready Facts</i>")]
        Quarantine[("🛑 Quarantine Vault<br/><i>Policy & Schema Breaches</i>")]
    end

    subgraph DefenseHarness["4. 5-STAGE AI DEFENSE HARNESS"]
        direction TB
        Ingress["🛡️ Stage 1: Ingress Guard<br/><i>PoLP Check · Zero-PII Tokenizer</i>"]
        Copilot["🤖 Stage 2: Financial Copilot<br/><b>Gemini 1.5 Flash (Agent 3)</b>"]
        CircuitBreaker{"⚡ Stage 3: Circuit Breaker<br/><i>Four-Eyes Gate >S$10K / ₹5L</i>"}
        HITL["👥 Stage 4: HITL Approval<br/><i>Dual-Custody Risk Officer</i>"]
        Egress["🔒 Stage 5: Egress Guard<br/><i>MAS FEAT Bias & Secret Scanner</i>"]
    end

    subgraph SovereignSurface["5. GOVERNANCE & AUDIT SURFACE"]
        direction TB
        SafeResponse["✅ Sanitized Response<br/><i>Verified Financial Intelligence</i>"]
        Console["📊 Governance Console<br/><i>React 18 + Vite Real-time Radar</i>"]
        AuditLedger[("🔐 Cryptographic Ledger<br/><i>SHA-256 Tamper-Evident Chain</i>")]
    end

    %% Flow Connections
    Policies --> Agent1 --> Contracts
    Contracts -->|Contract Enforce| Bronze
    Streams --> Bronze
    Bronze -->|Tokenize PII| Silver
    Silver -->|Certify SLAs| Gold
    Bronze -.->|Breach| Quarantine

    Users --> Ingress --> Copilot
    Gold ==>|Grounded Facts| Copilot
    Copilot --> CircuitBreaker

    CircuitBreaker -->|Action <= S$10K| Egress
    CircuitBreaker -->|Action > S$10K| HITL -->|Sign-Off| Egress

    Egress --> SafeResponse
    Egress -.->|Audit Trace| AuditLedger
    Quarantine -.->|Breach Event| AuditLedger
    Gold -.->|Lineage Telemetry| Console
    CircuitBreaker -.->|Risk Radar| Console

    %% Professional Color Palettes
    classDef inputStyle fill:#0f172a,stroke:#38bdf8,stroke-width:1.5px,color:#f8fafc;
    classDef compilerStyle fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef lakehouseStyle fill:#022c22,stroke:#34d399,stroke-width:1.5px,color:#f8fafc;
    classDef harnessStyle fill:#311042,stroke:#c084fc,stroke-width:1.5px,color:#f8fafc;
    classDef egressStyle fill:#172554,stroke:#60a5fa,stroke-width:1.5px,color:#f8fafc;
    classDef surfaceStyle fill:#18181b,stroke:#a1a1aa,stroke-width:1.5px,color:#f8fafc;
    classDef gateStyle fill:#450a0a,stroke:#f87171,stroke-width:2px,color:#f8fafc;

    class Policies,Streams,Users inputStyle;
    class Agent1,Contracts compilerStyle;
    class Bronze,Silver,Gold,Quarantine lakehouseStyle;
    class Ingress,Copilot,HITL,Egress harnessStyle;
    class CircuitBreaker gateStyle;
    class SafeResponse,Console,AuditLedger surfaceStyle;
```

---

## 🌟 Key Capabilities

### 1. JAPAC Native Currency & Rail Architecture
- **Primary Currencies:** **SGD (S\$)** and **INR (₹)** as first-class native currencies with cross-currency support for JPY (¥) and AUD ($).
- **Payment Rails Simulated:** Singapore **FAST** & **PayNow**, India **UPI** & **IMPS**, and international **SWIFT**.
- **JAPAC Identifier Protection:** Dynamic tokenization and masking of **Singapore NRIC/FIN** (`S****123A`) and **India PAN** (`ABCDE****F`) & **Aadhaar** (`**** **** 4321`).

### 2. Tri-Agent System Powered by Google Gemini
- **Agent 1: Policy-as-Code Compiler (Gemini 1.5 Pro)**: Reads natural language compliance mandates and compiles them into structured Pydantic and JSON Schema data contracts.
- **Agent 2: Medallion Lakehouse Inspector**: Enforces contracts across Bronze, Silver, and Gold tiers in an in-memory DuckDB engine, quarantining malformed records.
- **Agent 3: Financial Analyst Copilot (Gemini 1.5 Flash)**: Answers queries grounded strictly in certified Gold metrics, operating within the 5-stage defense harness.

### 3. Enterprise Access Control: RBAC + ABAC + TBAC (PoLP)
- **Role-Based (RBAC):** Personas include *Junior Analyst*, *Wealth Advisor*, *Compliance Officer*, and *Risk Officer*.
- **Attribute-Based (ABAC):** Clearance hierarchy (`INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`, `SECRET`) and cross-border jurisdiction locks (`SG`, `IN`, `GLOBAL`).
- **Time/Task-Based (TBAC):** Ephemeral single-session capability tokens with explicit TTLs enforcing the **Principle of Least Privilege (PoLP)**.

### 4. Human-in-the-Loop (HITL) Governance Center
Deterministic gates halt execution and require human sign-off when:
- Proposed transactions exceed **SGD 10,000** or **INR 5,00,000** (**Four-Eyes Principle**).
- External internet egress or third-party webhooks are called.
- Sensitive PII unmasking or bulk KYC export is attempted.
- High-confidence prompt injection attacks are flagged.

### 5. Cryptographic Tamper-Evident Audit Ledger
Every prompt, evaluation, tool call, and HITL decision is hashed using **SHA-256** and chained sequentially to the previous block hash (`previous_hash -> entry_hash`). The dashboard includes a one-click **"Verify Cryptographic Chain"** tool providing 100% mathematical proof of audit integrity for regulatory inspections (MAS/RBI).

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm

### 1. Clone & Set Up Backend
```zsh
# Navigate to repository
cd /Users/shanusingh/Google_AI_Builder_Cup_2026

# Activate existing virtual environment
source backend/venv/bin/activate

# (Optional) Set your Gemini API Key in .env
cp .env.example .env
# Edit .env and set GEMINI_API_KEY="your-key-here"
```

### 2. Run Backend Unit Tests
```zsh
PYTHONPATH=. backend/venv/bin/pytest backend/tests -v
```
All 12 unit tests verify RBAC/ABAC/TBAC access controls, JAPAC PII tokenization, prompt injection mitigations, circuit breakers, and Medallion pipeline execution.

### 3. Build & Run Application
```zsh
# Start Backend API Server
source backend/venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 --reload
```
In a second terminal:
```zsh
# Start Frontend Development Server
npm run dev --prefix frontend
```
Open **`http://localhost:3000`** in your browser to access the live dashboard.

---

## ☁️ Google Cloud Run Deployment

AegisGov AI is packaged as a lightweight, multi-stage Docker container serving both the React frontend and FastAPI backend on port 8080.

### One-Command Deployment via Cloud Build
```zsh
# Set your GCP Project ID
gcloud config set project aegisgov-ai-2026

# Deploy directly from source to Cloud Run in Singapore (asia-southeast1)
gcloud run deploy aegisgov-ai \
  --source . \
  --region asia-southeast1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars BASE_CURRENCY=SGD,ENVIRONMENT=production
```

---

## 🏆 Demo Scenarios for Judges

1. **Test Scenario 1 (Direct Prompt Injection):**
   * In the Copilot tab, select **"Direct Jailbreak Attack"**.
   * Observe the **Ingress Guard** immediately intercepting the attack with a critical threat score and logging the incident to the **Cryptographic Audit Ledger**.
2. **Test Scenario 2 (Four-Eyes Principle / High-Value S$ 45,000 Transfer):**
   * As *Wealth Advisor*, submit: *"Please execute a transfer of S$ 45,000 via FAST to Sentosa Real Estate Holdings for lease deposit."*
   * The **Circuit Breaker** pauses execution and generates ticket `#HITL-SG-109X`.
   * Switch persona to *Risk Officer* in the header. Open the **HITL Approval Center**, enter remarks, and approve the transaction.
3. **Test Scenario 3 (Medallion PII Masking):**
   * Navigate to the **Medallion Lakehouse** tab. Click **"Run Medallion Inspection"**.
   * Compare Bronze (showing raw Singapore NRIC `S7819234A`) against Silver (automatically masked to `S****234A`).
4. **Test Scenario 4 (Cryptographic Audit Verification):**
   * Navigate to the **Cryptographic Audit Ledger** tab.
   * Click **"Verify Cryptographic Chain"** to witness sequential block hash verification across all historical system events.

---

## 🔒 Data Governance, Security & Synthetic Privacy Declaration

* **100% Synthetic Data Guarantee:** All customer names, national identity documents (Singapore NRIC/FIN, Indian PAN, Aadhaar), account numbers, and transaction records within this repository are entirely synthetically generated for algorithm demonstration, safety benchmarking, and testing. **No real customer Personal Data (PII) is stored, processed, or exposed.**
* **Regulatory Alignment:** Designed in strict compliance with the **Singapore Personal Data Protection Act (PDPA)**, the **India Digital Personal Data Protection (DPDP) Act 2023**, and the **Monetary Authority of Singapore (MAS) TRM Notice 644 / FEAT Principles**.
* **Cryptographic Tamper-Evidence:** All system decisions, policy enforcement actions, and human approvals are immutably chained using SHA-256 cryptographic hashes with automatic PII redaction prior to hashing.
* **Principle of Least Privilege (PoLP):** Raw lakehouse data (Bronze tier) is strictly gated at both the API and UI layers, accessible exclusively to authorized Data Platform Engineers.

---

## 📄 License & Attribution
Developed for the **Google Cloud AI Builder Cup 2026 (JAPAC Edition)** by **Team AegisGov**. Powered by Google Gemini and Google Cloud Run.
