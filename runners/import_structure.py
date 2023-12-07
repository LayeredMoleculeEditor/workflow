import asyncio
import os.path
from pathlib import Path
import aiofile
import numpy as np
from pydantic import BaseModel
from engine import Metas, RunnerBase, RunnerContext

from python_sdk import CleanedMolecule, Workspace


class RunnerConfig(BaseModel):
    directory: str
    selects: list[str]

class ImportStructure(BaseModel):
    structure: CleanedMolecule
    translation: np.array
    rotation: np.array
    class_name: str

class Runner(RunnerBase):
    def __init__(self, metas: Metas, options: RunnerConfig) -> None:
        super().__init__(metas, options)
        self.options = options
        self.imported_structures = []

    async def init_resources(self) -> None:
        directory = Path(self.options.directory)
        selects = [item for select in self.selects for item in directory.glob(select)]
        files = await asyncio.gather(*[aiofile.async_open(select) for select in selects])
        files = await asyncio.gather(*[file.read() for file in files])
        structures = [ImportStructure.model_validate_json(data) for data in files]
        self.imported_structures = structures

    def cache(self) -> int:
        directory = Path(self.options.directory)
        selects = [item for select in self.selects for item in directory.glob(select)]
        targets = [(item, os.path.getmtime(item)) for item in selects]
        return hash(targets)
    
    async def execute(self, workspace: Workspace, context: RunnerContext) -> RunnerContext:
        return await super().execute(workspace, context)