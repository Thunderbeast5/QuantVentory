# 📁 Project Structure Guide

## Quantventory Directory Layout

```
Quantventory/
│
├── 📄 README.md                    # Main documentation (Quick start)
├── 📋 requirements.txt              # Python dependencies (pip install)
├── 🔑 .gitignore                    # Git ignore patterns
├── 🚀 setup.sh                      # Quick setup script (bash)
├── 🚀 launch.py                     # Streamlit launcher (Python)
│
├── 📂 src/                          # Source code
│   ├── __init__.py                  # Package initialization
│   ├── app.py                       # Streamlit UI (main entry point)
│   ├── quantum_solver.py            # QAOA solver (Qiskit)
│   └── utils.py                     # QUBO conversion & classical solver
│
├── 📂 docs/                         # Documentation
│   ├── README_GUIDE.md              # Detailed user guide
│   └── (other docs go here)
│
├── 📂 tests/                        # Testing & verification
│   ├── __init__.py                  # Test package
│   └── test_setup.py                # Dependency verification
│
└── 📂 venv/                         # Virtual environment (ignored in git)
    └── (Python packages)
```

---

## File Purposes

### Root Files
| File | Purpose |
|------|---------|
| `README.md` | Quick start guide |
| `requirements.txt` | All Python dependencies |
| `.gitignore` | Git ignore patterns |
| `setup.sh` | Automated setup script |
| `launch.py` | Python launcher for the app |

### `src/` - Source Code (Main Logic)
| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Streamlit UI, inputs, outputs | ~700 |
| `quantum_solver.py` | QAOA solver via Qiskit | ~150 |
| `utils.py` | QUBO building & classical solver | ~250 |

### `docs/` - Documentation
| File | Purpose |
|------|---------|
| `README_GUIDE.md` | Comprehensive usage guide |
| (future) | Additional docs, formulas, images |

### `tests/` - Testing
| File | Purpose |
|------|---------|
| `test_setup.py` | Verify all dependencies are installed |
| (future) | Unit tests, integration tests |

---

## How to Run

### Option 1: Python Launcher (Recommended)
```bash
python launch.py
```

### Option 2: Direct Streamlit
```bash
streamlit run src/app.py
```

### Option 3: Using Setup Script First
```bash
bash setup.sh
streamlit run src/app.py
```

---

## Development Workflow

### Add New Features
1. Edit files in `src/` directory
2. Test with `streamlit run src/app.py`
3. Commit and push

### Add Tests
1. Create test files in `tests/`
2. Run: `python -m pytest tests/`

### Add Documentation
1. Create `.md` files in `docs/`
2. Link from main README.md

---

## Version Control (Git)

The `.gitignore` automatically excludes:
- ✓ Virtual environment (`venv/`)
- ✓ Python cache (`__pycache__/`, `*.pyc`)
- ✓ IDE files (`.vscode/`, `.idea/`)
- ✓ OS files (`.DS_Store`, `Thumbs.db`)
- ✓ Logs and temp files
- ✓ Streamlit cache

### Basic Git Commands
```bash
# Check status
git status

# Add all changes
git add .

# Commit
git commit -m "Your message"

# Push to remote
git push origin main
```

---

## Package Structure Benefits

✅ **Organized** - Clear separation of concerns
✅ **Scalable** - Easy to add new modules
✅ **Testable** - Tests separated from source
✅ **Documented** - Documentation in dedicated folder
✅ **Professional** - Industry-standard layout
✅ **Git-friendly** - Proper `.gitignore` handling

---

## Next Steps

1. ✅ Verify dependencies: `python tests/test_setup.py`
2. ✅ Run the app: `python launch.py`
3. ✅ Read detailed guide: `docs/README_GUIDE.md`
4. 📝 Contribute: Make changes in `src/` and commit to git
5. 🧪 Add tests: Create files in `tests/`
6. 📚 Expand docs: Add files to `docs/`

---

**Last Updated:** April 24, 2026
