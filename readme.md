# Text Information

This add-on allows for getting information based on selected text. Simply select something, then use NVDA+; (semicolon). Alternativly you can use NVDA+shift+; (semicolon) to get info about the clipboard text. You should, hopefully, be presented with something that fits the context.

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