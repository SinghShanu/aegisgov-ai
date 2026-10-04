import duckdb
import time
from typing import Dict, List, Any, Optional
from .contracts import MedallionTier, PIIType, MaskingStrategy, DataContract, ColumnContractRule
from .japac_currency import JAPACCurrencyEngine
from ..harness.pii_vault_tokenizer import pii_vault

class MedallionLakehouse:
    def __init__(self):
        self.con = duckdb.connect(database=":memory:")
        self._init_tables()
        self.quarantine_vault: List[Dict[str, Any]] = []

    def _init_tables(self):
        # Bronze: Raw Ingestion
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS bronze_transactions (
                transaction_id VARCHAR,
                timestamp VARCHAR,
                sender_id VARCHAR,
                sender_name VARCHAR,
                sender_id_doc VARCHAR,
                sender_account VARCHAR,
                recipient_id VARCHAR,
                recipient_name VARCHAR,
                recipient_account VARCHAR,
                amount DOUBLE,
                currency VARCHAR,
                payment_rail VARCHAR,
                purpose VARCHAR,
                ingested_at DOUBLE
            )
        """)

        # Silver: Cleansed & Masked
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS silver_transactions (
                transaction_id VARCHAR,
                timestamp VARCHAR,
                sender_id VARCHAR,
                sender_name VARCHAR,
                sender_id_doc_masked VARCHAR,
                sender_account_masked VARCHAR,
                recipient_id VARCHAR,
                recipient_name VARCHAR,
                recipient_account_masked VARCHAR,
                amount DOUBLE,
                currency VARCHAR,
                amount_sgd DOUBLE,
                amount_inr DOUBLE,
                payment_rail VARCHAR,
                purpose VARCHAR,
                processed_at DOUBLE
            )
        """)

    def ingest_bronze(self, raw_records: List[Dict[str, Any]]) -> int:
        ts = time.time()
        for r in raw_records:
            self.con.execute("""
                INSERT INTO bronze_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                r.get("transaction_id", f"TX-{int(time.time()*1000)}"),
                r.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                r.get("sender_id", "SND-001"),
                r.get("sender_name", "Anonymous"),
                r.get("sender_id_doc", "UNKNOWN"),
                r.get("sender_account", "ACC-0000"),
                r.get("recipient_id", "REC-001"),
                r.get("recipient_name", "Vendor"),
                r.get("recipient_account", "ACC-9999"),
                float(r.get("amount", 0.0)),
                r.get("currency", "SGD").upper(),
                r.get("payment_rail", "FAST"),
                r.get("purpose", "Transfer"),
                ts
            ])
        return len(raw_records)

    def run_medallion_processing(self, contract: Optional[DataContract] = None) -> Dict[str, Any]:
        """
        Processes Bronze into Silver (applying PII tokenization/masking and schema contracts)
        and flags defective records into Quarantine.
        """
        # Clear existing silver
        self.con.execute("DELETE FROM silver_transactions")
        self.quarantine_vault.clear()

        # Fetch all Bronze
        bronze_rows = self.con.execute("""
            SELECT transaction_id, timestamp, sender_id, sender_name, sender_id_doc, 
                   sender_account, recipient_id, recipient_name, recipient_account, 
                   amount, currency, payment_rail, purpose
            FROM bronze_transactions
        """).fetchall()

        promoted_count = 0
        quarantined_count = 0
        now = time.time()

        for row in bronze_rows:
            (tx_id, timestamp, s_id, s_name, s_doc, s_acc, r_id, r_name, r_acc, amt, curr, rail, purp) = row

            # Validation 1: Negative or zero amount
            if amt <= 0.0:
                self.quarantine_vault.append({
                    "transaction_id": tx_id,
                    "reason": f"Negative or zero amount ({amt} {curr}). Invalid under RBI/MAS transaction contracts.",
                    "violating_field": "amount",
                    "payload": dict(zip(["tx_id", "amt", "curr", "rail"], [tx_id, amt, curr, rail]))
                })
                quarantined_count += 1
                continue

            # Validation 2: Currency Support
            if curr not in ["SGD", "INR", "JPY", "AUD", "USD"]:
                self.quarantine_vault.append({
                    "transaction_id": tx_id,
                    "reason": f"Unsupported JAPAC currency '{curr}'. Ingestion contract rejected.",
                    "violating_field": "currency",
                    "payload": dict(zip(["tx_id", "amt", "curr", "rail"], [tx_id, amt, curr, rail]))
                })
                quarantined_count += 1
                continue

            # Masking: Apply Tokenization / Middle Masking on JAPAC PII
            # For Singapore NRIC or Indian PAN / Aadhaar
            pii_type = PIIType.SG_NRIC if curr in ["SGD", "USD", "AUD"] else PIIType.IN_PAN
            masked_doc = pii_vault.mask_string(s_doc, MaskingStrategy.MASK_MIDDLE, pii_type)
            masked_s_acc = pii_vault.mask_string(s_acc, MaskingStrategy.MASK_MIDDLE, PIIType.BANK_ACCOUNT)
            masked_r_acc = pii_vault.mask_string(r_acc, MaskingStrategy.MASK_MIDDLE, PIIType.BANK_ACCOUNT)

            amt_sgd = JAPACCurrencyEngine.to_sgd(amt, curr)
            amt_inr = JAPACCurrencyEngine.to_inr(amt_sgd)

            self.con.execute("""
                INSERT INTO silver_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                tx_id, timestamp, s_id, s_name, masked_doc, masked_s_acc,
                r_id, r_name, masked_r_acc, amt, curr, amt_sgd, amt_inr, rail, purp, now
            ])
            promoted_count += 1

        return {
            "bronze_total": len(bronze_rows),
            "silver_promoted": promoted_count,
            "quarantined": quarantined_count,
            "status": "COMPLETED"
        }

    def process_stream_transaction(self, r: Dict[str, Any]) -> Dict[str, Any]:
        """
        Incrementally ingests a single streaming transaction into Bronze and 
        applies immediate schema, currency, amount, and safety contract checks.
        Promotes to Silver if valid, otherwise routes to Quarantine.
        """
        now = time.time()
        tx_id = r.get("transaction_id", f"TX-{int(now*1000)}")
        ts_str = r.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)))
        s_id = r.get("sender_id", "SND-STREAM")
        s_name = r.get("sender_name", "Anonymous")
        s_doc = r.get("sender_id_doc", "UNKNOWN")
        s_acc = r.get("sender_account", "ACC-0000")
        r_id = r.get("recipient_id", "REC-STREAM")
        r_name = r.get("recipient_name", "Vendor")
        r_acc = r.get("recipient_account", "ACC-9999")
        amt = float(r.get("amount", 0.0))
        curr = str(r.get("currency", "SGD")).upper()
        rail = str(r.get("payment_rail", "FAST")).upper()
        purp = str(r.get("purpose", "Transfer"))

        # 1. Ingest to Bronze
        self.con.execute("""
            INSERT INTO bronze_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            tx_id, ts_str, s_id, s_name, s_doc, s_acc,
            r_id, r_name, r_acc, amt, curr, rail, purp, now
        ])

        # 2. Check for Injected Threat / Malicious payload
        if r.get("is_corrupted", False) or r.get("threat_type"):
            threat_reason = r.get("quarantine_reason", "Corrupted payload detected by JAPAC Ingress Safety Guard.")
            self.quarantine_vault.append({
                "transaction_id": tx_id,
                "reason": threat_reason,
                "violating_field": r.get("violating_field", "security_anomaly"),
                "payload": {"tx_id": tx_id, "amount": amt, "currency": curr, "rail": rail, "purpose": purp, "threat": r.get("threat_type")}
            })
            return {
                "transaction_id": tx_id,
                "status": "QUARANTINED",
                "tier": "QUARANTINE",
                "reason": threat_reason
            }

        # 3. Validation: Amount
        if amt <= 0.0:
            reason = f"Negative or zero amount ({amt} {curr}). Invalid under RBI/MAS transaction contracts."
            self.quarantine_vault.append({
                "transaction_id": tx_id,
                "reason": reason,
                "violating_field": "amount",
                "payload": {"tx_id": tx_id, "amount": amt, "currency": curr, "rail": rail}
            })
            return {
                "transaction_id": tx_id,
                "status": "QUARANTINED",
                "tier": "QUARANTINE",
                "reason": reason
            }

        # 4. Validation: Supported Currency
        if curr not in ["SGD", "INR", "JPY", "AUD", "USD"]:
            reason = f"Unsupported JAPAC currency '{curr}'. Ingestion contract rejected."
            self.quarantine_vault.append({
                "transaction_id": tx_id,
                "reason": reason,
                "violating_field": "currency",
                "payload": {"tx_id": tx_id, "amount": amt, "currency": curr, "rail": rail}
            })
            return {
                "transaction_id": tx_id,
                "status": "QUARANTINED",
                "tier": "QUARANTINE",
                "reason": reason
            }

        # 5. Masking and Currency Normalization
        pii_type = PIIType.SG_NRIC if curr in ["SGD", "USD", "AUD"] else PIIType.IN_PAN
        masked_doc = pii_vault.mask_string(s_doc, MaskingStrategy.MASK_MIDDLE, pii_type)
        masked_s_acc = pii_vault.mask_string(s_acc, MaskingStrategy.MASK_MIDDLE, PIIType.BANK_ACCOUNT)
        masked_r_acc = pii_vault.mask_string(r_acc, MaskingStrategy.MASK_MIDDLE, PIIType.BANK_ACCOUNT)

        amt_sgd = JAPACCurrencyEngine.to_sgd(amt, curr)
        amt_inr = JAPACCurrencyEngine.to_inr(amt_sgd)

        # 6. Insert to Silver
        self.con.execute("""
            INSERT INTO silver_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            tx_id, ts_str, s_id, s_name, masked_doc, masked_s_acc,
            r_id, r_name, masked_r_acc, amt, curr, amt_sgd, amt_inr, rail, purp, now
        ])

        return {
            "transaction_id": tx_id,
            "status": "PROMOTED_TO_SILVER",
            "tier": "SILVER",
            "amount_sgd": amt_sgd,
            "amount_inr": amt_inr
        }

    def _query_dicts(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        cur = self.con.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def get_tier_data(self, tier: str, limit: int = 50) -> List[Dict[str, Any]]:
        tier_upper = tier.upper()
        if tier_upper == "BRONZE":
            return self._query_dicts(f"SELECT * FROM bronze_transactions LIMIT {limit}")
        elif tier_upper == "SILVER":
            return self._query_dicts(f"SELECT * FROM silver_transactions LIMIT {limit}")
        elif tier_upper == "QUARANTINE":
            return self.quarantine_vault[:limit]
        return []

    def get_gold_analytics(self) -> Dict[str, Any]:
        """Gold Tier: Certified aggregations & compliance health metrics"""
        row = self.con.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                COALESCE(SUM(amount_sgd), 0.0) as total_volume_sgd,
                COALESCE(SUM(amount_inr), 0.0) as total_volume_inr,
                COALESCE(AVG(amount_sgd), 0.0) as avg_transaction_sgd
            FROM silver_transactions
        """).fetchone()

        rails = self._query_dicts("""
            SELECT payment_rail, COUNT(*) as count, SUM(amount_sgd) as rail_volume_sgd
            FROM silver_transactions
            GROUP BY payment_rail
        """)

        currencies = self._query_dicts("""
            SELECT currency, COUNT(*) as count, SUM(amount) as total_native
            FROM silver_transactions
            GROUP BY currency
        """)

        total_tx = row[0]
        quarantine_tx = len(self.quarantine_vault)
        total_ingested = total_tx + quarantine_tx
        compliance_health = (total_tx / total_ingested * 100.0) if total_ingested > 0 else 100.0

        return {
            "total_certified_transactions": total_tx,
            "total_volume_sgd": round(row[1], 2),
            "total_volume_inr": round(row[2], 2),
            "avg_transaction_sgd": round(row[3], 2),
            "compliance_health_score": round(compliance_health, 1),
            "quarantine_count": quarantine_tx,
            "payment_rails_breakdown": rails,
            "currency_distribution": currencies,
            "certified_status": "MAS_FEAT_AND_RBI_CERTIFIED"
        }

    def get_lineage_graph(self) -> Dict[str, Any]:
        """Returns structured lineage nodes and edges for the React Flow diagram"""
        nodes = [
            {"id": "source_streams", "type": "input", "label": "JAPAC Payment Streams (FAST / PayNow / UPI)", "tier": "SOURCE"},
            {"id": "bronze_lake", "label": "Bronze Tier (Raw Lakehouse)", "tier": "BRONZE", "records": self.con.execute("SELECT count(*) FROM bronze_transactions").fetchone()[0]},
            {"id": "policy_contract", "label": "Active Data Contracts (MAS / RBI / DPDP)", "tier": "CONTRACT"},
            {"id": "silver_curated", "label": "Silver Tier (PII-Masked & Curated)", "tier": "SILVER", "records": self.con.execute("SELECT count(*) FROM silver_transactions").fetchone()[0]},
            {"id": "quarantine_vault", "label": "Quarantine Vault (Contract Violations)", "tier": "QUARANTINE", "records": len(self.quarantine_vault)},
            {"id": "gold_certified", "label": "Gold Tier (Certified AI-Ready)", "tier": "GOLD"},
            {"id": "ai_copilot", "label": "Enterprise Financial AI Copilot", "tier": "CONSUMER"}
        ]
        edges = [
            {"source": "source_streams", "target": "bronze_lake", "label": "Ingestion"},
            {"source": "bronze_lake", "target": "silver_curated", "label": "Schema & PII Guardrails"},
            {"source": "policy_contract", "target": "silver_curated", "label": "Enforces Contracts"},
            {"source": "bronze_lake", "target": "quarantine_vault", "label": "Rejected Payloads"},
            {"source": "silver_curated", "target": "gold_certified", "label": "Certified Aggregation"},
            {"source": "gold_certified", "target": "ai_copilot", "label": "Safe Grounded Retrieval"}
        ]
        return {"nodes": nodes, "edges": edges}

medallion_lakehouse = MedallionLakehouse()
