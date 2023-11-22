from python_sdk import Workspace

async def main():
    ws = Workspace("http://localhost:18010", "example")
    try:
        await ws.create()
        print(ws)
        print(await ws.get_stacks())
        print(await ws.clone_stack(0))
        print(await ws.get_stack(1))
        print(await ws.is_stack_writable(1))
        print(await ws.overlay_fill_layer(1))
        print(await ws.is_stack_writable(1))
        print(await ws.write_to_layer(1, {
            0: {
                "element": 6, "position": [0.,0.,0.] 
            },
            1: {
                "element": 1, "position": [1., 0., 0.]
            },
            2: {
                "element":15, "position": [0., 0., -1.]
            },
        }, {
            "indexes": [(0, 1), (0, 2)],
            "values": [1, 3]
        }))
        ws.overlay_fill_layer(1)
        print(await ws.write_to_layer(1, {
            1: None,
            2: {
                "element": 5, "position": [0., 0., -1.]
            }
        }, {}))
        print(await ws.get_stack(1))
    finally:
        print(f"Remove created Workspaces: {await ws.remove()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())