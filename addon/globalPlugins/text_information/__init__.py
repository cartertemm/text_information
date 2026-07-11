# text information add-on: provides information about selected text
# Copyright (C) 2018 Carter Temm

# In python 3, urllib has been reorganized
# import urllib
from urllib.request import urlopen, Request
from urllib.parse import urlencode, urlparse, quote
from urllib.error import HTTPError, URLError

from logHandler import log
import json
import ui
import api
import textInfos
import addonHandler

addonHandler.initTranslation()
import treeInterceptorHandler
import scriptHandler
import tones
import threading
import globalPluginHandler
import re
import sys
import os
import ctypes
import tempfile
import wx
import gui

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import isbn
from bs4 import BeautifulSoup

sys.path.remove(sys.path[-1])


# taken and partially modified from http://code.activestate.com/recipes/578019
def bytes2human(n):
	symbols = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	prefix = {}
	for i, s in enumerate(symbols):
		prefix[s] = 1 << (i + 1) * 10
	for s in reversed(symbols):
		if n >= prefix[s]:
			value = float(n) / prefix[s]
			return "%.1f%s" % (value, s)
	return "%sB" % n


last = ""
# (label, url) pairs for pronunciation audio available for the word in `last`
lastAudio = []
# the word `last`/`lastAudio` refer to, when the lookup was a word definition
lastWord = ""
IPV4 = re.compile(
	r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
IPV6 = re.compile(
	r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"
)
phone_number = re.compile(
	r"^(\+[0-9]{1,3})?\s?(\([2-9]|[2-9])(\d{2}|\d{2}\))(-|.|\s)?\d{3}(-|.|\s)?\d{4}$"
)
credit_cards = {
	"visa": re.compile(r"^4[0-9]{12}(?:[0-9]{3})?$"),
	"MasterCard": re.compile(
		r"^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$"
	),
	"American Express": re.compile(r"^3[47][0-9]{13}$"),
	"Diners Club": re.compile(r"^3(?:0[0-5]|[68][0-9])[0-9]{11}$"),
	"discover": re.compile(r"^6(?:011|5[0-9]{2})[0-9]{12}$"),
	"JCB": re.compile(r"^(?:2131|1800|35\d{3})\d{11}$"),
}
email = re.compile(
	r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
)
url = re.compile(
	r"^(https?://)?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(/[^\s]*)?$"
)
URL_MAX_BYTES = 32768
CHROME_UA = (
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
	"AppleWebKit/537.36 (KHTML, like Gecko) "
	"Chrome/125.0.0.0 Safari/537.36"
)


def is_match(obj, match):
	return bool(obj.search(match))


def isIPv4(addr):
	return is_match(IPV4, addr)


def isIPv6(addr):
	return is_match(IPV6, addr)


def is_phone_number(number):
	return is_match(phone_number, number)


def is_email(address):
	return is_match(email, address)


def is_card(number):
	for type, obj in credit_cards.items():
		if is_match(obj, number):
			return type
	return


def is_isbn(text):
	return isbn.isValid(str(text))


def is_url(text):
	return is_match(url, text)


def get(addr, timeout=10):
	# translators: error
	error = _("error")
	try:
		response = urlopen(addr, timeout=timeout).read()
	except IOError as i:
		log.error(f"IOError fetching {addr}: {i}")
		# translators: message spoken when we can't connect (error with connection)
		error_connection = _("error making connection")
		if str(i).find("Errno 11001") > -1:
			tones.beep(150, 200)
			ui.message(error_connection)
			return
		elif str(i).find("Errno 10060") > -1:
			tones.beep(150, 200)
			ui.message(error_connection)
			return
		elif str(i).find("Errno 10061") > -1:
			tones.beep(150, 200)
			# translators: message spoken when the connection is refused by our target
			ui.message(_("error, connection refused by target"))
			return
		else:
			tones.beep(150, 200)
			ui.message(error + ": " + str(i))
			return
	except Exception as i:
		log.error(f"Unexpected error fetching {addr}: {i}", exc_info=True)
		tones.beep(150, 200)
		ui.message(error + ": " + str(i))
		return
	return response


def get_ip_info(ip):
	global last, lastAudio
	response = get(
		"http://ip-api.com/json/"
		+ ip
		+ "?"
		+ urlencode(
			{
				"fields": "status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,mobile,proxy"
			}
		)
	)
	if not response:
		return
	response = json.loads(response)
	if response["status"] != "success":
		tones.beep(150, 200)
		# translators: message, followed by the error, spoken when the response returned contains an error
		ui.message(_("error obtaining IP info ") + response["message"])
	else:
		tones.beep(300, 200)
		lastAudio = []
		last = (
			_("country")
			+ ": "
			+ response["country"]
			+ ". "
			+ _("region")
			+ ": "
			+ response["regionName"]
			+ ". "
			+ _("city")
			+ ": "
			+ response["city"]
			+ ". "
			+ _("zipcode")
			+ ": "
			+ response["zip"]
			+ ". "
			+ _("longitude")
			+ ": "
			+ str(response["lon"])
			+ ". "
			+ _("latitude")
			+ ": "
			+ str(response["lat"])
			+ ". "
			+ _("timezone")
			+ ": "
			+ response["timezone"]
			+ ". "
			+ _("ISP")
			+ ": "
			+ response["isp"]
		)
		if response["mobile"]:
			last += ". " + _("mobile connection")
		if response["proxy"]:
			last += ". " + _("Proxy, VPN or Tor exit address")
		ui.message(last)


def get_book_info(isbn):
	global last, lastAudio
	isbn = isbn.replace(" ", "")
	isbn = isbn.replace("-", "")
	response = get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn)
	if not response:
		return
	response = json.loads(response)
	if not response["totalItems"]:
		tones.beep(150, 200)
		# translators: message spoken when we're unable to find a book with the given ISBN
		ui.message(_("no book with that ISBN found"))
	else:
		tones.beep(300, 200)
		lastAudio = []
		info = response["items"][0]["volumeInfo"]
		last = (
			_("title")
			+ ": "
			+ info["title"]
			+ ". "
			+ _("author (s)")
			+ ": "
			+ ", ".join(info["authors"])
			+ ". "
			+ _("language")
			+ ": "
			+ info["language"]
			+ ". "
			+ _("description")
			+ ": "
			+ info["description"]
			+ ". "
			+ _("maturity rating")
			+ ": "
			+ info["maturityRating"]
			+ ". "
			+ _("published date")
			+ ": "
			+ info["publishedDate"]
		)
		ui.message(last)


