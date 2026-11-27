# Circuit and Network Solver

A small Streamlit web application for DC resistor and independent ideal voltage-source circuits. It follows Project 2 in the Linear Algebra Project Handbook.

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Input format
One component per line:
- `R1,n1,0,1000` = 1 kΩ resistor between node n1 and ground.
- `V1,n1,0,5` = 5 V source, positive at n1 and negative at ground.
- `0` is the reference/ground node.
- Lines beginning with `#` are comments.

## What the application shows
1. Automatically numbered junctions and the circuit adjacency list.
2. Kirchhoff Current Law equations and voltage-source constraints.
3. Coefficient matrix A and right-hand side b.
4. Gaussian elimination with partial pivoting, with each row-operation stage displayed.
5. Rank(A), rank([A|b]), determinant and null-space basis.
6. Unique / infinitely many / no-solution classification.
7. Node voltages, branch currents and a current bar chart when the solution is unique.
8. Saving circuits and results in SQLite (`db/circuits.db`).

## Linear algebra method
The implementation uses modified nodal analysis. Every non-ground node has a KCL equation. Each ideal voltage source adds one branch-current unknown and one voltage constraint. This makes the system square while handling voltage sources without trying to represent an ideal source as a resistance.

The core routines in `math_engine/linear_algebra.py` implement Gaussian elimination with partial pivoting, rank and null-space basis from scratch. NumPy is used in tests to validate the results, not to solve the application's system.

## Required sample demonstrations
`sample_circuits.txt` contains five circuits:
1. Single resistor and voltage source — unique solution.
2. Two-resistor voltage divider — unique solution.
3. Parallel resistor branches — unique solution.
4. Floating isolated branch — dependent equations / infinitely many solutions.
5. Conflicting parallel ideal voltage sources — no solution.

Paste each circuit block separately into the app to demonstrate all required statuses. The app saves a circuit only when the user chooses the save action.

## Tests
```bash
python -m unittest discover -s tests -v
```
Each core algorithm has normal, edge and NumPy comparison tests.

## Project structure
- `math_engine/`: from-scratch linear algebra and circuit solver
- `db/`: SQLite schema and persistence
- `ds/`: adjacency-list graph representation
- `app.py`: single-page interface
- `tests/`: unit tests
- `sample_circuits.txt`: five demonstration circuits
