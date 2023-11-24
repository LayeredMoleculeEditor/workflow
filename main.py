from python_sdk import AddSubstitute, Workspace

async def main():
    ws = Workspace("http://localhost:18010", "example")
    try:
        await ws.create()
        await ws.get_stacks()
        await ws.clone_stack(0)
        await ws.get_stack(1)
        await ws.is_stack_writable(1)
        await ws.overlay_fill_layer(1)
        await ws.is_stack_writable(1)
        await ws.write_to_layer(1, {
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
        })
        await ws.overlay_fill_layer(1)
        add_substituent: AddSubstitute = {
            "atoms": [
                {
                    "element": 1,
                    "position": [0., 0., 0.]
                },
                {
                    "element": 6,
                    "position": [0., 1., 0.]
                },
                {
                    "element": 5,
                    "position": [0., 2., 0.]
                }
            ],
            "bonds_idxs": [
                (0,1), (1,2)
            ],
            "bonds_values": [
                1.0, 3.0
            ],
            "class_name": "CN",
            "current": (0, 1),
            "target": (0, 1),
        }
        await ws.add_substitute(1, add_substituent)
        print(await ws.cleaned_molecule(1))
    finally:
        # pass
        print(f"Remove created Workspaces: {await ws.remove()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())