def fetch_word_entry(word):
	# translators: error
	error = _("error")
	try:
		req = Request(
			"https://api.dictionaryapi.dev/api/v2/entries/en/" + quote(word),
			headers={"User-Agent": CHROME_UA},
		)
		response = urlopen(req, timeout=10).read()
	except HTTPError as h:
		if h.code == 404:
			log.debug(f"No dictionary entry for word: {word}")
			tones.beep(150, 200)
			# translators: The message spoken when a word was not found.
			ui.message(_("unable to find definition for word"))
		else:
			log.error(f"HTTPError fetching definition for {word!r}: {h}")
			tones.beep(150, 200)
			ui.message(error + ": " + str(h))
		return None
	except URLError as u:
		log.error(f"URLError fetching definition for {word!r}: {u}")
		tones.beep(150, 200)
		# translators: message spoken when we can't connect (error with connection)
		error_connection = _("error making connection")
		if str(u).find("Errno 11001") > -1 or str(u).find("Errno 10060") > -1:
			ui.message(error_connection)
		elif str(u).find("Errno 10061") > -1:
			# translators: message spoken when the connection is refused by our target
			ui.message(_("error, connection refused by target"))
		else:
			ui.message(error + ": " + str(u))
		return None
	except Exception as e:
		log.error(f"Unexpected error fetching definition for {word!r}: {e}", exc_info=True)
		tones.beep(150, 200)
		ui.message(error + ": " + str(e))
		return None
	return json.loads(response)[0]


def get_entry_phonetic(entry):
	phonetic = entry.get("phonetic")
	if phonetic:
		return phonetic
	for p in entry.get("phonetics", []):
		if p.get("text"):
			return p["text"]
	return None


