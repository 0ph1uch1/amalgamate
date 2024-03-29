import os
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypeVar, overload

from amalgamation.patterns import Patterns


if TYPE_CHECKING:
    from amalgamation.amalgamation import Amalgamation

_T = TypeVar("_T", bound="FileProcessor", covariant=True)


class IncludeStruct(object):
    def __init__(self, _match: re.Match) -> None:
        self._match = _match
        self.object: "FileProcessor" = None  # type: ignore


class FileProcessor(object):
    baseDir = ""

    def __init__(self, file: str) -> None:
        self.filename = file
        with open(file, 'r', encoding='utf-8') as f:
            self.data = f.read()
        self.forget()  # initialize these fields
        self.trimspace()
        self.refCount = 0
        self.includes: List[IncludeStruct] = []

    def analyze(self, amalgamation: "Amalgamation"):
        self.removeUseless(amalgamation.removeTwoSlashComments)
        self.readInclude(amalgamation)

    def forget(self):
        self.strLiternalMatches: List[re.Match] = None
        self.threeslashCommentMatches: List[re.Match] = None
        self.twoslashCommentMatches: List[re.Match] = None
        self.quoteCommentMatches: List[re.Match] = None
        self.includeMatches: List[re.Match] = None
        self.pragmaonceMatches: List[re.Match] = None

    def initMemory(self):
        self.strLiternalMatches: List[re.Match] = []
        self.threeslashCommentMatches: List[re.Match] = []
        self.twoslashCommentMatches: List[re.Match] = []
        self.quoteCommentMatches: List[re.Match] = []
        self.includeMatches: List[re.Match] = []
        self.pragmaonceMatches: List[re.Match] = []

    def memorizeMatches(self):
        """
        Find three types of patterns in the source file.

        Walk through the content char by char, and try to grab
        these matches when found.
        """
        self.initMemory()

        i = 1
        self.data = "\n" + self.data
        content_len = len(self.data)

        while i < content_len:
            j = i - 1
            current = self.data[i]
            previous = self.data[j]

            if current == '"':
                # String value.
                i = self.searchMatchAt(
                    j,
                    Patterns.string_pattern,
                    self.strLiternalMatches
                )
            elif current == '*' and previous == '/':
                # /* Multi-line comment */.
                i = self.searchMatchAt(
                    j,
                    Patterns.raw_quote_comment_pattern,
                    self.quoteCommentMatches
                )
            elif current == '/' and previous == '/':
                # /// Single-line comment starting with three slashes.
                i = self.searchMatchAt(
                    j,
                    Patterns.raw_threeslash_comment_pattern,
                    self.threeslashCommentMatches
                )
                # // Single-line comment starting with two slashes.
                if i == j + 2:
                    i = self.searchMatchAt(
                        j,
                        Patterns.raw_twoslash_comment_pattern,
                        self.twoslashCommentMatches
                    )
            elif current == '#' and previous == '\n':
                i = self.searchMatchAt(
                    j,
                    Patterns.include_pattern,
                    self.includeMatches
                )
                if i == j + 2:
                    i = self.searchMatchAt(
                        j,
                        Patterns.pragmaonce_pattern,
                        self.pragmaonceMatches
                    )
            else:
                # Skip to the next char.
                i += 1

    def removeUseless(self, removeComment: bool):
        """
        Remove all useless patterns.
        """
        if self.strLiternalMatches is None:
            self.memorizeMatches()

        data = ""
        lastend = 0

        iComment = 0
        iPragma = 0

        def decideRemoveType(lsts: List[List[re.Match]], *args: int) -> Optional[List[re.Match]]:
            """Find the first match in args, args should be a list of List[re.Match]."""
            index = -1
            start = len(self.data) + 1
            for i, lst in enumerate(lsts):
                if len(lst) == args[i]:
                    continue
                if lst[args[i]].start() < start:
                    start = lst[args[i]].start()
                    index = i
            if index == -1:
                return None
            return lsts[index]

        if removeComment:
            lst = decideRemoveType(
                [
                    self.twoslashCommentMatches,
                    self.pragmaonceMatches
                ],
                iComment,
                iPragma)
        else:
            lst = decideRemoveType(
                [self.pragmaonceMatches],
                iPragma
            )

        while lst is not None:
            if lst is self.twoslashCommentMatches:
                m = self.twoslashCommentMatches[iComment]
                iComment += 1
            else:
                m = self.pragmaonceMatches[iPragma]
                iPragma += 1

            if not removeComment and lst is self.twoslashCommentMatches:
                continue

            data += self.data[lastend:m.start()]
            lastend = m.end()
            if lst is self.twoslashCommentMatches and self.data[lastend - 1] == '\n':
                lastend -= 1

            if removeComment:
                lst = decideRemoveType(
                    [
                        self.twoslashCommentMatches,
                        self.pragmaonceMatches
                    ],
                    iComment,
                    iPragma)
            else:
                lst = decideRemoveType(
                    [self.pragmaonceMatches],
                    iPragma
                )

        data += self.data[lastend:]
        self.data = data

        self.forget()
        self.trimspace()

    def findIncludes(self):
        """
        Find all includes and memorize them.
        """
        if self.strLiternalMatches is None:
            self.memorizeMatches()

        for m in self.includeMatches:
            self.includes.append(IncludeStruct(m))

    def searchFile(self, searchPath: List[str], relpath: str, dlist: List[Dict[str, _T]]) -> Optional[_T]:
        fullpath = [os.path.abspath(os.path.join(
            os.path.dirname(self.filename), relpath))]
        for path in searchPath:
            fullpath.append(os.path.abspath(os.path.join(path, relpath)))

        for d in dlist:
            for path in fullpath:
                v = d.get(path)
                if v is not None:
                    return v
        return None

    def searchMatchAt(self, index: int, pattern: re.Pattern, matchList: List[re.Match]) -> int:
        """
        Test if `self.data` matches `pattern` at index `index`.
        Return the end of match if matches, else index + 2.
        """
        match = pattern.match(self.data, index)
        if match:
            matchList.append(match)
            return match.end()
        return index + 2

    def readInclude(self, any):
        """Override this."""
        raise NotImplementedError()

    def process(self) -> str:
        """Override this."""
        raise NotImplementedError()

    def trimspace(self) -> None:
        if self.strLiternalMatches is None:
            self.memorizeMatches()
        data = self.data
        rows = data.split('\n')
        ans = ""
        countChar = 0
        for row in rows:
            rt = row.rstrip()
            t = rt.lstrip()
            if len(t) == 0:
                countChar += 1
                ans += "\n"
                continue
            cannotLstrip = self.charInLiteral(countChar)
            cannotRstrip = self.charInLiteral(countChar + len(row))
            if cannotRstrip:
                # not pre-compile commands
                ans += row + "\n"
            elif cannotLstrip:
                # not pre-compile commands
                ans += rt + "\n"
            else:
                if t[0] == '#':
                    ans += t + "\n"
                else:
                    ans += rt + "\n"
            countChar += len(row) + 1
        self.data = ans
        self.forget()

    def charInLiteral(self, index: int) -> bool:
        for m in self.strLiternalMatches:
            if m.start() <= index and index < m.end():
                return True
        return False

    @overload
    @staticmethod
    def overlaps(_match: re.Match, _matches: re.Match) -> bool:
        ...

    @overload
    @staticmethod
    def overlaps(_match: re.Match, _matches: Any) -> bool:
        ...

    @staticmethod
    def overlaps(_match: re.Match, _matches):
        """
        Test if `_match` overlaps with `_matches`.

        `_matches` can be any iterable that contains only :class:`re.Match` objects,
        or just a :class:`re.Match` object.
        """
        if isinstance(_matches, re.Match):
            return not (_match.end() <= _matches.start() or _match.start() >= _matches.end())
        return any(FileProcessor.overlaps(_match, x) for x in _matches)

    @staticmethod
    def registerBaseDirectory(path: str):
        if path is None:
            raise ValueError("Base directory not set")

        if os.path.isabs(path):
            FileProcessor.baseDir = os.path.abspath(path)
        else:
            folder = os.path.curdir
            FileProcessor.baseDir = os.path.abspath(os.path.join(folder, path))

        if not os.path.exists(FileProcessor.baseDir) or not os.path.isdir(FileProcessor.baseDir):
            raise ValueError(f"No such directory: {FileProcessor.baseDir}")
