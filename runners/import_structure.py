import asyncio
import os.path
from pathlib import Path
import aiofile
from pydantic import BaseModel
from engine import Metas, RunnerBase, RunnerContext

from python_sdk import CleanedMolecule, Workspace


class RunnerConfig(BaseModel):
    directory: str
    selects: list[str]


class ImportStructure(BaseModel):
    structure: CleanedMolecule
    class_name: str


class Runner(RunnerBase):
    def __init__(self, metas: Metas, options: RunnerConfig) -> None:
        super().__init__(metas, options)
        self.options = options
        self.imported_structures: list[ImportStructure] = []

    async def init_resources(self) -> None:
        directory = Path(self.options.directory)
        selects = [
            item for select in self.options.selects for item in directory.glob(f"{select}.json")]
        files = await asyncio.gather(*[aiofile.async_open(select) for select in selects])
        files = await asyncio.gather(*[file.read() for file in files])
        structures = [ImportStructure.model_validate_json(
            data) for data in files]
        self.imported_structures = structures

    def cache(self) -> int:
        directory = Path(self.options.directory)
        selects = [
            item for select in self.options.selects for item in directory.glob(select)]
        targets = [(item, os.path.getmtime(item)) for item in selects]
        return hash(targets)

    async def execute(self, workspace: Workspace, context: RunnerContext) -> RunnerContext:
        start = context.start + len(context.tags)
        imported_tags: list[dict[str, str]] = []
        for i, tags in enumerate(context.tags):
            stack_idx = context.start + i
            start, _ = await workspace.clone_stack(stack_idx, len(self.imported_structures))
            for i, to_import in enumerate(self.imported_structures):
                await workspace.import_structure(start + i, to_import.structure, to_import.class_name)
                imported_tags.append(tags | {
                    self.__metas__.name: to_import.class_name
                })
        return RunnerContext(start=start, tags=imported_tags)
