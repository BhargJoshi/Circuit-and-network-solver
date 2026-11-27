# Where is Linear Algebra used here and why does it work?

A circuit is represented as a graph. Its junctions are nodes and its electrical parts are branches. Kirchhoff's Current Law says that the algebraic sum of currents at a node is zero. For a resistor, Ohm's Law gives I = (Vp - Vn) / R. These relationships are linear in the unknown node voltages and voltage-source branch currents.

Putting all node-balance equations and voltage-source constraints together gives A x = b. Gaussian elimination changes the equations through valid row operations without changing their solution set. Partial pivoting chooses a large available pivot to reduce numerical instability. Rank(A) compared with rank([A|b]) classifies the system: unequal ranks mean no solution; equal ranks with rank equal to the number of unknowns mean one solution; equal smaller ranks mean infinitely many solutions.

The null space contains changes to the unknown vector that leave A x unchanged. A non-trivial null space therefore signals free directions in a dependent system. The determinant of the square coefficient matrix is zero when the matrix is singular, which is a warning that the equations do not determine every unknown.

The application uses an adjacency list to store which nodes are connected by each component. SQLite stores the circuit input, status, ranks and computed result so that saved work remains available after the app is restarted.
