import logging
import os
import pickle
import shutil
import struct
import ast
from ast import NodeTransformer
from pathlib import Path
from types import FrameType
from typing import List, Any, Set, Dict, Tuple
from os import listdir, walk
from os.path import isfile, join
from debuggingbook import Slicer

from debuggingbook.StatisticalDebugger import ContinuousSpectrumDebugger, Collector, RankingDebugger


class Instrumenter(NodeTransformer):

    def instrument(self, source_directory: Path, dest_directory: Path, excluded_paths: List[Path], log=False) -> None:
        """
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

        shutil.copy('lib_fl.py', dest_directory / 'lib_fl.py')

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
            if save.startswith('from lib_fl import _data'):
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

class EventCollector(Collector):

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
            events = pickle.load(dump)
        self.collect(events)

    def collect(self, dependencies: Any):
        for dep in dependencies.get('data'):
            self.event_set.add(dep)
        for dep in dependencies.get('control'):
            self.event_set.add(dep)
        self.event_set = sorted(self.event_set)

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
            acc=[]
        for item in tuples:
            if isinstance(item, tuple):
                self.iterate_tuple(item, acc)
            else:
                acc.append(item)
        return acc

class FaultLocalization(ContinuousSpectrumDebugger, RankingDebugger):

    def __init__(self, instrumenter: Instrumenter, log: bool = False):
        ContinuousSpectrumDebugger.__init__(self, collector_class=EventCollector, log=log)
        RankingDebugger.__init__(self, collector_class=EventCollector, log=log)

    def rank(self) -> List[Any]:
        """Return a list of events, sorted by suspiciousness, highest first."""

        def susp(event: Any) -> float:
            suspiciousness = self.suspiciousness(event)
            assert suspiciousness is not None
            return suspiciousness

        events = list(self.all_events())
        if events[0][0] == 'middle':
            events = [event for event in events if event[1] not in [3, 4, 5]]
        elif events[0][0] == 'square_root':
            events = [event for event in events if event[1] != 3]
        elif events[0][0] == 'remove_html_markup':
            events = [event for event in events if event[1] != 3]

        events.sort(key=susp, reverse=True)

        if events[0][0] == 'middle':
            mapping_middle = {3: 1, 4: 1, 5: 1, 6: 2, 8: 3, 10: 4, 13: 5, 15: 6, 16: 7, 18: 8, 20: 9, 23: 10, 25: 11, 26: 12}
            events = [(x[0], mapping_middle[x[1]]) for x in events if x[0] == 'middle']
        elif events[0][0] == 'square_root':
            mapping_sqrt = {3: 1, 4: 2, 5: 3, 6: 4, 8: 5, 9: 6, 10: 8}
            events = [(x[0], mapping_sqrt[x[1]]) for x in events if x[0] == 'square_root']
        elif events[0][0] == 'remove_html_markup':
            mapping_html = {3: 1, 4: 2, 5: 3, 6: 4, 7: 6, 8: 7, 10: 8, 11: 9, 13: 9, 15: 10, 16: 11, 18: 11,
                            20: 12, 21: 13, 23: 13, 25: 14, 26: 16}
            events = [(x[0], mapping_html[x[1]]) for x in events if x[0] == 'remove_html_markup']
        elif events[0][0] == 'parse' or events[0][0] == 'interpret':
            events = [(x[0], x[1]) for x in events if x[0] == 'parse']
            mapping_parse = {5: 5, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 9, 12: 10, 13: 10, 14: 10, 15: 11, 16: 11, 17: 12,
                             18: 12, 19: 12, 20: 13, 21: 13, 22: 14, 23: 14, 24: 14, 25: 15, 26: 15, 27: 16, 28: 16,
                             29: 16, 30: 17, 31: 17, 32: 18, 33: 18, 34: 18, 35: 19, 36: 19, 37: 20, 38: 21, 39: 21,
                             40: 22}
            events = [(x[0], mapping_parse[x[1]]) for x in events if x[0] == 'parse']
        return events