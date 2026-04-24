#!/usr/bin/env python3
"""
Quick verification script to test all imports and basic functionality.
Run this to ensure all dependencies are correctly installed.
"""

import sys

print("🔍 Checking Quantventory Project Dependencies...\n")

# Test each import with clear feedback
checks = [
    ("numpy", "Core numerical computing"),
    ("pandas", "Data handling"),
    ("matplotlib", "Visualization"),
    ("streamlit", "UI framework"),
    ("qiskit", "Quantum circuits"),
    ("qiskit_optimization", "Optimization module"),
    ("qiskit_aer", "Simulator backend"),
    ("qiskit_algorithms", "QAOA & eigensolvers"),
]

failed = []
for package, description in checks:
    try:
        __import__(package)
        print(f"  ✅ {package:<25} — {description}")
    except ImportError as e:
        print(f"  ❌ {package:<25} — {description}")
        failed.append(package)

print("\n" + "="*60)

# Test local imports
print("\n🔍 Checking local module imports...\n")

try:
    from utils import build_qubo_matrix, decode_binary_solution, compute_profit, check_constraints
    print("  ✅ utils.py           — QUBO building & constraint checking")
except ImportError as e:
    print(f"  ❌ utils.py — {e}")
    failed.append("utils")

try:
    from quantum_solver import solve_with_qaoa, get_qaoa_circuit_text
    print("  ✅ quantum_solver.py   — QAOA solver functions")
except ImportError as e:
    print(f"  ❌ quantum_solver.py — {e}")
    failed.append("quantum_solver")

print("\n" + "="*60)

if failed:
    print(f"\n⚠️  FAILED: {len(failed)} package(s) missing: {', '.join(failed)}")
    print("\n📦 Install with:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
else:
    print("\n✅ All checks passed!")
    print("\n🚀 Ready to run:")
    print("   streamlit run app.py")
    sys.exit(0)
