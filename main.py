from python_sdk import AddSubstitute, Workspace
from ase.io.gaussian import read_gaussian_in
from ase import Atom, Atoms

async def main():
    ws = Workspace("http://localhost:18010", "example")
    template = read_gaussian_in(open("./template.gjf"))
    atoms = [{"element": int(atom.number), "position": list(atom.position)} for atom in template]
    try:
        await ws.create()
        await ws.overlay_fill_layer([0])
        await ws.import_structure(0, (atoms, [], []), "base")
        benzene = [{"element": int(atom.number), "position": list(atom.position)} for atom in read_gaussian_in(open("./benzene.gjf"))]
        add_benzene: AddSubstitute = {
            "atoms": benzene,
            "bonds_idxs": [],
            "bonds_values": [],
            "class_name": "left",
            "current": (7, 1),
            "target": (12, 19)
        }
        await ws.clone_stack(0)
        await ws.add_substitute(1, add_benzene)
        [atoms, _, _] = await ws.cleaned_molecule(1)
        atoms = map(lambda atom: Atom(atom["element"], atom["position"]), atoms)
    finally:
        # pass
        print(f"Remove created Workspaces: {await ws.remove()}")
        await ws.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())