#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cr_reader.py — CRReader class.

Responsibilities:
  - Pre-scan the data folder to count files and events
  - Walk the JSON data folder and yield raw events with progress info
  - Reconstruct a specific event from CSV coordinates (for Step 2)
"""

import os
import json
from pathlib import Path
from typing import Iterator, Tuple, Optional, List

from inc.settings import output_align, IGNORED_FOLDER_PREFIX
from inc.cr.cr_writer import CREventCoords


class CRReader:
    """
    Iterates over all events in a data folder, or loads a specific
    event by its CSV coordinates for Step 2.
    """

    def __init__(self, raw_data_folder_name: str):
        self.raw_data_folder_name = raw_data_folder_name
        self.data_path = Path(f"../DATA/{raw_data_folder_name}/jsonData/")

    # ------------------------------------------------------------------ #
    #  Pre-scan                                                            #
    # ------------------------------------------------------------------ #

    def scan(self) -> Tuple[int, int]:
        """
        Quick pre-scan of the data folder.
        Counts JSON files only and estimates total events as
        n_files * N_EVTS_PER_CONV_FILE (from settings.py) to
        avoid opening every file — no delay before processing starts.

        Returns
        -------
        (n_files, n_events_estimated) : (int, int)
        """
        from inc.settings import N_EVTS_PER_CONV_FILE

        if not self.data_path.exists():
            return 0, 0

        n_files = 0
        for dirpath, dirnames, filenames in os.walk(self.data_path):
            dirnames.sort()
            filenames.sort()
            for json_file in filenames:
                if not json_file.endswith('.json'):
                    continue
                if json_file.startswith(IGNORED_FOLDER_PREFIX):
                    continue
                n_files += 1

        return n_files, n_files * N_EVTS_PER_CONV_FILE

    # ------------------------------------------------------------------ #
    #  Step 1: iterate over all events                                     #
    # ------------------------------------------------------------------ #

    def iter_events(
        self,
        n_files:  int = 0,
        n_events: int = 0,
    ) -> Iterator[Tuple[str, dict, dict, int, int, int]]:
        """
        Yield (json_file, event_dict, data_dict, event_index,
               file_counter, event_counter) for every event in the
        data folder, in sorted order.

        Parameters
        ----------
        n_files  : int — total file count from scan() for progress display
        n_events : int — total event count from scan() for progress display
        """
        if not self.data_path.exists():
            print(f"{output_align}!! Data folder not found: {self.data_path}")
            return

        file_counter  = 0
        event_counter = 0

        for dirpath, dirnames, filenames in os.walk(self.data_path):
            dirnames.sort()
            filenames.sort()

            for json_file in filenames:
                if not json_file.endswith('.json'):
                    continue
                if json_file.startswith(IGNORED_FOLDER_PREFIX):
                    continue

                file_counter += 1
                full_path = os.path.join(dirpath, json_file)

                file_progress = (f"[file {file_counter}/{n_files}]"
                                 if n_files > 0 else f"[file {file_counter}]")
                print(f"{output_align}{file_progress}  {json_file}")

                with open(full_path) as tf:
                    data = json.load(tf)

                for i, event in enumerate(data['all']):
                    event_counter += 1
                    yield json_file, event, data, i, file_counter, event_counter

    # ------------------------------------------------------------------ #
    #  Step 2: load a specific event by CSV coordinates                   #
    # ------------------------------------------------------------------ #

    def load_event(self, coords: CREventCoords) -> Optional[Tuple[dict, dict, int]]:
        """
        Load a single event identified by its CSV coordinates.

        Returns
        -------
        (event_dict, data_dict, event_index) or None if not found.
        """
        full_path = self.data_path / coords.json_file
        if not full_path.exists():
            print(f"{output_align}!! File not found: {full_path}")
            return None

        with open(full_path) as tf:
            data = json.load(tf)

        for i, event in enumerate(data['all']):
            if str(event.get('convertedEventID')) == coords.converted_event_id:
                return event, data, i

        print(
            f"{output_align}!! Event convertedEventID={coords.converted_event_id} "
            f"not found in {coords.json_file}."
        )
        return None

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def event_subdir(base_folder: str, event_id: str,
                     converted_file_id: str,
                     converted_event_id: str) -> str:
        """
        Build the per-event subdirectory path for single-trace plots.
        Pattern: {base_folder}/Event_{event_id}_{converted_event_id}
        """
        name = f"Event_{event_id}_{converted_event_id}"
        return os.path.join(base_folder, name)

    @staticmethod
    def event_metadata(event: dict, raw_data_folder_name: str,
                       path_to_folder_plots: str,
                       json_file: str) -> dict:
        """
        Extract and format the standard metadata fields from a raw event.
        """
        run_time           = str(event['runTime'])
        event_id           = str(event['eventId'])
        binary_file_id     = str(event['binaryFileID'])
        binary_event_id    = str(event['binaryEventID'])
        converted_file_id  = str(event['convertedFileID'])
        converted_event_id = str(event['convertedEventID'])

        evt_title = (
            f"{raw_data_folder_name} - Evt ID: {event_id} "
            f"({binary_file_id}, {binary_event_id}) "
            f"({converted_file_id}, {converted_event_id})"
        )
        save_file_name = (
            f"{path_to_folder_plots}/{json_file[:-5]}_"
            f"Evt{event_id}_{converted_event_id}"
        )

        return dict(
            run_time           = run_time,
            event_id           = event_id,
            binary_file_id     = binary_file_id,
            binary_event_id    = binary_event_id,
            converted_file_id  = converted_file_id,
            converted_event_id = converted_event_id,
            evt_title          = evt_title,
            save_file_name     = save_file_name,
        )
