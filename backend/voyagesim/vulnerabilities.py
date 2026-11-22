"""VulnFlags -- toggleable vulnerability flags for VoyageSim."""


class VulnFlags:
    """Singleton holding vulnerability flags. All default to True (vulnerable)."""

    _instance = None

    VULN_NAMES = [
        "idor_booking",
        "idor_invoice",
        "fare_tamper",
        "duplicate_refund",
        "coupon_reuse",
        "privilege_escalation",
        "mass_assignment",
        "skip_payment",
        "negative_quantity",
        "excessive_exposure",
        "missing_rate_limit",
        "zombie_v1_api",
        "undocumented_routes",
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._flags = {name: True for name in cls.VULN_NAMES}
        return cls._instance

    def is_enabled(self, name: str) -> bool:
        return self._flags.get(name, False)

    def fix(self, name: str) -> bool:
        if name not in self._flags:
            return False
        self._flags[name] = False
        return True

    def unfix(self, name: str) -> bool:
        if name not in self._flags:
            return False
        self._flags[name] = True
        return True

    def list_all(self) -> dict:
        return dict(self._flags)

    def reset(self):
        self._flags = {name: True for name in self.VULN_NAMES}
