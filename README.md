# ⚛ Quantventory
## Inventory Optimization using Quantum Computing (QAOA + Qiskit + Streamlit)

**A complete quantum-classical hybrid optimization system for inventory planning.**

---

## 📌 Quick Start

### 1️⃣ Installation

```bash
# Navigate to project directory
cd /Users/vedant/Desktop/Quantventory

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Verify Setup (Optional)
```bash
python tests/test_setup.py
```

### 3️⃣ Run the Application

**Option A: Python Launcher (Recommended)**
```bash
python launch.py
```

**Option B: Direct Streamlit**
```bash
streamlit run src/app.py
```

This will open a browser at `http://localhost:8501`

---

## 📁 Project Structure

```
Quantventory/
├── 📄 README.md                    # This file
├── 📋 requirements.txt              # Dependencies
├── 🔑 .gitignore                    # Git ignore patterns ✨ NEW
├── 🚀 setup.sh                      # Setup script
├── 🚀 launch.py                     # App launcher ✨ NEW
├── 🔧 config.py                     # Configuration ✨ NEW
│
├── 📂 src/                          # Source code ✨ REORGANIZED
│   ├── __init__.py                  # Package init
│   ├── app.py                       # Streamlit UI
│   ├── quantum_solver.py            # QAOA solver
│   └── utils.py                     # QUBO & classical
│
├── 📂 docs/                         # Documentation ✨ NEW
│   ├── STRUCTURE.md                 # Project structure guide
│   └── README_GUIDE.md              # Detailed user guide
│
├── 📂 tests/                        # Tests ✨ NEW
│   ├── __init__.py                  # Test package
│   └── test_setup.py                # Dependency check
│
└── 📂 venv/                         # Virtual environment (git-ignored)
```

✨ **NEW:** `.gitignore`, `launch.py`, `config.py`, improved folder structure!

---

## � Documentation

