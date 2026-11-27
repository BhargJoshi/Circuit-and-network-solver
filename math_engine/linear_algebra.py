from copy import deepcopy

TOL = 1e-10

def gaussian_elimination(A, b, tol=TOL):
    """Solve/row-reduce [A|b] using Gaussian elimination with partial pivoting.
    Returns RREF-like echelon result, pivot columns, determinant, and visible steps.
    """
    m, n = len(A), (len(A[0]) if A else 0)
    M = [list(map(float, A[i])) + [float(b[i])] for i in range(m)]
    steps = [{"title": "Initial augmented matrix [A|b]", "matrix": _fmt(M)}]
    pivot_cols, pivot_rows, det = [], [], 1.0
    sign, row = 1, 0
    for col in range(n):
        if row >= m:
            break
        pivot = max(range(row, m), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) <= tol:
            continue
        if pivot != row:
            M[row], M[pivot] = M[pivot], M[row]
            sign *= -1
            steps.append({"title": f"Swap row {row+1} with row {pivot+1} (partial pivoting)", "matrix": _fmt(M)})
        pv = M[row][col]
        det *= pv
        M[row] = [v / pv for v in M[row]]
        steps.append({"title": f"Divide row {row+1} by pivot {pv:.6g}", "matrix": _fmt(M)})
        for r in range(m):
            if r != row and abs(M[r][col]) > tol:
                factor = M[r][col]
                M[r] = [M[r][j] - factor * M[row][j] for j in range(n+1)]
        steps.append({"title": f"Eliminate column {col+1} using row {row+1}", "matrix": _fmt(M)})
        pivot_cols.append(col)
        pivot_rows.append(row)
        row += 1
    det *= sign
    if m != n or len(pivot_cols) < n:
        det = 0.0
    # Clean numerical noise.
    for i in range(m):
        M[i] = [0.0 if abs(x) < tol else x for x in M[i]]
    steps.append({"title": "Final reduced system", "matrix": _fmt(M)})
    return M, pivot_cols, pivot_rows, det, steps

def _fmt(M):
    if not M:
        return "(empty)"
    return "\n".join("[ " + "  ".join(f"{v: .6g}" for v in row) + " ]" for row in M)

def matrix_rank(A, tol=TOL):
    """Rank by partial-pivot row reduction (no library solver)."""
    if not A:
        return 0
    M = [list(map(float, row)) for row in A]
    m, n = len(M), len(M[0])
    rank, r = 0, 0
    for c in range(n):
        if r == m:
            break
        p = max(range(r, m), key=lambda i: abs(M[i][c]))
        if abs(M[p][c]) <= tol:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        for i in range(r+1, m):
            f = M[i][c] / pv
            for j in range(c, n):
                M[i][j] -= f * M[r][j]
        rank += 1
        r += 1
    return rank

def null_space(A, tol=TOL):
    """Return a basis for null(A), using free variables in RREF."""
    if not A:
        return []
    m, n = len(A), len(A[0])
    M = [list(map(float, row)) for row in A]
    pivots, r = [], 0
    for c in range(n):
        if r == m:
            break
        p = max(range(r, m), key=lambda i: abs(M[i][c]))
        if abs(M[p][c]) <= tol:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [v / pv for v in M[r]]
        for i in range(m):
            if i != r:
                f = M[i][c]
                M[i] = [M[i][j] - f*M[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = [0.0]*n
        v[f] = 1.0
        for i, p in enumerate(pivots):
            v[p] = -M[i][f]
        basis.append(v)
    return basis
