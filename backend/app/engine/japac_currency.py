from typing import Dict

# Exchange rates benchmarked against Base Currency (SGD)
FX_RATES_TO_SGD: Dict[str, float] = {
    "SGD": 1.0,
    "INR": 0.0155,    # 1 INR = ~0.0155 SGD (1 SGD = ~64.5 INR)
    "JPY": 0.0087,    # 1 JPY = ~0.0087 SGD (1 SGD = ~115 JPY)
    "AUD": 0.88,      # 1 AUD = ~0.88 SGD
    "USD": 1.34       # 1 USD = ~1.34 SGD
}

class JAPACCurrencyEngine:
    @staticmethod
    def to_sgd(amount: float, from_currency: str) -> float:
        rate = FX_RATES_TO_SGD.get(from_currency.upper(), 1.0)
        return round(amount * rate, 2)

    @staticmethod
    def to_inr(amount_sgd: float) -> float:
        return round(amount_sgd * 64.516, 2)

    @staticmethod
    def format(amount: float, currency: str) -> str:
        curr = currency.upper()
        if curr == "SGD":
            return f"S$ {amount:,.2f}"
        elif curr == "INR":
            return f"₹ {amount:,.2f}"
        elif curr == "JPY":
            return f"¥ {amount:,.0f}"
        elif curr == "AUD":
            return f"A$ {amount:,.2f}"
        elif curr == "USD":
            return f"${amount:,.2f}"
        return f"{amount:,.2f} {curr}"