# dictionaryapi.dev audio filenames end in a run of hyphen-joined 2-letter locale
# codes (e.g. "hello-uk.mp3", "data-ie-uk-us.mp3"); a leading sense number like the
# "1" in "read-1-uk.mp3" is not a locale code and is left out of the label.
AUDIO_LOCALE_TOKEN_RE = re.compile(r"^[a-z]{2}$")


def get_audio_label(audioUrl, phoneticText, usedLabels):
	stem = audioUrl.rsplit("/", 1)[-1].rsplit(".", 1)[0]
	tokens = stem.split("-")
	localeTokens = []
	while tokens and AUDIO_LOCALE_TOKEN_RE.match(tokens[-1]):
		localeTokens.insert(0, tokens.pop())
	# translators: fallback label for a pronunciation audio button when no locale
	# or phonetic transcription could be determined for it
	label = "/".join(t.upper() for t in localeTokens) if localeTokens else phoneticText or _("pronunciation")
	if label in usedLabels:
		usedLabels[label] += 1
		label = "{0} ({1})".format(label, usedLabels[label])
	else:
		usedLabels[label] = 1
	return label


def get_entry_audio(entry):
	seenUrls = set()
	usedLabels = {}
	audio = []
	for p in entry.get("phonetics", []):
		audioUrl = p.get("audio")
		# MCI ("type mpegvideo") only reliably decodes mp3; skip other formats (eg. ogg)
		if not audioUrl or not audioUrl.lower().endswith(".mp3") or audioUrl in seenUrls:
			continue
		seenUrls.add(audioUrl)
		audio.append((get_audio_label(audioUrl, p.get("text"), usedLabels), audioUrl))
	return audio


def format_word_definition(definition, index):
	text = str(index) + ". " + definition["definition"]
	if definition.get("example"):
		# translators: label for an example sentence using a word
		text += ". " + _("example") + ": " + definition["example"]
	if definition.get("synonyms"):
		# translators: label for a list of synonyms
		text += ". " + _("synonyms") + ": " + ", ".join(definition["synonyms"])
	if definition.get("antonyms"):
		# translators: label for a list of antonyms
		text += ". " + _("antonyms") + ": " + ", ".join(definition["antonyms"])
	return text


def format_word_meaning(meaning):
	definitions = [
		format_word_definition(definition, index)
		for index, definition in enumerate(meaning.get("definitions", []), 1)
	]
	if meaning.get("synonyms"):
		definitions.append(_("synonyms") + ": " + ", ".join(meaning["synonyms"]))
	if meaning.get("antonyms"):
		definitions.append(_("antonyms") + ": " + ", ".join(meaning["antonyms"]))
	return meaning["partOfSpeech"] + ": " + " ".join(definitions)


def get_word_info(word):
	global last, lastAudio, lastWord
	entry = fetch_word_entry(word)
	if entry is None:
		return
	fields = []
	phonetic = get_entry_phonetic(entry)
	if phonetic:
		# translators: label for the phonetic pronunciation of a word
		fields.append(_("pronunciation") + ": " + phonetic)
	fields.extend(format_word_meaning(meaning) for meaning in entry.get("meanings", []))
	if not fields:
		tones.beep(150, 200)
		ui.message(_("unable to find definition for word"))
		return
	tones.beep(300, 200)
	lastAudio = get_entry_audio(entry)
	lastWord = word
	last = ". ".join(fields)
	ui.message(last)


