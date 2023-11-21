from python_sdk import config, Workspace

config["prefix"] = "http://localhost:18010"

try:
    ws = Workspace.create("example")
    print(ws)
    print(ws.clone_stack(0))
    print(ws.get_stacks())
    print(ws.remove())
except:
    ws.remove()