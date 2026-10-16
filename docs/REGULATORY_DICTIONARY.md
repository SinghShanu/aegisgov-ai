# 📖 AegisGov AI: JAPAC BFSI Regulatory, Legal & Security Dictionary

This dictionary explains every regulatory guideline, legal policy, technical acronym, security control, and payment rail baseline used in **AegisGov AI** in simple, plain English.

---

## ⚡ Quick-Glance Acronym Cheat Sheet

| Acronym | Full Form | What It Means in 1 Sentence |
| :--- | :--- | :--- |
| **MAS** | Monetary Authority of Singapore | Singapore's central bank and integrated financial regulatory authority. |
| **RBI** | Reserve Bank of India | India's central bank and apex monetary regulatory body. |
| **PoLP** | Principle of Least Privilege | A security rule where users/agents get only the absolute minimum permissions needed to do their specific job. |
| **FAST** | Fast And Secure Transfers | Singapore's 24/7 instant electronic interbank payment rail. |
| **UPI** | Unified Payments Interface | India's instant real-time payment system powering mobile bank-to-bank transfers. |
| **RBAC** | Role-Based Access Control | Access permissions assigned based on employee job title (e.g. Junior Analyst vs Compliance Officer). |
| **ABAC** | Attribute-Based Access Control | Access permissions evaluated dynamically using contextual attributes (e.g. user jurisdiction: SG vs IN). |
| **TBAC** | Time-Based Access Control | Access permissions restricted by time windows or session token TTL (Time-To-Live). |
| **HITL** | Human-in-the-Loop | Requiring a qualified human supervisor to verify and approve high-risk AI decisions before execution. |
| **Four-Eyes** | Four-Eyes Principle (Dual Control) | Mandate requiring at least two authorized individuals to review and approve a high-value or sensitive financial action. |
| **PDPA** | Personal Data Protection Act (Singapore) | Singapore's statutory data privacy law safeguarding personal data and national IDs (NRIC). |
| **DPDP** | Digital Personal Data Protection Act 2023 (India) | India's primary digital privacy statute governing the processing of personal data (PAN/Aadhaar). |
| **FEAT** | Fairness, Ethics, Accountability, and Transparency | MAS's core principles for responsible AI and data analytics in the financial sector. |
| **SOC 2** | System and Organization Controls 2 | An international cybersecurity auditing standard verifying that cloud services securely manage customer data. |
| **NRIC / FIN** | National Registration Identity Card / Foreign Identification Number | Singapore's unique citizen/permanent resident and foreigner identity numbers. |
| **PAN** | Permanent Account Number | India's 10-character alphanumeric tax identifier required for financial transactions. |
| **Aadhaar** | Aadhaar (Unique Identification) | India's 12-digit biometric citizen identification number. |
| **PaC** | Policy-as-Code | Writing regulatory compliance rules as executable programming code rather than static manual text policies. |

---

## 🏛️ Section 1: Regulatory Authorities & Statutes

### 1. MAS (Monetary Authority of Singapore)
- **Who They Are:** Singapore's central bank and supreme financial regulator.
- **Why It Matters to Our Project:** MAS is globally renowned for setting the strictest fintech, AI, and technology risk benchmarks in Asia.
- **Specific Regulations Used in AegisGov AI:**
  - **MAS Notice 644 (Technology Risk Management):** Requires financial institutions to maintain strict access controls, data confidentiality, system resilience, and dual authorization for payment processing.
  - **MAS FEAT Principles (Fairness, Ethics, Accountability, Transparency):** Mandates that any AI used in banking must be explainable, non-discriminatory, and accountable. Our **Fiduciary Suitability Check** scenario enforces FEAT by preventing advisors from pitching high-risk speculative crypto to conservative clients.
  - **MAS Shared Responsibility Framework (SRF):** Holds banks liable for scam losses if they fail to implement real-time phishing and mule account detection. Our **Cross-Rail Scam & Mule Ring Bypass** scenario uses this to isolate smurfing rings in the Medallion Quarantine tier.

