import os
from typing import TYPE_CHECKING

from amalgamation.cpp_process import FileProcessor

if TYPE_CHECKING:
    from amalgamation.amalgamation import Amalgamation


class HeaderProcessor(FileProcessor):
    def __init__(self, file: str) -> None:
        super().__init__(file)

    def readInclude(self, amalgamation: "Amalgamation"):
        self.findIncludes()
        searchPaths = amalgamation.includeDirectory

        for i in range(len(self.includes)):
            _match = self.includes[i]._match
            relpath = _match.group("path")
            self.includes[i].object = self.searchFile(
                searchPaths,
                relpath,
                [amalgamation.headersDict]  # type: ignore
            )  # type: ignore

        l = []
        for inc in self.includes:
            if inc.object is not None:
                l.append(inc)
                inc.object.refCount += 1
        self.includes = l

    def process(self) -> str:
        if self.data == "":
            return ""
        ans = f"/// {os.path.basename(self.filename)} START\n"
        lastEndIndex = 0
        datacopy = self.data
        self.data = ""
        for inc in self.includes:
            if inc.object is None:
                raise RuntimeError("include object is None")
            ans += datacopy[lastEndIndex:inc._match.start()]
            inctarget = inc.object.process()
            if inctarget != "":
                ans += f"\n{inctarget}\n"
            lastEndIndex = inc._match.end()
        ans += datacopy[lastEndIndex:]
        ans += f"/// {os.path.basename(self.filename)} END\n"
        return ans
