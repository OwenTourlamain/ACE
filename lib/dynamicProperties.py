# -- STRINGS.PY - Dynamic language library for ACE-NG --
# Author:     Owen Tourlamain
# Supervisor: Dr. Laurence Tyler

import json
import sys
import os

class DynamicProperties(object):
    """
    dynamicProperties.py

    Libarary for ace-ng that enables dynamic loading of properties from JSON
    files.

    from lib.dynamicProperties import DynamicProperties
    strings = DynamicProperties("lang/en-GB.json")
    print(strings.appName)

    ----
    Language files should be stored in ACE-NG/lang/ or in the user configuable
    location (defaults to ~/.ace-ng/lang/).

    Files should be JSON formatted, look in the en-GB file for the list of
    properties required.

    Files should be named using a combination of ISO 639-1 and 3166-1. For
    example the file for UK English is: "en-GB.json" and Mexican Spanish is:
    "es-MX.json".

    Users can specify which language should be used through the "lang_pref"
    config setting, the value should match the file name minus the suffix. For
    example: "en-GB" or "es-MX".

    If a file is missing a property then this library will fall back to the next
    relevant choice. The library prioritises the file from the users lang
    directory first, then the matching lang file in ACE-NG/lang/ (if any), then
    finally the default en-GB file as this is assumed to always be complete.

    The library can be used by initialising it with a populated config
    dictionary, then accessing the properties as python module attributes. E.g:

    """

    def __init__(self, defaultFile, verbose, cleanPaths=False):

        # save the default file so we don't re-read it later
        self.defaultFile = defaultFile
        self.cleanPaths = cleanPaths
        self.verbose = verbose

        # First lets read the default file
        try:
            if self.verbose: print("Reading: %s" % defaultFile)
            with open(defaultFile, 'r') as default:
                self.dict = json.load(default)
        except ValueError:
            raise MalformedDataError("File (%s) is malformed" % defaultFile)
        except OSError:
            raise FileAccessError("Error accessing file %s" % defaultFile)

        self._set_attributes()

    def update(self, dirs, match=None):

        for dir in dirs:
            if not os.path.isdir(dir):
                try:
                    os.makedirs(dir)
                except OSError:
                    print("Error creating directory '%s' skipping..." % dir)
                    continue
            for file in os.listdir(dir):
                if file.endswith(".json"):
                    if match:
                        if match not in file:
                            continue

                    fileName = os.path.join(dir, file)
                    try:
                        if self.verbose: print("Reading: %s" % fileName)
                        with open(fileName, 'r') as thisFile:
                            self.dict.update(json.load(thisFile))
                    except ValueError:
                        raise MalformedDataError("File (%s) is malformed" % fileName)
                    except OSError:
                        raise FileAccessError("Error accessing file %s" % fileName)

            self._set_attributes()

    def _set_attributes(self):
        # If needed tidy up the paths before setting the properties
        if self.cleanPaths:
            self._cleanPaths()

        # We turn each of the dictionary keys into attributes to make them
        # easier to access.
        for name in self.dict:
            setattr(self, name, self.dict[name])

    def _cleanPaths(self):
        for item in self.dict:
            if "dir" in item:
                self.dict[item] = os.path.normpath(self.dict[item])
                self.dict[item] = os.path.expanduser(self.dict[item])

class MalformedDataError(Exception):
    # TODO: docstrings
    """docstring for MalformedDataError."""
    def __init__(self, value):
        self.value = value

    def __str__(self,):
        return repr(self.value)

class FileAccessError(Exception):
    # TODO: docstrings
    """docstring for FileAccessError."""
    def __init__(self, value):
        self.value = value

    def __str__(self,):
        return repr(self.value)
