"""
SILT Configuration System

Contains the configuration system that handles loading keys and values
into the config collection for use by the rest of the system.

Strongly inspired by Flask's config system, as it is essentially ideal.
"""

import errno
from typing import Callable, TextIO

import yaml


class Config(dict):
    """The config class behaves like a native python dict but
    provides methods to populate the values from modules, classes or
    files of various provenances.

    Strongly inspired by the Flask config structure, because it is
    sane and also a nice, extensible abstraction.
    """

    def __init__(self, defaults: dict = {}) -> None:
        dict.__init__(self, defaults)

    def from_object(self, obj: object) -> None:
        """Populate the configuration structure directly from the
        properties of a Ptython Object.

        Only UPPERCASE attributes of the object will be loaded.
        """
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_yaml(self, filepath: str) -> None:
        """Populate the configuration structure from a yaml file

        This method is a convenience wrapper used for shorthand for
        the from_file method with yaml.safe_load as the loader.

        See `from_file` for more information.
        """
        self.from_file(filepath, yaml.safe_load)

    def from_file(
        self, filepath: str, loader: Callable[[TextIO], dict], silent: bool = False
    ) -> bool:
        """Populate the configuration structure from a file
        with a specified loader.

        The loader should be a callable that takes a file object
        and returns a mapping of the data contained within.

        Example:
        .. code-block:: python
            import yaml
            config.from_file('config.yaml', loader=yaml.safe_load)

        This allows the format to be easily decoupled from the internal
        config structure.
        """
        try:
            with open(filepath) as f:
                confobj = loader(f)
        except IOError as e:
            # Silence out exclusively file not found or is directory
            # errors, anything more serious needs to be raised
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False

            e.strerror = "Unable to load configuration file: {}".format(e.strerror)
            raise

        return self.update_from_mapping(confobj)

    def update_from_mapping(self, *mapping, **kwargs) -> bool:
        """Populate values like the `update()` method, but
        only looks for keys in UPPERCASE to allow for nesting or
        module level values.
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], "items"):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                "Config mapping expected at most 1 argument, got {}".format(
                    len(mapping)
                )
            )

        mappings.append(kwargs.items())

        for mapping in mappings:
            for key, value in mapping:
                if key.isupper():
                    self[key] = value

        return True
