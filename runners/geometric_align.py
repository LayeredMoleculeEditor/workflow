from typing import TypedDict
from engine import RunnerBase, RunnerContext
from python_sdk import Atoms, Workspace
import numpy as np
from scipy.spatial.transform import Rotation
import asyncio

class GeometricAlign(TypedDict):
    target: tuple[float, float, float]
    atoms: tuple[str | int, str | int]

class Runner(RunnerBase):
    def __init__(self, options: GeometricAlign) -> None:
        super().__init__(None)
        self.__options__ = options

    def cache(self) -> int:
        return hash(self.__options__)

    async def __generate_rotation_layer__(atoms: Atoms, start: int, end: int, target: tuple[float, float, float]):
        start = np.array(atoms[start]['position'])
        end = np.array(atoms[end]['position'])
        current = end - start
        target = np.array(target)
        axis = np.cross(current, target)
        angle = np.arccos(np.dot(target, current) / (np.linalg.norm(target) * np.linalg.norm(current)))
        matrix = Rotation.from_rotvec(angle * axis).as_matrix()
        return ({
            "Rotation": {
                "matrix": matrix,
                "center": tuple(start)
            }
        }, {
            "Translate": {
                "vector": tuple(start)
            }
        })

    async def execute(self, workspace: Workspace, context: RunnerContext) -> RunnerContext:
        start, end = self.__options__['atoms']
        start = start if type(start) == int else await workspace.get_atom_by_id(context['start'], start)
        end = end if type(end) == int else await workspace.get_atom_by_id(context['start'], end)
        stack_ids = [
            stack_id for stack_id in range(context['start'], context['start'] + len(context['tags']))
        ]
        stack_atoms = await asyncio.gather(*[workspace.get_stack(stack_id) for stack_id in stack_ids])
        transform_layers = await asyncio.gather(*[Runner.__generate_rotation_layer__(atoms, start, end, self.__options__["target"]) for atoms in stack_atoms])
        rotations, translates = zip(*transform_layers)
        await asyncio.gather(*[workspace.overlay_layer([stack_id], layer) for (stack_id, layer) in zip(stack_ids, rotations)])
        await asyncio.gather(*[workspace.overlay_layer([stack_id], layer) for (stack_id, layer) in zip(stack_ids, translates)])
        return context
