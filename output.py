from graphviz import Digraph

# Create diagram
dot = Digraph(comment="Simplified AI DM Flow", format="png")

# Nodes
dot.node("A", "Player Action Request", shape="box", style="filled", fillcolor="#f4cccc")
dot.node("B", "Rules Agent (RAG)\n- Finds relevant D&D rules", shape="box", style="filled", fillcolor="#cfe2f3")
dot.node("C", "Campaign Memory Agent (RAG)\n- Continuity + Progress tracking", shape="box", style="filled", fillcolor="#d9ead3")
dot.node("D", "Decision / Narration Agent\n- Combines rules + memory + player request", shape="box", style="filled", fillcolor="#fff2cc")
dot.node("E", "Log Agent\n- Summarizes events into quest log + structured data", shape="box", style="filled", fillcolor="#ead1dc")
dot.node("F", "Vector DBs / Structured Storage\n(Rules DB, Campaign DB)", shape="cylinder", style="filled", fillcolor="#d0e0e3")

# Edges
dot.edge("A", "B")
dot.edge("A", "C")
dot.edge("B", "D")
dot.edge("C", "D")
dot.edge("D", "E")
dot.edge("E", "C", label="Update campaign state")
dot.edge("B", "F", label="Rules reference")
dot.edge("C", "F", label="Campaign reference")

# Render diagram to file
output_path = 'simplified_ai_dm_flow.png'
dot.render(output_path, cleanup=True)

output_path