def get_url_info(addr, timeout=10):
	# We violate DRY and implement parts of `get()` here, because we have to retrieve the headers and set a common user agent
	# Ugly, but passable under the circumstances
	global last, lastAudio
	error = _("error")
	if not addr.startswith(("http://", "https://")):
		addr = "https://" + addr
	original_domain = urlparse(addr).netloc
	try:
		req = Request(
			addr,
			headers={
				"User-Agent": CHROME_UA,
				"Accept-Encoding": "identity",
			},
		)
		response = urlopen(req, timeout=timeout)
		data = response.read(URL_MAX_BYTES)
	except IOError as i:
		log.error(f"IOError fetching URL {addr!r}: {i}")
		tones.beep(150, 200)
		if str(i).find("Errno 11001") > -1 or str(i).find("Errno 10060") > -1:
			ui.message(_("error making connection"))
		elif str(i).find("Errno 10061") > -1:
			ui.message(_("error, connection refused by target"))
		else:
			ui.message(error + ": " + str(i))
		return
	except Exception as i:
		log.error(f"Unexpected error fetching URL {addr!r}: {i}", exc_info=True)
		tones.beep(150, 200)
		ui.message(error + ": " + str(i))
		return
	soup = BeautifulSoup(data, "html.parser")
	title = soup.title.string.strip() if soup.title and soup.title.string else None
	if not title:
		tones.beep(150, 200)
		# translators: message spoken when the page title cannot be retrieved
		ui.message(_("unable to retrieve page title"))
		return
	fields = []
	fields.append(_("title") + ": " + title)
	desc_tag = soup.find("meta", attrs={"name": "description"})
	if desc_tag:
		desc = desc_tag.get("content", "").strip()
		if desc:
			# translators: label for the page description field in URL output
			fields.append(_("description") + ": " + desc)
	content_length = response.headers.get("Content-Length")
	if content_length:
		try:
			# translators: label for the content length field in URL output
			fields.append(_("content length") + ": " + bytes2human(int(content_length)))
		except ValueError:
			log.debug(f"Non-numeric Content-Length header for {addr!r}: {content_length!r}")
	final_domain = urlparse(response.geturl()).netloc
	if final_domain and final_domain != original_domain:
		# translators: label spoken when a URL redirects to a different domain
		fields.append(_("redirects to") + ": " + final_domain)
	tones.beep(300, 200)
	lastAudio = []
	last = ". ".join(fields)
	ui.message(last)


def word_count(string):
	if not string:
		return 0
	return len(string.split())


_audioPlaybackLock = threading.Lock()
AUDIO_MCI_ALIAS = "textInformationPronunciation"


def play_audio_url(audioUrl):
	try:
		req = Request(audioUrl, headers={"User-Agent": CHROME_UA})
		data = urlopen(req, timeout=10).read()
	except Exception as e:
		log.error(f"Error downloading pronunciation audio from {audioUrl!r}: {e}", exc_info=True)
		tones.beep(150, 200)
		return
	tempPath = os.path.join(tempfile.gettempdir(), "text_information_pronunciation.mp3")
	with _audioPlaybackLock:
		try:
			winmm = ctypes.windll.winmm
			# close any previous playback first, otherwise it still holds tempPath open and the write below fails
			winmm.mciSendStringW("close " + AUDIO_MCI_ALIAS, None, 0, None)
			with open(tempPath, "wb") as f:
				f.write(data)
			winmm.mciSendStringW(
				'open "{0}" type mpegvideo alias {1}'.format(tempPath, AUDIO_MCI_ALIAS), None, 0, None
			)
			winmm.mciSendStringW("play " + AUDIO_MCI_ALIAS, None, 0, None)
		except Exception as e:
			log.error(f"Error playing pronunciation audio from {audioUrl!r}: {e}", exc_info=True)
			tones.beep(150, 200)


def make_audio_button_handler(audioUrl):
	def handler(event):
		threading.Thread(target=play_audio_url, args=(audioUrl,), daemon=True).start()

	return handler