### 2. RBI (Reserve Bank of India)
- **Who They Are:** India's central banking institution regulating digital payments and commercial banks.
- **Why It Matters to Our Project:** India has the world's highest volume of real-time digital transactions (UPI). RBI mandates strict digital lending guardrails and data sovereignty.
- **Specific Regulations Used in AegisGov AI:**
  - **RBI Digital Lending Guidelines (2022/2023):** Dictates that all loan disbursals and repayments must execute directly between the borrower's bank account and the regulated bank, without third-party pass-throughs. Crucially, automated AI lending systems must have explicit human oversight for loan increases.
  - **RBI Master Direction on IT Governance & Cybersecurity:** Mandates role-based privilege controls, segregation of duties, and audit trail retention.

### 3. Singapore PDPA vs. India DPDP Act 2023 (Data Privacy)
- **Singapore PDPA (Personal Data Protection Act):** Regulates the collection, use, and disclosure of personal data. Under PDPA guidelines, organizations are strictly prohibited from collecting or displaying unmasked **NRIC numbers** except where required by law.
- **India DPDP Act 2023 (Digital Personal Data Protection Act):** Imposes stringent penalties (up to ₹250 Crore per incident) on data fiduciaries for unauthorized processing or leakage of personal data like **PAN and Aadhaar**.
- **How AegisGov AI Complies:** In Stage 2 (Ingress) and Stage 5 (Egress), our **PII Vault Tokenizer** automatically detects NRIC and PAN strings and replaces them with cryptographic surrogate tokens (e.g. `TOK_SG_NRIC_9921`). The LLM never sees or stores real citizen identity documents.

### 4. SOC 2 Type II & AICPA Trust Services Criteria (TSC)
- **What It Is:** An independent auditing standard created by the American Institute of Certified Public Accountants (AICPA).
- **The 5 Trust Principles:** Security, Availability, Processing Integrity, Confidentiality, and Privacy.
- **Controls Used in AegisGov AI:**
  - **CC6.1 (Logical Access):** Verifies that only authorized personas can perform financial operations (mapped to Stage 1 PoLP).
  - **PI1.1 (Processing Integrity):** Guarantees that financial transactions are complete, valid, accurate, and authorized (mapped to Stage 3 Circuit Breakers).
  - **C1.1 (Confidentiality):** Ensures customer PII is protected from unauthorized disclosure (mapped to Stage 2 & 5 Tokenization).
  - **CC7.2 (Threat Monitoring):** Continuous anomaly and prompt injection detection (mapped to Threat Radar).

---

## 🔒 Section 2: Cybersecurity & Access Control Concepts

### 1. PoLP (Principle of Least Privilege)
- **The Concept:** A foundational cybersecurity paradigm dictating that a user, program, or AI agent should be granted only the minimum levels of access or permissions necessary to perform their specific job—and nothing more.
- **In Our Code:** 
  - `Rachel Lim` is a **Junior Analyst**. Under PoLP, she has permissions to `view_gold_metrics` and `query_financial_sentinel_basic`. She is explicitly denied `initiate_payment_order`.
  - When Rachel asks to disburse a commercial loan or lease payout, Stage 1 immediately rejects the request with a `DENIED_ACCESS` event. The prompt never touches the LLM.

### 2. The Triple-Access Control Model: RBAC, ABAC, and TBAC
AegisGov AI evaluates three distinct access dimensions simultaneously:
1. **RBAC (Role-Based Access Control):** Permissions linked to organizational role (`JUNIOR_ANALYST`, `WEALTH_ADVISOR`, `COMPLIANCE_OFFICER`, `RISK_OFFICER`).
2. **ABAC (Attribute-Based Access Control):** Permissions linked to contextual attributes:
   - *Jurisdiction:* An advisor in the **India Hub (IN)** cannot authorize payments in the **Singapore Hub (SG)** without cross-border clearance.
   - *Security Clearance:* Four tiers (`INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`, `SECRET`).
3. **TBAC (Time-Based Access Control):** Permissions bounded by session token lifespan (Time-To-Live / TTL). Once the session token expires (1800s), all operations are blocked until re-authenticated.

