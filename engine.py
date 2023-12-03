from abc import ABC, abstractclassmethod, abstractproperty
import json
import os
import os.path
import pathlib
from typing import TypedDict

from python_sdk import Workspace

LME_CACHE_DIR = pathlib.Path.home() if os.environ["LME_CACHE_DIR"] is None else os.environ["LME_CACHE_DIR"]

class RunnerContext(TypedDict):
    start: int
    tags: list[dict[str, str]]

class RunnerMetas(TypedDict):
    name: str

class RunnerBase:
    def __init__(self, metas: RunnerMetas) -> None:
        self.__metas__ = metas

    async def init_resources(self) -> None:
        return None

    def cache(self) -> int:
        raise NotImplementedError

    async def init_resources(self) -> None:
        pass

    async def execute(self, workspace: Workspace, context: RunnerContext) -> RunnerContext:
        raise NotImplementedError
    
class Engine:
    def __init__(self, server: str, ws: str, runners: list[RunnerBase]) -> None:
        self.__workspace__ = Workspace(server, ws)
        self.__runners__ = runners
        self.__cached__ = list(map(lambda r: str(r.cache), runners))
        self.__cache_status__ = None
        self.__current_ctx__: RunnerContext = {
            "start": 0, "tags": [[]]
        }
        while len(self.__cached__) > 0:
            cache_full_path = os.path.join(LME_CACHE_DIR, *self.__cached__, "data")
            if os.path.exists(cache_full_path):
                f = open(cache_full_path)
                self.__cache_status__ = json.loads("\n".join(f.readlines()))
                f.close()
                break
            else:
                self.__cached__.pop()

    async def init_resources(self):
        await self.__workspace__.create(self.__cache_status__)

    async def one_step(self):
        if len(self.__cached__) == len(self.__runners__):
            return False
        runner = self.__runners__[len(self.__cached__)]
        self.__current_ctx__ = await runner.execute(self.__workspace__, self.__current_ctx__)
        self.__cache_status__ = await self.__workspace__.export()
        self.__cached__.append(str(runner.cache))
        os.mkdir(os.path.join(LME_CACHE_DIR, *self.__cached__))
        f = open(os.path.join(LME_CACHE_DIR, *self.__cached__, "data"), mode="w")
        f.write(json.dumps(self.__cache_status__))
        f.close()
        return True
    
    async def clear_resources(self):
        await self.__workspace__.close()