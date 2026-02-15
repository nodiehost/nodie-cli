"""
Nodie CLI - Turn your terminal into a network node and earn rewards.
"""

__version__ = "1.0.1"
__author__ = "Nodie Team"
__email__ = "support@nodie.host"

from nodie_cli.client import NodieClient
from nodie_cli.node import NodieNode

__all__ = ["NodieClient", "NodieNode", "__version__"]
