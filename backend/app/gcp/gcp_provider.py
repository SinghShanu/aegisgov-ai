import os
import time
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from ..config import settings

class GCPServiceDetail(BaseModel):
    service_name: str
    category: str
    problem_addressed: str
    gcp_product: str
    architecture_role: str
    operational_mode: str  # "Local Emulator" or "GCP Cloud Native"
    status: str
    icon_name: str
    regulatory_relevance: str

class GCPArchitectureOverview(BaseModel):
    project_id: str
    region: str
    gcp_mode: str
    base_currency: str
    services: List[GCPServiceDetail]
    timestamp: str

class GCPProvider:
    """
    Manages Google Cloud Platform service abstractions and provides
    dual-mode execution (Local Emulated vs Cloud Native) for hackathon demo.
    """
    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID or "aegisgov-ai-2026"
        self.region = settings.GCP_LOCATION
        self.gcp_mode = settings.GCP_MODE  # "local" or "cloud"

    def get_service_matrix(self) -> List[GCPServiceDetail]:
        is_cloud = self.gcp_mode == "cloud"
        mode_label = "GCP Cloud Native" if is_cloud else "Local Emulated Mode"

        return [
            GCPServiceDetail(
                service_name="Vertex AI & Agent Development Kit (ADK)",
                category="Agentic AI & Reasoning",
                problem_addressed="Autonomous financial copilot reasoning, policy compilation, and continuous compliance auditing without hallucinations.",
                gcp_product="Vertex AI (Gemini 2.0 Flash / Pro) + Reasoning Engine",
                architecture_role="Powers Tri-Agent framework + SOC 2 Auditor with System Instructions and Grounding.",
                operational_mode=mode_label,
                status="OPERATIONAL",
                icon_name="Brain",
                regulatory_relevance="MAS FEAT Principles (Explainability & Fairness) & RBI Digital Lending AI Guidelines."
            ),
            GCPServiceDetail(
                service_name="Cloud Sensitive Data Protection (DLP)",
                category="Data Privacy & Pseudonymization",
                problem_addressed="Detecting, tokenizing, and preventing exfiltration of Singapore NRIC/FIN and India PAN / Aadhaar.",
                gcp_product="Sensitive Data Protection (Cloud DLP)",
                architecture_role="Intercepts raw payment payloads and replaces national identifiers with cryptographic vault tokens before lakehouse persistence.",
                operational_mode=mode_label,
                status="OPERATIONAL",
                icon_name="ShieldCheck",
                regulatory_relevance="Singapore PDPA 2024 & India Digital Personal Data Protection (DPDP) Act 2023."
            ),
            GCPServiceDetail(
                service_name="Cloud Pub/Sub",
                category="Streaming Ingestion",
                problem_addressed="High-throughput asynchronous decoupling of live transaction bursts across FAST, UPI, and SWIFT payment rails.",
                gcp_product="Google Cloud Pub/Sub",
                architecture_role="Ingests raw rail topics (`japac-rail-transactions`, `high-risk-alerts`) with dead-letter queue routing for anomalies.",
                operational_mode=mode_label,
                status="OPERATIONAL",
                icon_name="Activity",
                regulatory_relevance="MAS TRM Section 6 (Continuous Availability & Resilient Message Ingestion)."
            ),
            GCPServiceDetail(
                service_name="BigQuery & BigLake",
                category="Medallion Data Lakehouse",
                problem_addressed="Zero-trust progression of transactional data across Bronze (Raw) -> Silver (Masked) -> Gold (Certified) tiers with quarantine isolation.",
                gcp_product="Google BigQuery + Storage API",
                architecture_role="Houses partitioned and clustered lakehouse datasets, certified materialized marts, and quarantine dead-letter tables.",
                operational_mode=mode_label,
                status="OPERATIONAL",
                icon_name="Database",
                regulatory_relevance="SOC 2 Processing Integrity (PI1.1) & RBI Data Localization mandate."
            ),
            GCPServiceDetail(
                service_name="Google Cloud Run",
                category="Serverless Container Hosting",
                problem_addressed="Zero-maintenance, autoscale-to-zero container execution in Singapore region with strict instance quotas to protect Free Tier credits.",
                gcp_product="Google Cloud Run (asia-southeast1)",
                architecture_role="Runs unified FastAPI and React Vite production image with HTTPS and health probes.",
                operational_mode="Cloud Ready (Containerized)",
                status="OPERATIONAL",
                icon_name="Server",
                regulatory_relevance="Singapore low-latency residency & regional financial disaster recovery compliance."
            ),
            GCPServiceDetail(
                service_name="Secret Manager & Cloud KMS",
                category="Key Management & Cryptography",
                problem_addressed="Zero hardcoded secrets, rotation of Gemini API keys, and hardware-backed HMAC keys for tamper-evident ledger sealing.",
                gcp_product="Cloud Secret Manager & Cloud KMS",
                architecture_role="Protects audit ledger cryptographic signing keys and AI model endpoint credentials.",
                operational_mode=mode_label,
                status="OPERATIONAL",
                icon_name="Key",
                regulatory_relevance="SOC 2 CC6.1 (Logical Access & Cryptographic Key Management) & MAS Notice 644."
            ),
            GCPServiceDetail(
                service_name="Cloud Armor & Identity-Aware Proxy (IAP)",
                category="Zero-Trust Perimeter Security",
                problem_addressed="DDoS protection, rate limiting, and zero-trust user authentication before requests touch internal banking APIs.",
                gcp_product="Google Cloud Armor + IAP",
                architecture_role="Filters incoming IP ranges, enforces WAF rules, and restricts access to authenticated bank officers.",
                operational_mode=mode_label,
                status="CONFIGURED",
                icon_name="Lock",
                regulatory_relevance="MAS TRM Section 5 (Perimeter Defense & Network Segmentation)."
            )
        ]

    def get_overview(self) -> GCPArchitectureOverview:
        return GCPArchitectureOverview(
            project_id=self.project_id,
            region=self.region,
            gcp_mode=self.gcp_mode,
            base_currency=settings.BASE_CURRENCY,
            services=self.get_service_matrix(),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        )

gcp_provider = GCPProvider()
