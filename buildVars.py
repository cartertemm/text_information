# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x : x

# Add-on information variables
addon_info = {
	# for previously unpublished addons, please follow the community guidelines at:
	# https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
	# add-on Name, internal for nvda
	"addon_name" : "text-information",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown on installation and add-on information.
	"addon_summary" : _("text information"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-ons manager
	"addon_description" : _("""Provides information about selected text. Press NVDA+; (semicolon) to activate, NVDA + shift + ; to get information from the clipboard, and NVDA + control + ; to speak the last retrieved information. You can press this twice to have it displayed in a browseable dialog. Note: for non-english keyboard layouts these gestures might need to be redefined in the input gestures dialog."""),
	# version
	"addon_version" : "1.0",
	# Author(s)
	"addon_author" : u"Carter Temm <crtbraille@gmail.com>",
	# URL for the add-on documentation support
	"addon_url" : "http://github.com/cartertemm/text_information",
	# Documentation file name
	"addon_docFileName" : "readme.html",
}


import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = []

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []
