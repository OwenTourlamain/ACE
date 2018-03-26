ACE: Data capture application for the Aberystwyth University PanCam Emulator (AUPE)
- Author:     Owen Tourlamain
- Supervisor: Dr. Laurence Tyler

Note: This project relies upon code that cannot be included for licencing reasons, as such it will not run in its current form.

Usage:
 ace-ng [-fv]

 -f, --faupe,   Skip connection to AUPE server and launch FAUPE server
 -v, --verbose, Print more information to the console

Dependencies:
 - Python 3.4
 - Python 2.X
 - PyQt5
 - Pillow
 For most Linux systems all dependancies can be met by running:
	apt-get install python3-pyqt5

Notable system features:
- Dynamic language files:
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

- Extras:
  Extension module template included, as well as a simple example extension,
  calibrate.py. Move this file to ext to load it into ACE-NG. An example panorama file 
  has also been included here.

Acknowledgements:
- lib/au/*, and bin/*:
  Provided by Dr. Laurence Tyler, used without modification.

- lang/cy-GB.json:
  File created by the author, translation services provided by James Cox (jsc12@aber.ac.uk)

- Remaining files:
  Created solely by the author
  
Licencing
The author withholds all permissions for use, modification and redistribution of this work.