### 3. Four-Eyes Principle (Dual Authorization)
- **The Concept:** Originating in physical bank vaults requiring two separate keys held by two different officers to open a safe. In software, it means a high-value or high-risk transaction initiated by Person A cannot execute until Person B (a qualified reviewer) independently approves it.
- **In Our Code:** 
  - `Vikram Mehta` (Senior Wealth Advisor) initiates a lease payment of **S$ 75,000**.
  - Since this exceeds his single-operator discretionary limit of **S$ 10,000**, Stage 3 halts execution and generates a **HITL Ticket**.
  - `Sarah Chen` (Compliance Officer) reviews the transaction in the HITL Approval Center. Once approved, the transaction is marked as `DUAL_AUTHORIZED_SETTLED`.

### 4. Circuit Breaker
- **The Concept:** Borrowed from electrical engineering and financial trading exchanges. When a financial threshold or safety parameter is tripped, the circuit opens to prevent catastrophic damage (e.g. capital flight or flash crashes).
- **In Our Code:** A deterministic code gate in [circuit_breaker.py](file:///Users/shanusingh/Google_AI_Builder_Cup_2026/backend/app/harness/circuit_breaker.py) that inspects the extracted transaction amount:
  - If $\text{amount} > \text{S}\$ 10,000$ or $\text{amount} > \text{₹} 5,00,000$, it trips the circuit and escalates to HITL.

### 5. Ingress vs. Egress Guards
- **Ingress Guard (Input Gate):** Sanitizes and inspects data coming **IN** from the user before the LLM processes it. Checks for prompt injections, system overrides, and tokenizes PII.
- **Egress Guard (Output Gate):** Sanitizes and inspects data going **OUT** from the LLM back to the user. Ensures the model did not leak backend passwords, internal API keys, or raw customer IDs.

### 6. Salted HMAC SHA-256 Chained Ledger
- **The Concept:** A cryptographic technique that creates an immutable, tamper-evident audit trail (similar to a private blockchain).
- **How It Works:** Every log entry contains the cryptographic hash of the *previous* log entry plus a secret server salt. If anyone alters or deletes a previous row in the database, the hash chain breaks immediately, alerting auditors to tampering.

---

## 💳 Section 3: Financial Payment Rails & Crime Terms

### 1. FAST (Fast And Secure Transfers)
- **What It Is:** Singapore’s electronic funds transfer service that enables customers of participating banks to transfer Singapore Dollar funds almost instantly (under 15 seconds) 24/7/365.
- **In Our Code:** Used as the primary settlement rail for Singapore transactions (e.g. S$ 75,000 commercial lease deposit to Sentosa Commercial Realty Hub).

### 2. UPI (Unified Payments Interface)
- **What It Is:** Developed by the National Payments Corporation of India (NPCI) and regulated by RBI. It is an instant real-time payment system facilitating inter-bank peer-to-peer (P2P) and person-to-merchant (P2M) transactions.
- **In Our Code:** Used as the primary settlement rail for India transactions (e.g. ₹ 5,00,000 supplier payments).

### 3. Money Mule Accounts & Mule Rings
- **What It Is:** A "mule" is a person who transfers illegally acquired money on behalf of criminals, often tricked by work-from-home scams or selling their bank account credentials. A "mule ring" is a coordinated network of hundreds of such accounts used by fraud syndicates.
- **Smurfing:** The practice of breaking a large illicit sum of money into dozens of small transactions (e.g. S$ 950 each) to stay just below statutory reporting thresholds ($1,000).
- **In Our Code:** The **Cross-Rail Scam & Mule Ring Bypass** scenario simulates a syndicate attempting to launder funds across FAST and UPI. AegisGov AI's Ingress Guard and Lakehouse engine detect the pattern, flag the accounts, and shunt the transactions into the **Quarantine Vault**.

---

## 📊 Section 4: Data Architecture & AI Terminology

### 1. Medallion Lakehouse Architecture
A data design pattern that organizes data into progressive refinement tiers:
1. **Bronze Tier (Raw Ingestion):** Unprocessed, raw transaction events streaming in from payment rails (FAST/UPI). Contains raw timestamps and sender/recipient payloads.
2. **Silver Tier (Cleansed & Masked):** Validated data where PII has been masked (`S****921A`) or replaced with vault tokens. Cleaned of anomalies.
3. **Gold Tier (Certified Business Aggregates):** Curated, highly aggregated financial metrics (Total Certified Volume, Currency Conversions, Compliance Health Score). This is the **only** tier that the Aegis Financial Sentinel queries to answer financial questions.
4. **Quarantine Tier (Security Vault):** An isolated holding area for transactions flagged as malicious, high-risk fraud, or schema contract violations. Quarantined records are barred from advancing to Silver or Gold.

### 2. Policy-as-Code (PaC) & Data Contracts
- **The Concept:** Traditional compliance relies on 100-page policy manuals written in legal English that developers must manually interpret. **Policy-as-Code** uses an AI compiler (Gemini Pro in [policy_compiler.py](file:///Users/shanusingh/Google_AI_Builder_Cup_2026/backend/app/agents/policy_compiler.py)) to parse statutory text (e.g. MAS Notice 644) and generate machine-executable JSON schemas called **Data Contracts**.
- **Data Contract:** A formal agreement specifying what columns are required, their data types, nullability rules, and specific PII masking algorithms (e.g. `MASK_MIDDLE` or `VAULT_TOKENIZE`). The data pipeline refuses to promote any record that violates the contract.

### 3. Grounding (Eliminating Hallucinations)
- **The Concept:** Grounding means anchoring an AI model's response to verified, authoritative external data rather than relying on its internal statistical weights.
- **In Our Code:** When a user asks: *"What is our total certified transaction volume today?"*, Gemini is not allowed to guess. The system queries DuckDB/BigQuery Gold tier (`SELECT sum(amount_sgd) FROM gold...`), obtains the exact certified float, and feeds it to Gemini as ground truth.

---

## 🪪 Section 5: National Identity Documents

| Identifier | Country | Format / Pattern | Why It Is Strictly Protected | Masking Applied in AegisGov AI |
| :--- | :--- | :--- | :--- | :--- |
| **NRIC** (National Registration Identity Card) | Singapore | 9 characters: 1 letter + 7 digits + 1 letter (e.g. `S1234567A`) | The primary national identifier used for government services, banking, medical records, and taxation in Singapore. Compromising it leads to identity theft and SIM-swap fraud. | Masked as `S****567A` or tokenized as `TOK_SG_NRIC_...` |
| **FIN** (Foreign Identification Number) | Singapore | 9 characters: Starts with F, G, or M (e.g. `G1234567B`) | Issued to foreigners residing or working in Singapore. Same statutory protection as NRIC under PDPA. | Masked as `G****567B` |
| **PAN** (Permanent Account Number) | India | 10 characters: 5 letters + 4 digits + 1 letter (e.g. `ABCDE1234F`) | Primary tax identifier required by the Income Tax Department and RBI for all banking, investments, and loan applications in India. | Masked as `ABCD****4F` or tokenized as `TOK_IN_PAN_...` |
| **Aadhaar** | India | 12 digits (e.g. `1234 5678 9012`) | India's biometric national ID. Under Supreme Court rulings and UIDAI regulations, storing or displaying unmasked 12-digit Aadhaar numbers is a punishable criminal offense. | Masked to show only last 4 digits: `****-****-9012` |

---

## 🎯 Summary: How to Articulate This to Judges

If a judge asks:
> *"What regulatory framework does your solution actually solve for?"*

**You can reply:**
> *"AegisGov AI targets the strict regulatory intersection of **MAS Notice 644 / FEAT Principles in Singapore** and the **RBI Digital Lending / DPDP Act in India**. Specifically, we enforce the statutory **Four-Eyes Principle** using deterministic **Circuit Breakers** on payments over S$ 10k, prevent **national PII leakage (NRIC/PAN)** via zero-trust vault tokenization, and halt **mule scam rings** before they enter the certified **Medallion Gold Lakehouse**."*