- **[Full User Guide](docs/README_GUIDE.md)** — Detailed walkthrough of all features
- **[Project Structure](docs/STRUCTURE.md)** — Folder organization and development workflow
- **[Mathematical Formulation](#-mathematical-formulation)** — See below

---

## �📐 Mathematical Formulation

### Problem Definition
Maximize profit subject to:
- **Demand Constraint**: `x_i ≤ d_i` (cannot produce more than demand)
- **Inventory Constraint**: `x_i + s_i ≥ d_i` (must satisfy demand with inventory + production)
- **Raw Material Constraint**: `Σ A_ij·x_i ≤ y_j` (cannot exceed material availability)
- **Integer Constraint**: `x_i ∈ Z⁺` (non-negative integers)

### Quantum Formulation

**Binary Encoding:**
```
x_i = Σ(k=0 to K) 2^k · b_ik  where b_ik ∈ {0,1}
```

**Objective Function (QUBO):**
```
H = -Revenue + λ₁·H_RM + λ₂·H_D + λ₃·H_inv

where:
  Revenue = Σ p_i · x_i
  H_RM = Σ_j (Σ_i A_ij·x_i - y_j)²  [Raw material penalty]
  H_D  = Σ_i (x_i - d_i)²             [Demand penalty]
  H_inv = Σ_i (x_i + s_i - d_i)²      [Inventory penalty]
```

---

## 🎮 How to Use the UI

### Left Sidebar
1. **Problem Setup**
   - Select number of products (2-3 recommended)
   - Select number of raw materials (1-2 recommended)
   - Select bits per variable (2-3 recommended)

2. **Product Parameters** (for each product)
   - `d_i`: Demand (units needed)
   - `p_i`: Selling price ($/unit)
   - `s_i`: Available inventory (units)

3. **Raw Material Parameters** (for each material)
   - `y_j`: Total availability (units)
   - `c_j`: Cost per unit ($/unit)

4. **A Matrix**
   - `A[i,j]`: Units of material j needed per unit of product i

5. **Penalty Weights**
   - `λ₁`: Raw material penalty (higher = stricter compliance)
   - `λ₂`: Demand penalty (higher = must meet demand)
   - `λ₃`: Inventory penalty (higher = must use inventory)

6. **QAOA Settings**
   - Select number of QAOA layers (p=1 is faster, p=2 is more accurate)

### Run Optimization
Click **"⚛ Run Optimization"** button

---

## 📊 Output Tabs

### 1. Results Tab
- **Quantum (QAOA)**: Solution from QAOA algorithm
  - Production plan (x_i values)
  - Revenue, Cost, Profit
  - Bitstring representation
  - Constraint violations
  
- **Exact Quantum (NumPy)**: Reference solution from exact eigensolver
  
- **Classical (Brute Force)**: Exhaustive search comparison

- **Comparison Table**: All three methods side-by-side

### 2. Visualizations Tab
- **Demand vs Production**: Bar chart comparing demand with solutions
- **Profit Comparison**: Which method achieved best profit?
- **Cost Breakdown**: Revenue vs raw material costs
- **Supply vs Demand**: Inventory sufficiency check

### 3. QAOA Circuit Tab
- Circuit architecture explanation
- Variational parameters (γ, β)
- Optimizer details (COBYLA)
- Backend info (Qiskit Aer Sampler)

### 4. QUBO Details Tab
- Number of qubits needed
- Non-zero QUBO terms
- Variable names
- Top 20 largest QUBO coefficients

---

## 🔬 Example Walkthrough

**Default Example (2 Products, 2 Materials):**

| Product | Demand | Price | Inventory |
|---------|--------|-------|-----------|
| P1      | 3      | 10    | 1         |
| P2      | 2      | 15    | 0         |

| Material | Available | Cost |
|----------|-----------|------|
| M1       | 10        | 3    |
| M2       | 8         | 2    |

| A[i,j] | M1 | M2 |
|--------|----|----|
| P1     | 2  | 1  |
| P2     | 1  | 3  |

**QAOA vs Classical:**
- Both find optimal production plans
- Visualize which algorithm performs better
- Check if constraints are satisfied

---

## ⚙️ How QAOA Works

1. **Convert MILP → QUBO**
   - Binary encode decision variables
   - Expand penalty terms into quadratic form
   - Create QUBO matrix

2. **Build Quantum Circuit**
   - Initialize with Hadamard gates (superposition)
   - Apply problem Hamiltonian (rotations parameterized by γ)
   - Apply mixer Hamiltonian (RX rotations parameterized by β)
   - Repeat p times

3. **Optimize Parameters**
   - Use COBYLA optimizer
   - Evaluate objective for each parameter set
   - Find parameters that minimize objective

4. **Measure & Decode**
   - Sample bitstring from final quantum state
   - Decode binary → integer production plan

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `qiskit` | 1.1.1 | Gate-based quantum circuits |
| `qiskit-optimization` | 0.6.1 | QuadraticProgram, QUBO converters |
| `qiskit-aer` | 0.14.1 | Quantum simulator backend |
| `qiskit-algorithms` | 0.2.1 | QAOA, eigensolvers |
| `streamlit` | 1.28.1 | Web UI framework |
| `numpy` | 1.24.3 | Numerical computing |
| `pandas` | 2.0.3 | DataFrames |
| `matplotlib` | 3.7.2 | Plotting |
| `scipy` | 1.11.2 | Scientific computing |

---

## 🚨 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'qiskit'"
**Solution:**
```bash
pip install -r requirements.txt
# or manually:
pip install qiskit qiskit-optimization qiskit-aer qiskit-algorithms
```

### Issue: "No feasible solution found"
**Solution:**
- Increase inventory `s_i` values
- Decrease demand `d_i` values
- Increase raw material availability `y_j`
- Reduce penalty weights (λ₁, λ₂, λ₃)

### Issue: QAOA gives worse result than Classical
- This is normal for small problems! QAOA is designed for larger problem sizes
- Try increasing `num_bits` (more complex problem)
- Increase QAOA layers `p` (more accurate but slower)

### Issue: Streamlit app crashes
- Make sure you're in the correct directory
- Check that all `.py` files are in the same folder
- Verify `requirements.txt` dependencies are installed

---

## 🧪 Testing

Run a quick test to verify everything works:

```bash
# Verify all dependencies are installed
python tests/test_setup.py
```

Expected output:
```
✅ All checks passed!

🚀 Ready to run:
   streamlit run src/app.py
```

---

## 🔧 Development & Contribution

### Folder Organization
- **`src/`** — All source code (app, solver, utilities)
- **`docs/`** — Documentation files (guides, formulas)
- **`tests/`** — Test scripts and verification
- **`.gitignore`** — Prevents committing unnecessary files

### Git Workflow
```bash
# Clone (if needed)
git clone <repository-url>
cd Quantventory

# Make changes
nano src/app.py
# or edit other files in src/

# Commit and push
git add .
git commit -m "Your message"
git push origin main
```

### Adding New Code
1. Edit/create files in `src/` directory
2. Test with: `python launch.py`
3. Verify with: `python tests/test_setup.py`
4. Commit with: `git commit -m "message"`

### `.gitignore` Coverage
✅ Virtual environment  
✅ Python cache files  
✅ IDE configuration  
✅ OS files  
✅ Logs and temp files  
✅ Streamlit cache  

---

## 📚 References

- **Qiskit Documentation**: https://qiskit.org/documentation
- **QAOA Paper**: Farhi et al. (2014) "A Quantum Approximate Optimization Algorithm"
- **Streamlit**: https://streamlit.io/

---

## 📝 Project Completeness Checklist

✅ **Backend (Qiskit)**
- [x] QUBO conversion (utils.py)
- [x] Binary encoding (xi = Σ 2^k·b_ik)
- [x] QuadraticProgram creation
- [x] QAOA solver
- [x] NumPy exact eigensolver (reference)
- [x] Classical brute-force solver

✅ **Frontend (Streamlit)**
- [x] White/minimal UI theme
- [x] Input controls (sidebar)
- [x] Product parameters
- [x] Raw material parameters
- [x] A matrix editor
- [x] Penalty weight sliders
- [x] Run button

✅ **Outputs**
- [x] Optimal production plan
- [x] Profit/cost calculations
- [x] Constraint checking
- [x] Visualizations (4 charts)
- [x] Circuit explanation
- [x] QUBO details
- [x] Classical vs Quantum comparison

✅ **Extra Features**
- [x] QAOA vs Classical vs Exact Quantum
- [x] QAOA circuit architecture display
- [x] Configurable QAOA layers
- [x] Bitstring visualization
- [x] Constraint violation reporting

---

## 🎯 Next Steps (Optional Enhancements)

1. Add real Qiskit hardware backend (needs IBM Quantum credentials)
2. Implement other QAOA variants (warm-start, parameter transfer)
3. Add noise models for realistic simulation
4. Implement other optimization algorithms (VQE, COBYLA variants)
5. Export results to CSV/JSON
6. Add multi-objective optimization (Pareto frontier)
7. Deploy on Streamlit Cloud (free hosting)

---

## 📄 License

This project is educational. Feel free to modify and use for learning quantum computing!

---

**Created:** April 2026  
**Framework:** Streamlit + Qiskit  
**Problem Domain:** Inventory Optimization with Quantum QAOA
