# definitions.py
# Dictionary word definitions and pronunciation audio playback for the text information add-on.
# Uses the Free Dictionary API (https://dictionaryapi.dev/).
# Copyright (C) 2018 Carter Temm

from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import HTTPError, URLError

from logHandler import log
import json
import ui
import tones
import threading
import queue
import re
import os
import ctypes
import tempfile
import glob
import wx
import gui

# Duplicated from __init__.py's CHROME_UA to avoid a circular import between the two modules.
# dictionaryapi.dev returns 403 without a browser-like User-Agent
CHROME_UA = (
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
	"AppleWebKit/537.36 (KHTML, like Gecko) "
	"Chrome/125.0.0.0 Safari/537.36"
)


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


# dictionaryapi.dev audio filenames end in hyphen-joined 2-letter locale
# codes (e.g. "hello-uk.mp3", "data-ie-uk-us.mp3");
# a leading number like the "1" in "read-1-uk.mp3" is not a locale code and is left out of the label.
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
		# MCI ("type mpegvideo") only reliably decodes mp3. Skip other formats (eg. ogg)
		# I have never seen anything other than an mp3 from this API, so continuing should be fine
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


# The MCI "mpegvideo" driver ties a device's teardown to the thread that opened it, so all
# open/play/close calls must happen from one persistent thread. A new thread per play would permanently lock the temp file as well.
AUDIO_MCI_ALIAS = "textInformationAudioPlayer"
AUDIO_TEMP_FILE_GLOB = os.path.join(tempfile.gettempdir(), "text_information_pronunciation*.mp3")
_audioQueue = queue.Queue()
# sentinel telling the worker to stop playback and clean up, without shutting the thread down
_AUDIO_STOP = object()


def _remove_audio_temp_files():
	for path in glob.glob(AUDIO_TEMP_FILE_GLOB):
		try:
			os.remove(path)
		except OSError as e:
			log.debug(f"Unable to remove pronunciation temp file {path!r}: {e}")


def _audio_worker():
	winmm = ctypes.windll.winmm
	counter = 0
	while True:
		audioUrl = _audioQueue.get()
		if audioUrl is None or audioUrl is _AUDIO_STOP:
			winmm.mciSendStringW("close " + AUDIO_MCI_ALIAS, None, 0, None)
			_remove_audio_temp_files()
			if audioUrl is None:
				return
			continue
		try:
			req = Request(audioUrl, headers={"User-Agent": CHROME_UA})
			data = urlopen(req, timeout=10).read()
		except Exception as e:
			log.error(f"Error downloading pronunciation audio from {audioUrl!r}: {e}", exc_info=True)
			tones.beep(150, 200)
			continue
		winmm.mciSendStringW("close " + AUDIO_MCI_ALIAS, None, 0, None)
		_remove_audio_temp_files()
		counter += 1
		tempPath = os.path.join(tempfile.gettempdir(), "text_information_pronunciation_{0}.mp3".format(counter))
		try:
			with open(tempPath, "wb") as f:
				f.write(data)
			winmm.mciSendStringW(
				'open "{0}" type mpegvideo alias {1}'.format(tempPath, AUDIO_MCI_ALIAS), None, 0, None
			)
			winmm.mciSendStringW("play " + AUDIO_MCI_ALIAS, None, 0, None)
		except Exception as e:
			log.error(f"Error playing pronunciation audio from {audioUrl!r}: {e}", exc_info=True)
			tones.beep(150, 200)


_audioThread = threading.Thread(target=_audio_worker, daemon=True)
_audioThread.start()


def play_audio_url(audioUrl):
	_audioQueue.put(audioUrl)


def stop_audio_playback():
	_audioQueue.put(_AUDIO_STOP)


def shutdown_audio_worker():
	_audioQueue.put(None)


def make_audio_button_handler(audioUrl):
	def handler(event):
		play_audio_url(audioUrl)
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
		self.SetEscapeId(wx.ID_CLOSE)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		textCtrl.SetFocus()

	def onClose(self, event):
		stop_audio_playback()
		gui.mainFrame.postPopup()
		self.Destroy()


def show_audio_browseable_message(message, title, audioEntries):
	dialog = WordAudioDialog(gui.mainFrame, title, message, audioEntries)
	gui.mainFrame.prePopup()
	dialog.Show()
