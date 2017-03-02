# -- STRINGS.PY - Dynamic language library for ACE-NG --
# Author:     Owen Tourlamain
# Supervisor: Dr. Laurence Tyler

import json
import sys
import os

class Strings(object):
    """
    strings.py

    Libarary for ace-ng that enables dynamic loading of language files.

    Language files should be stored in ACE-NG/lang/ or in the user configuable
    location (defaults to ~/.ace-ng/lang/).

    Files should be JSON formatted, use the en-GB file for the list of
    properties required.

    Files should be named using a combination of ISO 639-1 and 3166-1. For
    example the file for UK English is: "en-GB.json" and Mexican Spanish is:
    "es-MX.json".

    Users can specify which language should be used through the "lang_pref"
    config setting, the value should match the file name minus the suffix. For
    example: "en-GB" or "es-MX".

    If a file is missing a property then this library will fall back to the next
    relevant choice. The libarary prioritises the file from the users lang
    directory first, then the matching lang file in ACE-NG/lang/ (if any), then
    finally the default en-GB file as this is assumed to always be complete.

    The library can be used by initialising it with a populated config
    dictionary, then accessing the properties as python module attributes. E.g:

    from lib.strings import Strings
    self.Strings = Strings(self.config)
    print(self.Strings.appName)
    """

    def __init__(self, config):

        # First lets read the default language file
        try:
            with open("lang/en-GB.json", 'r') as defaultLang:
                self.langDict = json.load(defaultLang)
        except ValueError:
            # TODO: Make errors more effective
            print("Default lang file is malformed, please repair!")
            sys.exit(1)
        except OSError:
            print("Error accessing default lang file, please fix permissions!")
            sys.exit(1)

        # Now lets read in the other in-built language files. There is no need
        # to check for other in-built files if we are using the default language
        if not config["lang_pref"] == "en-GB":
            if os.path.exists("lang") and os.path.isdir("lang"):
                for file in os.listdir("lang"):
                    if file.endswith(".json"):
                        if config["lang_pref"] + ".json" == file:
                            langFile = os.path.join("lang", file)
                            try:
                                with open(langFile, 'r') as lang:
                                    # Using .update() alows us to override the
                                    # previous definitions without losing all
                                    # definitions.
                                    self.langDict.update(json.load(lang))
                            except ValueError:
                                # TODO: Make warnings more effective
                                print("Lang file %s is malformed, skipping..." % langFile)
                            except OSError:
                                print("Error accessing lang file %s, skipping..." % langFile)

        # Now lets look in the user configurable location, we should always read
        # these files incase the user wants to override the defaults.
        if os.path.exists(config["usr_lang_dir"]) and os.path.isdir(config["usr_lang_dir"]):
            for file in os.listdir(config["usr_lang_dir"]):
                if file.endswith(".json"):
                    if config["lang_pref"] + ".json" == file:
                        langFile = os.path.join(config["usr_lang_dir"], file)
                        try:
                            with open(langFile, 'r') as lang:
                                    self.langDict.update(json.load(lang))
                        except ValueError:
                            # TODO: Make warnings more effective
                            print("Lang file %s is malformed, skipping..." % langFile)
                        except OSError:
                            print("Error accessing lang file %s, skipping..." % langFile)

        # We turn each of the dictionary keys into attributes to make them
        # easier to access.
        for name in self.langDict:
            setattr(self, name, self.langDict[name])
