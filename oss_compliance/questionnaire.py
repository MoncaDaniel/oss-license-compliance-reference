"""Interactive business-context questionnaire (Anomaly #2).

License risk is not a property of the license alone -- GPL in an internal
tool and GPL in a distributed product carry very different obligations.
This questionnaire captures the context needed to make that distinction
instead of producing a generic, context-free score.
"""

from .models import ProductContext

_USE_CASES = ["Internal", "Embedded", "SaaS", "Distributed"]
_DATA_TYPE_OPTIONS = [
    "No sensitive data",
    "Customer data (GDPR-protected)",
    "Industrial/operational data",
    "Both customer and operational",
]


class ProductQuestionnaire:
    """Interactive Q&A to build a ProductContext."""

    def __init__(self, input_fn=input, print_fn=print):
        self._input = input_fn
        self._print = print_fn

    def ask_user(self) -> ProductContext:
        self._print("--- Product Context Questionnaire ---")

        product_name = self._input("Product name: ").strip()
        use_case = self._ask_use_case()
        data_types = self._ask_data_types()
        target_markets = self._ask_target_markets()
        is_safety_critical = self._ask_yes_no("Is this safety-critical?")
        has_ai = self._ask_yes_no("Does it use AI/ML?")
        modifications_expected = self._ask_yes_no(
            "Do you expect to modify any of these open source components?"
        )

        return ProductContext(
            product_name=product_name,
            use_case=use_case,
            data_types=data_types,
            target_markets=target_markets,
            is_safety_critical=is_safety_critical,
            has_ai=has_ai,
            modifications_expected=modifications_expected,
        )

    def _ask_use_case(self) -> str:
        self._print("\nHow is this software deployed?")
        for i, option in enumerate(_USE_CASES, start=1):
            label = {
                "Internal": "Internal (not distributed)",
                "Embedded": "Embedded (in hardware)",
                "SaaS": "SaaS (cloud-hosted)",
                "Distributed": "Distributed (sold/given to customers)",
            }[option]
            self._print(f"{i}. {label}")
        choice = self._input(f"Select (1-{len(_USE_CASES)}): ").strip()
        return self._select(choice, _USE_CASES, default="Internal")

    def _ask_data_types(self):
        self._print("\nWhat types of data does it handle?")
        for i, option in enumerate(_DATA_TYPE_OPTIONS, start=1):
            self._print(f"{i}. {option}")
        choice = self._input(f"Select (1-{len(_DATA_TYPE_OPTIONS)}): ").strip()
        selected = self._select(choice, _DATA_TYPE_OPTIONS, default="No sensitive data")
        if selected == "Both customer and operational":
            return ["Customer data (GDPR-protected)", "Industrial/operational data"]
        if selected == "No sensitive data":
            return []
        return [selected]

    def _ask_target_markets(self):
        raw = self._input("\nTarget markets? (comma-separated, e.g. EU, US, Asia): ").strip()
        if not raw:
            return []
        return [m.strip() for m in raw.split(",") if m.strip()]

    def _ask_yes_no(self, question: str) -> bool:
        answer = self._input(f"\n{question} (yes/no): ").strip().lower()
        return answer in ("y", "yes")

    @staticmethod
    def _select(choice: str, options, default: str) -> str:
        try:
            index = int(choice) - 1
            if 0 <= index < len(options):
                return options[index]
        except (ValueError, TypeError):
            pass
        return default
