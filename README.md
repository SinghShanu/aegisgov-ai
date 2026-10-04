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

```mermaid
flowchart TD
    subgraph JAPAC_Inputs["JAPAC BFSI Data & Regulatory Policies"]
        RegPolicies["Regulatory Policies<br>(MAS FEAT, RBI, Singapore PDPA, India DPDP)"]
        RawStreams["Raw JAPAC Financial Streams<br>(SGD PayNow, INR UPI/IMPS, FAST Transfers, KYC Documents)"]
    end

    subgraph Agent_1["Agent 1: Policy-as-Code Compiler (Gemini 1.5 Pro)"]
        Compiler["Policy-to-Code Agent"]
        Contracts["Machine-Executable Data Contracts<br>& RBAC/ABAC/TBAC Matrix (Pydantic / JSON)"]
        RegPolicies --> Compiler --> Contracts
    end

    subgraph Agent_2["Agent 2: Medallion Contract Inspector (DuckDB Lakehouse)"]
        Bronze["Bronze (Raw JAPAC Lakehouse)<br>Dirty Schemas, Plaintext NRIC/PAN/UPI"]
        Silver["Silver (Cleaned & Vault-Tokenized)<br>Curated SGD/INR Transactions, Masked PII"]
        Gold["Gold (Certified AI-Ready Tier)<br>Risk Metrics, Basel III / AML Certified Aggregations"]
        Quarantine["Quarantine Vault<br>Malformed Schemas & Contract Breaches"]

        RawStreams --> Bronze
        Contracts --> Agent_2
        Bronze -->|Schema Validation & PII Tokenization| Silver
        Bronze -.->|Policy Breach| Quarantine
        Silver -->|Certified Financial Aggregations & SLAs| Gold
    end

    subgraph Defense_Harness["Agentic AI Governance & Safety Harness (Gemini 1.5 Flash + Deterministic Guard)"]
        subgraph Ingress["1. Ingress Guard"]
            UserPrompt["Employee / System Prompt"]
            AccessCheck["RBAC / ABAC / TBAC Verification (PoLP)"]
            ThreatScanner["Prompt Injection & Attack Scanner"]
            TokenizePII["Dynamic JAPAC PII Tokenizer (NRIC/PAN)"]
            UserPrompt --> AccessCheck --> ThreatScanner --> TokenizePII
        end

        subgraph Core_Agent["2. Enterprise Financial Agent (Gemini 1.5 Pro / Flash)"]
            LLM["Financial Analyst Copilot"]
            CircuitBreaker["Circuit Breaker & Four-Eyes Gate<br>(Actions > S$ 10,000 / ₹ 5 Lakhs)"]
            TokenizePII --> LLM
            LLM <-->|Tool Execution| CircuitBreaker
            CircuitBreaker <-->|Certified Queries Only| Gold
        end

        subgraph HITL_Approval["3. Human-in-the-Loop (HITL) Center"]
            PendingQueue["HITL Approval Drawer"]
            HumanOfficer{"Authorized Reviewer<br>(Compliance / Risk Officer)"}
            CircuitBreaker -->|Mandatory Gate| PendingQueue
            PendingQueue --> HumanOfficer
        end

        subgraph Egress["4. Egress Guard"]
            GroundingCheck["Hallucination & Gold Factuality Verifier"]
            MASFilter["MAS FEAT Bias & Advisory Filter"]
            SecretLeakFilter["Secret & Token Leak Scanner"]
            LLM --> GroundingCheck --> MASFilter --> SecretLeakFilter
            HumanOfficer -->|Approved Action| GroundingCheck
        end
    end

    subgraph Telemetry_Console["Enterprise Governance Console (React + Vite + Tailwind)"]
        LineageGraph["Interactive Medallion Lineage"]
        HarnessMonitor["Live AI Safety Harness Telemetry & Threat Radar"]
        AuditLedger["Cryptographic Tamper-Evident Audit Ledger"]
        PolicyStudio["Natural Language -> Policy-as-Code Studio"]
    end

    SecretLeakFilter -->|Sanitized Compliant Output| FinalOutput["Safe Response to Employee / Customer"]
    Agent_2 --> LineageGraph
    Agent_2 --> AuditLedger
    Defense_Harness --> HarnessMonitor
    Defense_Harness --> AuditLedger
    Contracts --> PolicyStudio
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
