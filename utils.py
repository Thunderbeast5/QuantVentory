"""
utils.py — QUBO Conversion Utilities
=====================================
Based on handwritten notes:
  - Binary encoding: xi = Σ(k=0 to K) 2^k * b_ik
  - H_RM = Σ_j ( Σ_i Aij * (Σ_k 2^k * b_ik) - yj )^2
  - H_D  = Σ_i ( Σ_k 2^k * b_ik - di )^2
  - H_inv= Σ_i ( Σ_k 2^k * b_ik + si - di )^2
  - Final Hamiltonian: H = -Z + λ1*H_RM + λ2*H_D + λ3*H_inv
  where Z = Σ_i pi * xi  (revenue)
        Cost = Σ_j cj * (Σ_i Aij * xi)
"""

import numpy as np
from itertools import product


def binary_encode_variable(i, num_bits, prefix="x"):
    """
    Encode integer xi using binary variables b_ik.
    xi = Σ(k=0..K-1) 2^k * b_ik
    Returns list of (coefficient, variable_name) pairs.
    """
    terms = []
    for k in range(num_bits):
        coeff = 2 ** k
        var_name = f"{prefix}{i}_b{k}"
        terms.append((coeff, var_name))
    return terms


def get_all_binary_vars(num_products, num_bits):
    """Return ordered list of all binary variable names."""
    vars_list = []
    for i in range(num_products):
        for k in range(num_bits):
            vars_list.append(f"x{i}_b{k}")
    return vars_list


def build_qubo_matrix(num_products, num_bits, demands, prices, inventory,
                      raw_material_avail, A_matrix, raw_material_costs,
                      lambda1, lambda2, lambda3):
    """
    Build QUBO dictionary Q where the objective is:
      H = -Revenue + λ1*H_RM + λ2*H_D + λ3*H_inv

    From notes (Page 3):
      H_RM  = Σ_j ( Σ_i Aij*(Σ_k 2^k*b_ik) - yj )^2
      H_D   = Σ_i ( Σ_k 2^k*b_ik - di )^2
      H_inv = Σ_i ( Σ_k 2^k*b_ik + si - di )^2

    Revenue (from Page 2): Z = Σ_i pi*(Σ_k 2^k*b_ik)

    Returns:
      Q: dict of {(var_i, var_j): coefficient}  — upper-triangular QUBO
      var_names: ordered list of variable names
    """
    var_names = get_all_binary_vars(num_products, num_bits)
    n_vars = len(var_names)
    var_idx = {name: idx for idx, name in enumerate(var_names)}

    # Initialize QUBO as dense matrix, convert to dict at end
    Q = np.zeros((n_vars, n_vars))

    def add_qubo_term(vi, vj, coeff):
        """Add coefficient to Q[i,j] with upper-triangular convention."""
        i, j = var_idx[vi], var_idx[vj]
        if i <= j:
            Q[i, j] += coeff
        else:
            Q[j, i] += coeff

    # ------------------------------------------------------------------ #
    # 1. Revenue term: -Z = -Σ_i pi * Σ_k 2^k * b_ik
    #    This is linear, so only diagonal terms in QUBO
    # ------------------------------------------------------------------ #
    for i in range(num_products):
        for k in range(num_bits):
            var = f"x{i}_b{k}"
            coeff = -prices[i] * (2 ** k)
            add_qubo_term(var, var, coeff)

    # ------------------------------------------------------------------ #
    # 2. Raw Material Penalty: λ1 * H_RM
    #    H_RM = Σ_j ( Σ_i Aij * xi - yj )^2
    #    Expand: ( Σ_i Aij * Σ_k 2^k*b_ik - yj )^2
    #    Let L_j = Σ_i Σ_k Aij*2^k*b_ik  (linear part)
    #    (L_j - yj)^2 = L_j^2 - 2*yj*L_j + yj^2
    #    yj^2 is constant (ignored in QUBO), expand L_j^2 and -2yj*L_j
    # ------------------------------------------------------------------ #
    num_materials = len(raw_material_avail)
    for j in range(num_materials):
        # Collect all terms in L_j: list of (coeff, var_name)
        Lj_terms = []
        for i in range(num_products):
            for k in range(num_bits):
                c = A_matrix[i][j] * (2 ** k)
                Lj_terms.append((c, f"x{i}_b{k}"))

        # L_j^2 — quadratic cross terms
        for (c1, v1), (c2, v2) in product(Lj_terms, repeat=2):
            add_qubo_term(v1, v2, lambda1 * c1 * c2)

        # -2*yj*L_j — linear terms (use diagonal)
        yj = raw_material_avail[j]
        for (c, v) in Lj_terms:
            add_qubo_term(v, v, lambda1 * (-2.0) * yj * c)

    # ------------------------------------------------------------------ #
    # 3. Demand Penalty: λ2 * H_D
    #    H_D = Σ_i ( Σ_k 2^k*b_ik - di )^2
    #    Let Xi = Σ_k 2^k*b_ik
    #    (Xi - di)^2 = Xi^2 - 2*di*Xi + di^2
    # ------------------------------------------------------------------ #
    for i in range(num_products):
        di = demands[i]
        xi_terms = [(2 ** k, f"x{i}_b{k}") for k in range(num_bits)]

        # Xi^2
        for (c1, v1), (c2, v2) in product(xi_terms, repeat=2):
            add_qubo_term(v1, v2, lambda2 * c1 * c2)

        # -2*di*Xi
        for (c, v) in xi_terms:
            add_qubo_term(v, v, lambda2 * (-2.0) * di * c)

    # ------------------------------------------------------------------ #
    # 4. Inventory Penalty: λ3 * H_inv
    #    H_inv = Σ_i ( Σ_k 2^k*b_ik + si - di )^2
    #    Let Yi = Xi + si - di  (offset constant = si - di)
    #    (Xi + offset_i)^2 = Xi^2 + 2*offset_i*Xi + offset_i^2
    # ------------------------------------------------------------------ #
    for i in range(num_products):
        si = inventory[i]
        di = demands[i]
        offset = si - di  # constant offset from notes: xi + si - di = 0 for satisfaction

        xi_terms = [(2 ** k, f"x{i}_b{k}") for k in range(num_bits)]

        # Xi^2
        for (c1, v1), (c2, v2) in product(xi_terms, repeat=2):
            add_qubo_term(v1, v2, lambda3 * c1 * c2)

        # 2*offset*Xi
        for (c, v) in xi_terms:
            add_qubo_term(v, v, lambda3 * 2.0 * offset * c)

    # Convert matrix to dict, drop zeros
    Q_dict = {}
    for i in range(n_vars):
        for j in range(i, n_vars):
            if abs(Q[i, j]) > 1e-10:
                Q_dict[(var_names[i], var_names[j])] = Q[i, j]

    return Q_dict, var_names