class WordAudioDialog(wx.Dialog):
	def __init__(self, parent, title, message, audioEntries):
		super().__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		sizer = wx.BoxSizer(wx.VERTICAL)
		textCtrl = wx.TextCtrl(self, value=message, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
		sizer.Add(textCtrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
		for label, audioUrl in audioEntries:
			# translators: label for a button that plays a pronunciation audio clip, {0} is the locale/variant
			button = wx.Button(self, label=_("Play {0}").format(label))
			button.Bind(wx.EVT_BUTTON, make_audio_button_handler(audioUrl))
			sizer.Add(button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
		closeButton = wx.Button(self, wx.ID_CLOSE)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
		sizer.Add(closeButton, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
		self.SetSizer(sizer)
		self.SetSize((500, 400))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		textCtrl.SetFocus()

	def onClose(self, event):
		gui.mainFrame.postPopup()
		self.Destroy()


def show_audio_browseable_message(message, title, audioEntries):
	dialog = WordAudioDialog(gui.mainFrame, title, message, audioEntries)
	gui.mainFrame.prePopup()
	dialog.Show()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = _("Text Information")

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)

	def script_getClipInfo(self, gesture):
		try:
			text = api.getClipData()
		except TypeError as e:
			log.debug(f"Unable to get clipboard data: {e}")
			text = None
		if not text or not isinstance(text, str):
			# translators: message spoken when the clipboard is empty
			ui.message(_("There is no text on the clipboard"))
			return
		else:
			self.get_info(text.strip())

	script_getClipInfo.__doc__ = _("speaks information of text on the clipboard")

	def script_getInfo(self, gesture):
		obj = api.getFocusObject()
		treeInterceptor = obj.treeInterceptor
		if isinstance(treeInterceptor, treeInterceptorHandler.DocumentTreeInterceptor):
			obj = treeInterceptor
		try:
			info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except (RuntimeError, NotImplementedError) as e:
			log.debug(f"makeTextInfo failed on {obj!r}: {e}")
			info = None
		if not info or info.isCollapsed:
			# No text selected, try grabbing word under review cursor
			info = api.getReviewPosition().copy()
			try:
				info.expand(textInfos.UNIT_WORD)
			except AttributeError as e:  # Nothing more we can do
				log.debug(f"Unable to expand review position to word: {e}")
				# translators: message spoken when no text is selected or focused
				ui.message(_("select or focus something first"))
				return
		self.get_info(info.text.strip())

	script_getInfo.__doc__ = _("speaks information for currently selected text")

	def script_getLast(self, gesture):
		if last:
			# pressing once will speak info, twice will show a BrowseableDialog
			r = scriptHandler.getLastScriptRepeatCount()
			if r == 0:
				ui.message(last)
			elif r == 1:
				if lastAudio:
					# translators: title of the dialog showing a word's definition and pronunciation audio buttons
					title = _("Definition for {0}").format(lastWord)
					show_audio_browseable_message("\n".join(last.split(". ")), title, lastAudio)
				else:
					ui.browseableMessage("\n".join(last.split(". ")), "text information")
		else:
			# translators: message spoken when the user tries getting previous information but there is none
			ui.message(_("you haven't yet gotten info"))

	script_getLast.__doc__ = _(
		"reports the last retrieved information in a browseable dialog"
	)

	def get_info(self, text):
		final = ""
		w = word_count(text)
		c = is_card(text)
		if c:
			# translators: credit card
			t = _("credit card")
			final += " ".join((c, t))
		elif isIPv4(text):
			# translators: message spoken after selecting text that contains an IP v4 address
			final += _(" IPv4 address, retrieving information...")
			threading.Thread(target=get_ip_info, args=(text,)).start()
		elif isIPv6(text):
			# translators: message spoken after selecting text that contains an IP v6 address
			final += _("IPv6 address, retrieving information...")
			threading.Thread(target=get_ip_info, args=(text,)).start()
		# here for completeness. We'll hopefully have something for these in the future
		elif is_phone_number(text):
			# translators: phone number
			final += _("phone number")
		elif is_email(text):
			# translators: email
			final += _("email")
		elif is_isbn(text):
			# translators: message spoken after text is selected that contains an ISBN
			final += _("isbn: retrieving information...")
			threading.Thread(target=get_book_info, args=(text,)).start()
		# Deliberately placed below the IP detection, since many IP v4 addresses would be caught by our URL regexp
		elif is_url(text):
			# translators: message spoken after selecting text that contains a URL
			final += _("URL, retrieving page information...")
			threading.Thread(target=get_url_info, args=(text,)).start()
		elif w == 1:
			# translators: message spoken after selecting text that contains a word (will be defined)
			final += _("retrieving word information...")
			t = threading.Thread(target=get_word_info, args=(text,)).start()
		if not final:
			final += "text contains " + str(w) + (" words" if w != 1 else " word")
		ui.message(final)

	__gestures = {
		"kb:NVDA+;": "getInfo",
		"kb:NVDA+shift+;": "getClipInfo",
		"kb:NVDA+control+;": "getLast",
	}
