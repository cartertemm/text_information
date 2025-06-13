# Text Information

This add-on provides users with contextual information, fitting a wide variety of use cases.
With a single keypress, it can give you the meaning of a word, geolocate an IP address, and tell you about a book (via ISBN). Simply select something, use your assigned keystroke, and wait.

## Supported services

Currently, the following features are supported:

* IP address information. Includes geolocation, ISP, VPN/tor exit node and cellular network identification.
* english dictionary definitions, part of speech, example sentences, synonyms, antonyms, etc. Courtesy of [Dictionary API](https://github.com/cartertemm/dictionary-api), [web version here](https://dictionary.ctemm.me/)
* ISBN lookups via the google books API
* credit card type verification (Mastercard, Visa, Discover, Amex, etc)

The add-on implements support for identifying phone numbers and email addresses as well, though no actual information is obtained. This is apt to change as soon as I can find something to do with them, and a straightforward API that meets our specifications.

Note: Regular expressions are used under the hood to verify data. This means that email addresses and card numbers will never leave your machine.

## Keystrokes

note: These bindings asume an English keyboard layout, and might not work otherwise. If you experience an issue, first try changing them in the input gestures dialog.

* NVDA+; (semicolon): provides information based on the text that's selected
* NVDA+SHIFT+; (semicolon): provides information about text on the clipboard
* NVDA+control+; (semicolon): speaks the last reported information. Press twice to get it displayed in a browsable dialog.

## A note regarding python 3

As of NVDA version 2019.3, all add-ons must be python 3 compatible. If you are for some reason running an older version, [1.0](https://github.com/cartertemm/text_information/releases/download/1.0/textInformation-1.0.nvda-addon) is the last version usable with python 2, and dictionary definitions no longer work due to the deprecation of the Princeton Wordnetweb. Both should be considered unsupported.

## Contributing

Contributions are appreciated. You can either submit a PR, or get in contact with the following info:

twitter: @cartertemm

email: cartertemm (at) gmail (dot) com

## Licensing

This package is distributed under the terms of the GNU General Public License, version 2 or later. Please see the file COPYING.txt for further details.
