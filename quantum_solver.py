"""
quantum_solver.py — Qiskit QAOA Solver
========================================
Implements QAOA-based optimization for inventory planning.

Flow (from notes Page 3):
  QUBO → QUBO matrix → Quantum System → Answer
  Using IBM Qiskit gate-based model

Steps:
  1. Receive QUBO dict from utils.py
  2. Build QuadraticProgram
  3. Convert to Ising Hamiltonian
  4. Run QAOA via MinimumEigenOptimizer
  5. Decode and return result
"""

import numpy as np
import warnings
warnings.filterwarnings("ignore")


def solve_with_qaoa(Q_dict, var_names, num_products, num_bits,
                    demands, prices, inventory, raw_material_avail,
                    A_matrix, raw_material_costs, reps=1):
    """
    Main QAOA solver.

    Args:
        Q_dict: QUBO dict {(var_i, var_j): coeff}
        var_names: ordered list of binary variable names
        reps: QAOA circuit repetitions (p parameter)

    Returns:
        result dict with x_values, bitstring, circuit, etc.
    """
    try:
        from qiskit_optimization import QuadraticProgram
        from qiskit_optimization.algorithms import MinimumEigenOptimizer
        from qiskit_algorithms import QAOA, NumPyMinimumEigensolver
        from qiskit_algorithms.optimizers import COBYLA
        from qiskit_aer.primitives import Sampler
        from qiskit_optimization.converters import QuadraticProgramToQubo

    except ImportError as e:
        return {"error": f"Missing package: {e}. Run: pip install qiskit qiskit-optimization qiskit-aer qiskit-algorithms"}

    # ------------------------------------------------------------------ #
    # Step 1: Build QuadraticProgram from QUBO
    # ------------------------------------------------------------------ #
    qp = QuadraticProgram(name="InventoryOptimization")

    # Add binary variables
    for v in var_names:
        qp.binary_var(name=v)

    # Build linear and quadratic terms from Q_dict
    linear = {}
    quadratic = {}

    for (vi, vj), coeff in Q_dict.items():
        if vi == vj:
            # Diagonal → linear (since b^2 = b for binary)
            linear[vi] = linear.get(vi, 0.0) + coeff
        else:
            quadratic[(vi, vj)] = quadratic.get((vi, vj), 0.0) + coeff

    qp.minimize(linear=linear, quadratic=quadratic)

    # ------------------------------------------------------------------ #
    # Step 2: Convert to QUBO form (already is, but verify)
    # ------------------------------------------------------------------ #
    converter = QuadraticProgramToQubo()
    qubo = converter.convert(qp)

    # ------------------------------------------------------------------ #
    # Step 3: Get number of qubits
    # ------------------------------------------------------------------ #
    n_qubits = len(var_names)

    # ------------------------------------------------------------------ #
    # Step 4a: Classical reference — NumPy exact solver
    # ------------------------------------------------------------------ #
    numpy_solver = NumPyMinimumEigensolver()
    numpy_optimizer = MinimumEigenOptimizer(numpy_solver)
    numpy_result = numpy_optimizer.solve(qubo)
    numpy_bitstring = [int(b) for b in numpy_result.x]

    # ------------------------------------------------------------------ #
    # Step 4b: QAOA solver with Aer simulator
    # ------------------------------------------------------------------ #
    sampler = Sampler()
    optimizer = COBYLA(maxiter=200)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=reps)
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)
    qaoa_result = qaoa_optimizer.solve(qubo)
    qaoa_bitstring = [int(b) for b in qaoa_result.x]

    # ------------------------------------------------------------------ #
    # Step 5: Get QAOA circuit for visualization
    # ------------------------------------------------------------------ #
    from qiskit_algorithms import QAOA as QAOACircuit
    from qiskit.primitives import StatevectorSampler

    # Build circuit using initial parameters for display
    init_params = np.ones(2 * reps) * 0.5
    qaoa_circuit_obj = qaoa.ansatz.decompose()

    # ------------------------------------------------------------------ #
    # Step 6: Decode binary → integer x values
    # ------------------------------------------------------------------ #
    from utils import decode_binary_solution, compute_profit, check_constraints

    x_qaoa = decode_binary_solution(qaoa_bitstring, num_products, num_bits)
    x_numpy = decode_binary_solution(numpy_bitstring, num_products, num_bits)

    rev_q, cost_q, profit_q = compute_profit(
        x_qaoa, demands, prices, inventory,
        raw_material_avail, A_matrix, raw_material_costs
    )
    rev_n, cost_n, profit_n = compute_profit(
        x_numpy, demands, prices, inventory,
        raw_material_avail, A_matrix, raw_material_costs
    )

    violations_qaoa = check_constraints(x_qaoa, demands, inventory, raw_material_avail, A_matrix)
    violations_numpy = check_constraints(x_numpy, demands, inventory, raw_material_avail, A_matrix)

    return {
        "success": True,
        "n_qubits": n_qubits,
        "reps": reps,
        "qaoa": {
            "x_values": x_qaoa,
            "bitstring": qaoa_bitstring,
            "bitstring_str": "".join(str(b) for b in qaoa_bitstring),
            "objective": float(qaoa_result.fval),
            "revenue": rev_q,
            "cost": cost_q,
            "profit": profit_q,
            "violations": violations_qaoa,
        },
        "classical_quantum": {
            "x_values": x_numpy,
            "bitstring": numpy_bitstring,
            "bitstring_str": "".join(str(b) for b in numpy_bitstring),
            "objective": float(numpy_result.fval),
            "revenue": rev_n,
            "cost": cost_n,
            "profit": profit_n,
            "violations": violations_numpy,
        },
        "circuit": qaoa_circuit_obj,
        "qubo": qubo,
    }


def get_qaoa_circuit_text(n_qubits, reps):
    """
    Generate a text representation of the QAOA circuit structure.
    Used when full circuit drawing is not available.
    """
    lines = [f"QAOA Circuit (n={n_qubits} qubits, p={reps} layers)"]
    lines.append("=" * 50)
    lines.append("Layer 0 (Initial State):")
    lines.append(f"  H ⊗{n_qubits}  — Hadamard on all {n_qubits} qubits")
    for r in range(reps):
        lines.append(f"Layer {r+1} (QAOA Round {r+1}):")
        lines.append(f"  Problem unitary U(C, γ_{r+1}): ZZ rotations")
        lines.append(f"  Mixer unitary U(B, β_{r+1}): RX rotations")
    lines.append("Measurement: all {n_qubits} qubits → classical bits")
    return "\n".join(lines)