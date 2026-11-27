import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from math_engine.solver import solve_circuit, parse_netlist
from db.database import init_db, save_result, list_saved

st.set_page_config(page_title="Circuit & Network Solver", page_icon="⚡", layout="wide")
init_db()

st.title("Circuit & Network Solver")
st.caption("A minimal nodal-analysis simulator using Kirchhoff’s Current Law, Ohm’s Law and linear algebra.")

DEFAULT = """# Format: Rname,node+,node-,resistance_ohms
#         Vname,node+,node-,voltage_volts
# Node 0 is ground. A voltage source is positive at node+.
R1,n1,0,1000
R2,n1,n2,2000
R3,n2,0,1000
V1,n1,0,10
"""

st.markdown("Enter one component per line. Use node `0` as ground. Resistors and independent DC voltage sources are supported.")
netlist = st.text_area("Circuit components", value=DEFAULT, height=190, help="Examples: R1,n1,0,1000  or  V1,n1,0,5")
left, right = st.columns([1, 4])
with left:
    solve_clicked = st.button("Solve circuit", type="primary", use_container_width=True)
with right:
    st.caption("The solver numbers the nodes automatically, builds the matrix, performs Gaussian elimination with partial pivoting, and classifies the system using rank.")

if solve_clicked:
    try:
        result = solve_circuit(netlist)
        st.session_state["last_result"] = result
        st.session_state["last_netlist"] = netlist
    except Exception as exc:
        st.error(str(exc))

result = st.session_state.get("last_result")
if result:
    st.divider()
    st.subheader("1. Circuit structure")
    st.write("**Node numbering** (node 0 is the reference/ground):")
    st.dataframe([{"Node": k, "Number": v, "Role": "Ground" if k == "0" else "Unknown node voltage"} for k, v in result["node_map"].items()], hide_index=True, use_container_width=True)
    st.write("**Component graph (adjacency list)**")
    st.code("\n".join(f"{n}: {', '.join(neighbours) if neighbours else '(no connected nodes)'}" for n, neighbours in result["adjacency"].items()), language="text")

    st.subheader("2. Equations and matrix form")
    st.caption("Each non-ground node contributes a KCL equation. Each ideal voltage source contributes a voltage constraint; its current is included as an additional unknown (modified nodal analysis).")
    st.write("Unknown vector order:")
    st.code("x = [" + ", ".join(result["unknowns"]) + "]ᵀ", language="text")
    st.write("Node / source equations:")
    for eq in result["equations"]:
        st.latex(eq)
    st.write("Coefficient matrix A")
    st.dataframe(result["A"], use_container_width=True)
    st.write("Right-hand-side vector b")
    st.dataframe({"b": result["b"]}, use_container_width=True)

    st.subheader("3. Linear algebra solution process")
    st.markdown(f"**Rank(A) = {result['rank_A']}**  ·  **Rank([A|b]) = {result['rank_aug']}**  ·  **Unknowns = {len(result['unknowns'])}**")
    if result["status"] == "unique":
        st.success("Unique solution: rank(A) = rank([A|b]) = number of unknowns.")
    elif result["status"] == "infinite":
        st.warning("Infinitely many solutions: the ranks are equal but smaller than the number of unknowns. The circuit contains one or more free variables.")
    else:
        st.error("No solution: rank(A) differs from rank([A|b]); the equations are inconsistent.")
    with st.expander("Show Gaussian elimination steps", expanded=True):
        for step in result["steps"]:
            st.markdown(f"**{step['title']}**")
            st.code(step["matrix"], language="text")
    st.write(f"**Determinant:** {result['determinant_text']}")
    st.caption("For this square MNA system, a zero determinant indicates a singular coefficient matrix. This can occur with floating nodes or dependent constraints.")
    if result["nullspace"]:
        st.write("**Null-space basis** (directions in which the unknown vector can change without changing A·x):")
        for vec in result["nullspace"]:
            st.code(str([round(float(v), 8) for v in vec]))
    else:
        st.write("**Null space:** only the zero vector (trivial null space).")

    st.subheader("4. Circuit results")
    if result["status"] == "unique":
        st.write("**Node voltages**")
        st.dataframe([{"Node": n, "Voltage (V)": round(v, 8)} for n, v in result["voltages"].items()], hide_index=True, use_container_width=True)
        st.write("**Branch currents** (positive direction is component node+ → node−)")
        st.dataframe([{"Component": k, "Current (A)": round(v, 10)} for k, v in result["currents"].items()], hide_index=True, use_container_width=True)
        fig, ax = plt.subplots(figsize=(8, 3.2))
        labels = list(result["currents"].keys())
        values = list(result["currents"].values())
        ax.bar(labels, values)
        ax.axhline(0, linewidth=0.8)
        ax.set_ylabel("Current (A)")
        ax.set_title("Current in each branch")
        ax.grid(axis="y", alpha=0.25)
        st.pyplot(fig, clear_figure=True)
        plt.close(fig)
    else:
        st.info("Node voltages and branch currents are not displayed as single values because this system does not have one unique solution.")

    if st.button("Save circuit and result", use_container_width=False):
        save_result(st.session_state["last_netlist"], result)
        st.success("Circuit and result saved to the SQLite database.")

st.divider()
st.subheader("Saved circuits")
saved = list_saved()
if saved:
    st.dataframe(saved, hide_index=True, use_container_width=True)
else:
    st.caption("No saved circuits yet. Solve a circuit and choose “Save circuit and result”.")

st.caption("Core algorithms are implemented in Python in math_engine/. NumPy is used for matrix display and validation only; the solver does not call numpy.linalg to solve the system.")
