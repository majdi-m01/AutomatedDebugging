import ast
import logging
import os
import pickle
import shutil
from ast import NodeTransformer
from os import walk
from pathlib import Path
from types import FrameType
from typing import List, Any, Set, Dict, Tuple

from debuggingbook import Slicer
from debuggingbook.StatisticalDebugger import ContinuousSpectrumDebugger, Collector, RankingDebugger

DependencyDict = Dict[
    str,
    Set[
        Tuple[
            Tuple[str, Tuple[str, int]],
            Tuple[Tuple[str, Tuple[str, int]], ...]
        ]
    ]
]


class Instrumenter(NodeTransformer):

    def instrument(self, source_directory: Path, dest_directory: Path, excluded_paths: List[Path], log=False) -> None:
        """
        TODO: implement this function, such that you get an input directory, instrument all python files that are
        TODO: in the source_directory whose prefix are not in excluded files and write them to the dest_directory.
        TODO: keep in mind that you need to copy the structure of the source directory.
        :param source_directory: the source directory where the files to instrument are located
        :param dest_directory:   the output directory to which to write the instrumented files
        :param excluded_paths:   the excluded path that should be skipped in the instrumentation
        :param log:              whether to log or not
        :return:
        """

        if log:
            logging.basicConfig(level=logging.INFO)

        assert source_directory.is_dir()

        if dest_directory.exists():
            shutil.rmtree(dest_directory)
        os.makedirs(dest_directory)
        shutil.copy('lib.py', dest_directory / 'lib.py')

        for directory, sub_directories, files in os.walk(source_directory):
            # Iterates directory and its subdirectories in the form of (directory, [sub_directories], [files])
            logging.info(f'Current dir: {directory}')
            logging.info(f'Current sub_dirs: {sub_directories}')
            logging.info(f'Current files: {files}')

        for (dirpath, dirnames, filenames) in walk(source_directory):
            if dirnames == []:
                if filenames != []:
                    for f in filenames:
                        shutil.copy(dirpath + "\\\\" + f, dest_directory / f)
            else:
                for d in dirnames:
                    shutil.copytree(dirpath + "\\" + d, dest_directory / d)
                    if d not in dirnames:
                        if filenames != []:
                            for f in filenames:
                                shutil.copy(dirpath + "\\\\" + f, dest_directory / d / f)
                    else:
                        if filenames != []:
                            for f in filenames:
                                shutil.copy(dirpath + "\\\\" + f, dest_directory / f)
        files = []
        for (dirpath, dirnames, filenames) in walk(dest_directory):
            for file in filenames:
                if file.startswith('test_') or file.startswith('lib') or file.startswith('__'):
                    continue
                else:
                    files.append(dirpath + "\\" + file)
        for f in files:
            with open(f, 'r') as contents:
                save = contents.read()
            if save.startswith('from lib import _data'):
                continue
            else:
                with open(f, 'w') as contents:
                    call_tree = ast.parse(save)
                    Slicer.TrackCallTransformer().visit(call_tree)
                    Slicer.TrackSetTransformer().visit(call_tree)
                    Slicer.TrackGetTransformer().visit(call_tree)
                    Slicer.TrackControlTransformer().visit(call_tree)
                    Slicer.TrackReturnTransformer().visit(call_tree)
                    Slicer.TrackParamsTransformer().visit(call_tree)
                    contents.write(ast.unparse(call_tree))
                with open(f, 'r') as contents:
                    updated = contents.read()
                with open(f, 'w') as contents:
                    contents.write('from lib import _data' + '\n')
                with open(f, 'a') as contents:
                    contents.write(updated)

class DependencyCollector(Collector):

    def __init__(self, dump_path: Path):
        super().__init__()
        self.dump_path = dump_path
        self.event_set = set()
        self.locations = []

    def traceit(self, frame: FrameType, event: str, arg: Any) -> None:
        pass  # deactivate tracing overall, not required.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.dump_path, 'rb') as dump:
            deps = pickle.load(dump)
        self.collect(deps)

    def collect(self, dependencies: DependencyDict):
        """
        TODO: Collect the dependencies in the specified format.
        :param dependencies: The dependencies for a run
        :return:
        """
        for dep in dependencies.get('data'):
            self.event_set.add(dep)
        for dep in dependencies.get('control'):
            self.event_set.add(dep)
        self.event_set = sorted(self.event_set)

    def events(self) -> Set[Any]:
        return self.event_set


class CoverageDependencyCollector(DependencyCollector):

    def events(self) -> Set[Any]:
        self.locations = self.iterate_tuple(self.event_set)
        for loc in self.locations:
            if isinstance(loc, str):
                if loc.startswith('<'):
                    self.locations.remove(loc)
        i = 0
        for loc in self.locations:
            if (i % 2) == 1:
                if isinstance(loc, str):
                    del self.locations[i - 1]
            i += 1
        funcs = []
        lines = []
        for loc in self.locations:
            if isinstance(loc, str):
                funcs.append(loc)
            if isinstance(loc, int):
                lines.append(loc)
        updated_locations = []
        for i, l in enumerate(lines):
            if l is not None:
                f = funcs[i]
                updated_locations.append((f, l))
        return set(updated_locations)

    def iterate_tuple(self, tuples, acc=None):
        if acc is None:
            acc = []
        for item in tuples:
            if isinstance(item, tuple):
                self.iterate_tuple(item, acc)
            else:
                acc.append(item)
        return acc

class DependencyDebugger(ContinuousSpectrumDebugger, RankingDebugger):

    def __init__(self, coverage=False, log: bool = False):
        super().__init__(CoverageDependencyCollector if coverage else DependencyCollector, log)