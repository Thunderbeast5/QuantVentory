"""
Quantventory - Quantum Computing Inventory Optimization
======================================================

A hybrid quantum-classical optimization system using QAOA + Qiskit.
"""

__version__ = "1.0.0"
__author__ = "Vedant"

from .quantum_solver import solve_with_qaoa, get_qaoa_circuit_text
from .utils import (
    build_qubo_matrix,
    decode_binary_solution,
    compute_profit,
    check_constraints,
    classical_solve
)

__all__ = [
    "solve_with_qaoa",
    "get_qaoa_circuit_text",
    "build_qubo_matrix",
    "decode_binary_solution",
    "compute_profit",
    "check_constraints",
    "classical_solve",
]
