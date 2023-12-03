import asyncio
from typing import TypedDict
from engine import RunnerBase, RunnerContext
from python_sdk import CleanedMolecule, Workspace

class Substitute(CleanedMolecule):
    current: tuple[int, int]

class AddSubstitute(TypedDict):
    substitutes: list[tuple[str, Substitute]]
    to_replace: list[tuple[int, int]]

class Runner(RunnerBase):
    def __init__(self, options: AddSubstitute) -> None:
        super().__init__()
        self.__options__ = options
    
    async def add_substitute(self, workspace: Workspace, group: list[int], to_replace: tuple[int, int]):
        tasks = [
            workspace.add_substitute(stack_idx, substitute | {"target": to_replace}) for ((_, substitute), stack_idx) in zip(self.__options__["substitutes"], group)
        ]
        return await asyncio.gather(*tasks)
    
    def cache(self) -> int:
        return hash(self.__options__)

    async def execute(self, workspace: Workspace, context: RunnerContext) -> RunnerContext:
        sub_amount = len(self.__options__["substitutes"])
        targets = [stack_ids for stack_ids in range(context["start"], context["start"] + len(context["tags"]))]
        targets = await asyncio.gather(*[workspace.clone_stack(stack_idx, sub_amount) for stack_idx in targets])
        await workspace.overlay_fill_layer(sum(targets, []))
        for group in targets:
            for to_replace in self.__options__["to_replace"]:
                await self.add_substitute(workspace, group, to_replace)
        tags = list(map(lambda tags: list(map(lambda _: tags[1], tags[0])), zip(targets, tags)))
        return {
            "start": min(sum(targets, [])), "tags": sum(tags, [])
        }