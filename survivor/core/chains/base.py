"""Chain adapter interface. Every chain (solana.py now, base.py later) implements this,
and paper and live execution both go through it so they share quotes and costs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Quote:
    input_mint: str
    output_mint: str
    in_amount: int            # raw units of the input token
    out_amount: int           # raw units of the output token, after route fees
    price_impact_pct: float
    network_fee_lamports: int  # base + priority fee estimate
    raw: dict                  # the provider's full response, kept for the ledger


@dataclass(frozen=True)
class SwapResult:
    signature: str | None
    confirmed: bool
    in_amount: int
    out_amount: int            # actual amount received, read back from chain
    fee_lamports: int          # actual fee paid, including on failure
    error: str | None = None


class ChainAdapter(ABC):
    name: str

    @abstractmethod
    def wallet_address(self) -> str: ...

    @abstractmethod
    def balances(self) -> dict[str, int]:
        """Raw balances keyed by mint (native token under 'native')."""

    @abstractmethod
    def quote(self, input_mint: str, output_mint: str, in_amount: int, slippage_bps: int) -> Quote: ...

    @abstractmethod
    def simulate(self, quote: Quote) -> tuple[bool, str | None]:
        """Simulate the swap without sending it. Returns (ok, error)."""

    @abstractmethod
    def swap(self, quote: Quote) -> SwapResult: ...
