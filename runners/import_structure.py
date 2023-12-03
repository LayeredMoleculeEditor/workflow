from typing import TypedDict
from python_sdk import CleanedMolecule
from engine import RunnerBase, RunnerMetas

class ImportStructureOption(TypedDict):
    sources: list[str]
    positon: tuple[float, float, float]

class Runner(RunnerBase):
    def __init__(self, metas: RunnerMetas, options: ImportStructureOption) -> None:
        super().__init__(metas)
        self.__options__ = options