def decode_binary_solution(bitstring, num_products, num_bits):
    """
    Decode binary solution back to integer xi values.
    xi = Σ_k 2^k * b_ik
    bitstring: list/array of 0/1 in order [b_00, b_01, ..., b_10, b_11, ...]
    """
    x_values = []
    for i in range(num_products):
        xi = 0
        for k in range(num_bits):
            idx = i * num_bits + k
            xi += (2 ** k) * int(bitstring[idx])
        x_values.append(xi)
    return x_values


def compute_profit(x_values, demands, prices, inventory,
                   raw_material_avail, A_matrix, raw_material_costs):
    """
    From Page 2 notes:
      Revenue = Σ_i pi * xi
      Cost    = Σ_j cj * (Σ_i Aij * xi)
      Profit  = Revenue - Cost
    """
    revenue = sum(prices[i] * x_values[i] for i in range(len(prices)))
    cost = 0
    for j in range(len(raw_material_avail)):
        total_rm_j = sum(A_matrix[i][j] * x_values[i] for i in range(len(x_values)))
        cost += raw_material_costs[j] * total_rm_j
    profit = revenue - cost
    return revenue, cost, profit


def check_constraints(x_values, demands, inventory, raw_material_avail, A_matrix):
    """
    Check all three constraints from Page 2:
      1. Demand: xi <= di
      2. Inventory: xi + si >= di
      3. Raw material: Σ_i Aij*xi <= yj
    Returns dict of violations.
    """
    violations = {}

    # Demand constraint: xi <= di
    for i, (xi, di) in enumerate(zip(x_values, demands)):
        if xi > di:
            violations[f"Demand P{i+1}"] = f"x{i+1}={xi} > d{i+1}={di}"

    # Inventory constraint: xi + si >= di
    for i, (xi, si, di) in enumerate(zip(x_values, inventory, demands)):
        if xi + si < di:
            violations[f"Inventory P{i+1}"] = f"x{i+1}+s{i+1}={xi+si} < d{i+1}={di}"

    # Raw material constraint
    for j, yj in enumerate(raw_material_avail):
        used = sum(A_matrix[i][j] * x_values[i] for i in range(len(x_values)))
        if used > yj:
            violations[f"RawMat M{j+1}"] = f"used={used:.1f} > avail={yj}"

    return violations


def classical_solve(demands, prices, inventory, raw_material_avail, A_matrix, raw_material_costs):
    """
    Classical brute-force solver for comparison.
    Enumerate all feasible integer solutions (xi from 0 to di).
    Returns best x_values, profit, and all feasible solutions.
    """
    n = len(demands)
    best_profit = -np.inf
    best_x = None
    feasible_count = 0

    # Generate all combinations
    ranges = [range(0, int(demands[i]) + 1) for i in range(n)]
    for combo in product(*ranges):
        x = list(combo)

        # Check constraints
        valid = True
        # Demand
        for i in range(n):
            if x[i] > demands[i]:
                valid = False; break
        if not valid:
            continue
        # Inventory
        for i in range(n):
            if x[i] + inventory[i] < demands[i]:
                valid = False; break
        if not valid:
            continue
        # Raw material
        for j in range(len(raw_material_avail)):
            used = sum(A_matrix[i][j] * x[i] for i in range(n))
            if used > raw_material_avail[j]:
                valid = False; break

        if valid:
            feasible_count += 1
            _, _, profit = compute_profit(
                x, demands, prices, inventory,
                raw_material_avail, A_matrix, raw_material_costs
            )
            if profit > best_profit:
                best_profit = profit
                best_x = x[:]

    return best_x, best_profit, feasible_count