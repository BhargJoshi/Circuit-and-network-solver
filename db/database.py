import sqlite3, json, os
DB_PATH = os.path.join(os.path.dirname(__file__), "circuits.db")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS circuits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            netlist TEXT NOT NULL,
            status TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            circuit_id INTEGER NOT NULL,
            node_name TEXT NOT NULL,
            node_number INTEGER NOT NULL,
            FOREIGN KEY(circuit_id) REFERENCES circuits(id)
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            circuit_id INTEGER NOT NULL,
            component_name TEXT NOT NULL,
            component_type TEXT NOT NULL,
            positive_node TEXT NOT NULL,
            negative_node TEXT NOT NULL,
            value REAL NOT NULL,
            FOREIGN KEY(circuit_id) REFERENCES circuits(id)
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            circuit_id INTEGER NOT NULL,
            rank_a INTEGER NOT NULL,
            rank_aug INTEGER NOT NULL,
            result_json TEXT NOT NULL,
            FOREIGN KEY(circuit_id) REFERENCES circuits(id)
        )""")

def save_result(netlist, result):
    summary = {"voltages": result["voltages"], "currents": result["currents"],
               "unknowns": result["unknowns"], "A": result["A"], "b": result["b"]}
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute("INSERT INTO circuits(netlist,status) VALUES(?,?)", (netlist, result["status"]))
        circuit_id = cur.lastrowid
        con.executemany("INSERT INTO nodes(circuit_id,node_name,node_number) VALUES(?,?,?)",
                        [(circuit_id, name, number) for name, number in result["node_map"].items()])
        con.executemany("""INSERT INTO components(circuit_id,component_name,component_type,positive_node,negative_node,value)
                           VALUES(?,?,?,?,?,?)""",
                        [(circuit_id, c["name"], c["kind"], c["p"], c["n"], c["value"]) for c in result["components"]])
        con.execute("INSERT INTO results(circuit_id,rank_a,rank_aug,result_json) VALUES(?,?,?,?)",
                    (circuit_id, result["rank_A"], result["rank_aug"], json.dumps(summary)))

def list_saved():
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute("""SELECT c.id, c.created_at, c.status, r.rank_a, r.rank_aug
                               FROM circuits c LEFT JOIN results r ON r.circuit_id=c.id
                               ORDER BY c.id DESC LIMIT 20""").fetchall()
    return [{"ID": r[0], "Saved at": r[1], "Status": r[2], "Rank(A)": r[3], "Rank([A|b])": r[4]} for r in rows]
