"""rfp-bid-brief — a bid/no-bid brief generator and the evaluation behind it.

`spans` is the load-bearing module: it turns a fixture into a citable, reproducible span index, and
every claim the pipeline later makes is checked against it (ADR 0001).
"""

__all__ = ["spans"]
__version__ = "0.1.0"
