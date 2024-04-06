"""
The config module simplifies loading and parsing config files.

Config files may be written in YAML or JSON.
"""

from __future__ import annotations

import copy
import glob
import json
import os
from collections import deque
from collections.abc import Mapping, Sequence
from datetime import timedelta
from typing import Any, NamedTuple, TYPE_CHECKING, overload

import yaml

if (TYPE_CHECKING):
    from collections.abc import Collection, Iterator


class ConfigData(NamedTuple):
    """Tuple to store config data with file path."""

    value: Any
    path: (str | None)


class Config:
    """
    Config is a utility class with a single public 'load' classmethod.

    Config.load() will search for and process all config files and
    return a Config object.

    A Config object may be accessed as a Mapping or an object.
    All keys are case-insensitive.
    """

    __slots__ = ('_data', '_file_paths')

    _data: dict[str, ConfigData]
    _file_paths: list[str]

    @classmethod
    def _load_file(cls, config_file_path: str) -> tuple[dict[str, Any], (str | None)]:
        _, extension = os.path.splitext(config_file_path)
        try:
            with open(config_file_path) as config_file:
                if ('.json' == extension.lower()):
                    return (json.load(config_file), config_file_path)
                return (yaml.safe_load(config_file), config_file_path)
        except Exception:
            return ({}, None)

    @classmethod
    def _set_path(cls, value: Any, path: str = None) -> Any:
        """Add path information to nested data."""
        if (isinstance(value, Mapping)):
            return {name: ConfigData(cls._set_path(item, path), path) for name, item in value.items()}
        if (isinstance(value, Sequence) and not isinstance(value, str)):
            return [cls._set_path(item, path) for item in value]
        return value

    @classmethod
    def _merge(cls, base: (dict[str, ConfigData] | None),
               extra: Mapping[str, ConfigData]) -> dict[str, ConfigData]:
        """Merge extra ConfigData map into ConfigData map."""
        if (base is None):
            base = {}
        for name, (value, path) in extra.items():
            if (isinstance(value, Mapping)):
                base_data = base.get(name)
                base_data = base_data.value if (base_data is not None) else None
                base[name] = ConfigData(cls._merge(base_data, value), path)
            else:
                base[name] = ConfigData(value, path)
        return base

    @classmethod
    def _find_subdir_files(cls, config_dir: str, script_name: str, config_name: str = None) -> list[str]:
        file_paths: list[str] = []
        sub_dirs = ['conf.d', 'config.d', f'{script_name}.d']
        if (config_name):
            sub_dirs.append(f'{config_name}.d')
        for sub_dir in sub_dirs:
            for extension in ('.json', '.yml', '.yaml'):
                file_paths += glob.glob(os.path.join(config_dir, sub_dir, f'*{extension}'))
        return sorted(file_paths)

    @classmethod
    def _find_extensions(cls, config_path: str) -> list[str]:
        file_paths: list[str] = []
        for extension in ('.json', '.yml', '.yaml'):
            config_file_path = config_path + extension
            if (os.path.isfile(config_file_path)):
                file_paths.append(config_file_path)
        return file_paths

    @classmethod
    def _find_files(cls, config_path: str, script_name: str) -> list[str]:
        file_paths = []
        if (os.path.isfile(config_path)):
            file_paths.append(config_path)
            config_name, _ = os.path.splitext(os.path.basename(config_path))
            file_paths += cls._find_subdir_files(os.path.dirname(config_path), script_name, config_name)
        else:
            if (os.path.isdir(config_path)):
                for filename in ('config', 'config.local', script_name, script_name + '.local'):
                    file_paths += cls._find_extensions(os.path.join(config_path, filename))
                file_paths += cls._find_subdir_files(config_path, script_name)
            else:
                config_dir = os.path.dirname(config_path)
                config_name, _ = os.path.splitext(os.path.basename(config_path))
                if (os.path.isdir(config_dir)):
                    file_paths += cls._find_extensions(config_path)
                    file_paths += cls._find_subdir_files(config_dir, script_name, config_name)
        return file_paths

    @classmethod
    def load(cls, script_path: str, config_path: str = None, default: Mapping[str, Any] = None) -> Config:
        """
        Load configuration.

        script_path is the full path of the primary script file, e.g. __name__

        config_path is an optional path to a config file to load.
        If config_path is a directory,
        it will search for the files 'config', 'config.local', '{script_name}', and '{script_name}.local',
        loading each found file in turn.
        If config_path is not a directory or an existing file,
        it will attempt to load config_path + ['.json', '.yaml', '.yml'].
        It will also load all json and yaml files in the following subdirectories of the config_path:
        'conf.d', 'config.d', '{script_name}.d'

        If config_path is None, it will search for files in: the script's installed directory,
        including all parent directories (subdirectories override parents);
        /etc/{script_name}; and the current directory.
        Including json and yaml files in subdirectories named 'conf.d', 'config.d', '{script_name}.d' of
        all searched directories.
        Config files found later will override values in earlier files.

        default contains default values that will be overridden by any config file.
        """
        script_dir = os.path.dirname(os.path.abspath(script_path))
        script_name = os.path.basename(script_path)
        config_data = cls._set_path(default) if (default is not None) else {}

        config_paths = deque([script_dir])
        drive, dir = os.path.splitdrive(script_dir)
        while (os.sep != dir):
            dir = os.path.dirname(dir)
            config_paths.appendleft(drive + dir)
        if (config_path):
            config_paths.append(os.path.expanduser(config_path))
        else:
            etc_dir = os.path.join(drive, os.sep, 'etc', script_name)
            if etc_dir in config_paths:
                config_paths.remove(etc_dir)
            config_paths.append(etc_dir)
            if (os.getcwd() not in config_paths):
                config_paths.append(os.getcwd())

        file_paths: list[str] = []
        for config_path in config_paths:
            file_paths += cls._find_files(config_path, script_name)

        data_file_paths: list[str] = []
        for file_path in file_paths:
            file_data, path = cls._load_file(file_path)
            if (path):
                data_file_paths.append(path)
                config_data = cls._merge(config_data, cls._set_path(file_data, path))
        return Config(config_data=config_data, file_paths=data_file_paths)

    def __init__(self, data: Mapping[str, Any] = None,
                 config_data: Mapping[str, ConfigData] = None, file_paths: Sequence[str] = None) -> None:
        self._data = {}
        self._file_paths = list(file_paths) if (file_paths) else []
        if (data is not None):
            config_data = self._set_path(data)

        for name, (value, path) in (config_data or {}).items():
            self._data[name.lower()] = ConfigData(self._convert(value), path)

    def _convert(self, value: Any, path: str = None) -> Any:
        """Convert mappings into Configs recursively."""
        if (isinstance(value, Mapping)):
            return Config(config_data=value)
        if (isinstance(value, Sequence) and not isinstance(value, str)):
            return [self._convert(item, path) for item in value]
        return value

    def __bool__(self) -> bool:
        """Test if empty."""
        return (0 < len(self._data))

    def __len__(self) -> int:
        """Return number of values."""
        return len(self._data)

    def __eq__(self, other: Any) -> bool:
        """Compare to other."""
        return self._data.__eq__(other)

    def __ne__(self, other: Any) -> bool:
        """Compare to other."""
        return self._data.__ne__(other)

    def __getitem__(self, name: str) -> Any:
        """Allow access to value via []."""
        return self._data[name.lower()].value

    def __contains__(self, name: str) -> bool:
        """Test if value is present via 'in'."""
        return ((name.lower() in self._data) or (name in dir(self)))

    def __deepcopy__(self, memo: Any) -> object:
        """Handle deep copy by only copying data."""
        clone = type(self)(data={}, file_paths=self._file_paths)
        clone._data = copy.deepcopy(self._data, memo)
        return clone

    def keys(self) -> Collection[str]:
        """Return all keys."""
        return self._data.keys()

    def values(self) -> Collection[Any]:
        """Return all values."""
        return [value.value for value in self._data.values()]

    def items(self) -> Collection[tuple[str, Any]]:
        """Return all keys and values."""
        return [(name, value.value) for name, value in self._data.items()]

    def get(self, name: str, default: Any = None) -> Any:
        """Get an item."""
        key = name.lower()
        if (key not in self._data):
            return default
        return self._data[key].value

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        return self._data.__iter__()

    def __getattr__(self, name: str) -> Any:
        """Allow direct access to values via '.'."""
        data = object.__getattribute__(self, '_data')
        key = name.lower()
        if (key in data):
            return data[key].value
        return object.__getattribute__(self, name)

    @property
    def config_file_paths(self) -> Sequence[str]:
        """Paths of config files loaded."""
        return self._file_paths

    def get_config_file_path(self, name: str) -> (str | None):
        """Get path of config file item was loaded from."""
        key = name.lower()
        if (key not in self._data):
            return None
        return self._data[key].path

    @overload
    def get_int(self, name: str) -> (int | None): ...  # noqa
    @overload
    def get_int(self, name: str, default: int) -> int: ...  # noqa
    def get_int(self, name: str, default: int = None) -> (int | None):  # noqa: E301
        """
        Get an item as an int.

        Returns default if missing or not an int.
        """
        value = self.get(name)
        if (value is None):
            return default
        try:
            return int(value)
        except ValueError:
            return default

    @overload
    def get_float(self, name: str) -> (float | None): ...  # noqa
    @overload
    def get_float(self, name: str, default: float) -> float: ...  # noqa
    def get_float(self, name: str, default: float = None) -> (float | None):  # noqa: E301
        """
        Get an item as a float.

        Returns default if missing or not a float.
        """
        value = self.get(name)
        if (value is None):
            return default
        try:
            return float(value)
        except ValueError:
            return default

    @overload
    def get_bool(self, name: str) -> (bool | None): ...  # noqa
    @overload
    def get_bool(self, name: str, default: bool) -> bool: ...  # noqa
    def get_bool(self, name: str, default: bool = None) -> (bool | None):  # noqa: E301
        """
        Get an item as a bool.

        Returns default if missing or not a bool.
        """
        value = self.get(name)
        if (value is None):
            return default
        if (isinstance(value, bool)):
            return value
        return default

    @overload
    def get_path(self, name: str) -> (str | None): ...  # noqa
    @overload
    def get_path(self, name: str, default: str) -> str: ...  # noqa
    def get_path(self, name: str, default: str = None) -> (str | None):  # noqa: E301
        """
        Get an item as an absolute path.

        Relative paths are resolved to the config file the item was loaded from.
        Returns default if missing.
        """
        key = name.lower()
        if (key not in self._data):
            return default
        data = self._data[key]
        if (data.value is None):
            return None
        if (data.path is None):
            return os.path.abspath(os.path.expanduser(data.value))
        return os.path.abspath(os.path.join(os.path.dirname(data.path), os.path.expanduser(data.value)))

    @overload
    def get_duration(self, name: str) -> (timedelta | None): ...  # noqa: E704
    @overload
    def get_duration(self, name: str, default: timedelta) -> timedelta: ...  # noqa: E704
    def get_duration(self, name: str, default: timedelta = None) -> (timedelta | None):  # noqa: E301
        """
        Get an item as a timedelta.

        Accepts int values (seconds),
        or string values with s|m|h|d|w suffix for seconds, minutes, hours, days, or weeks.
        """
        value = self.get(name)
        if (value is None):
            return default
        if (isinstance(value, int)):
            return timedelta(seconds=value)
        if (isinstance(value, str)):
            if (value.endswith('s')):
                return timedelta(seconds=int(value[:-1]))
            if (value.endswith('m')):
                return timedelta(minutes=int(value[:-1]))
            if (value.endswith('h')):
                return timedelta(hours=int(value[:-1]))
            if (value.endswith('d')):
                return timedelta(days=int(value[:-1]))
            if (value.endswith('w')):
                return timedelta(weeks=int(value[:-1]))
        raise ValueError('invalid duration value, must be int (seconds) or str with s|m|h|d|w suffix')

    def set_default(self, name: str, value: Any) -> None:
        """Set a default value."""
        key = name.lower()
        if (key not in self._data):
            self._data[key] = ConfigData(self._convert(self._set_path(value)), None)

    def __repr__(self) -> str:
        """Debug representation."""
        lines: list[str] = []
        for name, (value, path) in self._data.items():
            if (isinstance(value, Sequence) and not isinstance(value, str)):
                lines.append(f'{name} ({path}): [')
                for item in value:
                    lines += [('  ' + line) for line in repr(item).split('\n')]
                lines.append(']')
            else:
                lines += f'{name} ({path}): {repr(value)}'.split('\n')
        return super().__repr__() + '\n' + '\n'.join([('  ' + line) for line in lines])
