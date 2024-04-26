from abc import ABC, abstractmethod


class ComposeCompiler(ABC):
    @abstractmethod
    def write(self) -> None:
        pass


class CompileExcel(ComposeCompiler):
    def write(self) -> None:
        pass


