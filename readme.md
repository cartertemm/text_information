# Text Information

This add-on allows for getting information based on selected text. Simply select something and use a keystroke to get information. You should, hopefully, be presented with something that fits the context.

note: This package is distributed under the terms of the GNU General Public License, version 2 or later. Please see the file COPYING.txt for further details.

## keystrokes

* NVDA+; (semicolon) - provides information based on the text that's selected
* NVDA+SHIFT+; (semicolon): provides information about text on the clipboard
* NVDA+control+; (semicolon): speaks the last reported information. Press twice to get it displayed in a dialog.

## supported services

Currently, the following features are supported:

* IP address information using the IPInfoDB API. An API key is provided, however I by no means guarantee it'll always work. You can generate your own, and enter it at the top of __init__.py, replacing the old one.
* english dictionary definitions from the princeton wordnetweb. Note: these definitions are not the best, and the database lacks definitions for simple words, e.g. could, you, etc.
* ISBN lookups via the google books API
* credit card type verification

Note: Regular expressions are used to verify data. There are currently some that aren't used, phone numbers and emails. This might be changed in the future.

## contributing

Contributions are appreciated. You can either submit a PR, or get in contact with the following info:

twitter: @cartertemm

email: crtbraille@gmail.com