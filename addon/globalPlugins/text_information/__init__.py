#text information add-on: provides information about selected text
#Copyright (C) 2018 Carter Temm

#unreliable API key. If your serious about IP geolocale, best bet is to generate your own at <http://ipinfodb.com/api>
IPInfoDBAPIKey="32ccf9b820f3c7a8c48c62bc3586582ed3b05faedb78ef90249941fa4de2e183"
import urllib
#it might be nice to provide more log output
#from logHandler import log
import json
import ui
import api
import textInfos
import addonHandler
addonHandler.initTranslation()
import treeInterceptorHandler
import scriptHandler
import tones
import isbn
import threading
import globalPluginHandler
import re
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import imp
a, b, c=imp.find_module("bs4")
BeautifulSoup=imp.load_module("bs4", a, b, c).BeautifulSoup
sys.path.remove(sys.path[-1])

last=""
IPV4=re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
IPV6 = re.compile(r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$")
phone_number=re.compile(r"^(\+[0-9]{1,3})?\s?(\([2-9]|[2-9])(\d{2}|\d{2}\))(-|.|\s)?\d{3}(-|.|\s)?\d{4}$")
credit_cards={
	"visa":re.compile(r"^4[0-9]{12}(?:[0-9]{3})?$"),
	"MasterCard":re.compile(r"^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$"),
	"American Express":re.compile(r"^3[47][0-9]{13}$"),
	"Diners Club":re.compile(r"^3(?:0[0-5]|[68][0-9])[0-9]{11}$"),
	"discover":re.compile(r"^6(?:011|5[0-9]{2})[0-9]{12}$"),
	"JCB":re.compile(r"^(?:2131|1800|35\d{3})\d{11}$")
}
email=re.compile(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")

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
	for (type, obj) in credit_cards.items():
		if is_match(obj, number): return type
	return

def is_isbn(text):
	return isbn.isValid(str(text))

def get(addr):
	#translators: error
	error=_("error")
	try:
		response=urllib.urlopen(addr).read()
	except IOError as i:
		#translators: message spoken when we can't connect (error with connection)
		error_connection=_("error making connection")
		if str(i).find("Errno 11001")>-1:
			tones.beep(150, 200)
			ui.message(error_connection)
			return
		elif str(i).find("Errno 10060")>-1:
			tones.beep(150, 200)
			ui.message(error_connection)
			return
		elif str(i).find("Errno 10061")>-1:
			tones.beep(150, 200)
			#translators: message spoken when the connection is refused by our target
			ui.message(_("error, connection refused by target"))
			return
		else:
			tones.beep(150, 200)
			ui.message(error+": "+str(i))
			return
	except Exception as i:
		tones.beep(150, 200)
		ui.message(error+": "+str(i))
		return
	return response

def get_ip_info(ip):
	global last
	response=get("http://api.ipinfodb.com/v3/ip-city?"+urllib.urlencode({"key":IPInfoDBAPIKey,"ip":ip,"format":"json"}))
	if not response:
		return
	response=json.loads(response)
	if response["statusCode"] == "ERROR":
		tones.beep(150, 200)
		#translators: message, followed by the error, spoken when the response returned contains an error
		ui.message(_("error in response ")+response["statusMessage"])
	else:
		tones.beep(300, 200)
		last=_("country")+": "+response["countryName"]+". "+_("region")+": "+response["regionName"]+". "+_("city")+": "+response["cityName"]+". "+_("zipcode")+": "+response["zipCode"]+". "+_("longitude")+": "+response["longitude"]+". "+_("latitude")+": "+response["latitude"]+". "+_("timezone")+": "+response["timeZone"]
		ui.message(last)

def get_book_info(isbn):
	global last
	isbn=isbn.replace(" ","")
	isbn=isbn.replace("-","")
	response=get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn)
	if not response:
		return
	response=json.loads(response)
	if not response["totalItems"]:
		tones.beep(150, 200)
		#translators: message spoken when we're unable to find a book with the given ISBN
		ui.message(_("no book with that ISBN found"))
	else:
		tones.beep(300, 200)
		info=response["items"][0]["volumeInfo"]
		last=_("title")+": "+info["title"]+". "+_("author (s)")+": "+", ".join(info["authors"])+". "+_("language")+": "+info["language"]+". "+_("description")+": "+info["description"]+". "+_("maturity rating")+": "+info["maturityRating"]+". "+_("published date")+": "+info["publishedDate"]
		ui.message(last)

def get_word_info(word):
	global last
	#parsing logic based on that seen in pydictionary
	final=""
	response=get("http://wordnetweb.princeton.edu/perl/webwn?s="+word)
	if not response:
		return
	try:
		response=BeautifulSoup(response)
		types=response.findAll("h3")
		lists=response.findAll("ul")
		for a in types:
			reg=str(lists[types.index(a)])
			meanings=[]
			for x in re.findall(r"\((.*?)\)", reg):
				if "often followed by" in x:
					pass
				elif len(x) > 5 or " " in str(x):
					meanings.append(x)
			if final: final+=". "
			final+=a.text+": "+", ".join(meanings)
		tones.beep(300, 200)
		ui.message(final)
		last=final
	except IndexError:
		tones.beep(150, 200)
		#translators: message spoken when we're unable to find a definition for the given word
		ui.message(_("unable to find definition for word"))
	except Exception as e:
		ui.message(str(e))
		tones.beep(150, 200)

def word_count(string):
	if not string: return 0
	return len(string.split())

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory=_("Text Information")

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)

	def script_getClipInfo(self, gesture):
		try:
			text = api.getClipData()
		except TypeError:
			text = None
		if not text or not isinstance(text,basestring):
			#translators: message spoken when the clipboard is empty
			ui.message(_("There is no text on the clipboard"))
			return
		else:
			self.get_info(text.strip())
	script_getClipInfo.__doc__=_("speaks information of text on the clipboard")

	def script_getInfo(self, gesture):
		text=""
		obj=api.getFocusObject()
		treeInterceptor=obj.treeInterceptor
		if isinstance(treeInterceptor, treeInterceptorHandler.DocumentTreeInterceptor):
			obj=treeInterceptor
		try:
			info=obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except (RuntimeError, NotImplementedError):
			info=None
		if not info or info.isCollapsed:
			#translators: message spoken when no text is selected
			ui.message(_("select something first"))
			return
		else:
			self.get_info(info.text.strip())
	script_getInfo.__doc__=_("speaks information for currently selected text")

	def script_getLast(self, gesture):
		if last:
			#pressing once will speak info, twice will show a BrowseableDialog
			r=scriptHandler.getLastScriptRepeatCount()
			if r==0:
				ui.message(last)
			elif r==1:
				ui.browseableMessage("\n".join(last.split(". ")), "text information")
		else:
			#translators: message spoken when the user tries getting previous information but there is none
			ui.message(_("you haven't yet gotten info"))
	script_getLast.__doc__=_("reports the last retrieved information in a browseable dialog")

	def get_info(self, text):
		final=""
		w=word_count(text)
		c=is_card(text)
		if c:
			#translators: credit card
			t=_("credit card")
			final+=" ".join((c, t))
		elif isIPv4(text):
			#translators: message spoken after selecting text that contains an IP v4 address
			final+=_(" IPv4 address, retrieving information...")
			threading.Thread(target=get_ip_info,args=(text,)).start()
		elif isIPv6(text):
			#translators: message spoken after selecting text that contains an IP v6 address
			final+=_("IPv6 address, retrieving information...")
			threading.Thread(target=get_ip_info,args=(text,)).start()
		#here for completeness. We'll hopefully have something for these in the future
		elif is_phone_number(text):
			#translators: phone number
			final+=_("phone number")
		elif is_email(text):
			#translators: email
			final+=_("email")
		elif is_isbn(text):
			#translators: message spoken after text is selected that contains an ISBN
			final+=_("isbn: retrieving information...")
			threading.Thread(target=get_book_info,args=(text,)).start()
		elif w==1:
			#translators: message spoken after selecting text that contains a word (will be defined)
			final+=_("retrieving word information...")
			t=threading.Thread(target=get_word_info,args=(text,)).start()
		if not final: final+="text contains "+str(w)+(" words" if w!=1 else " word")
		ui.message(final)

	__gestures={
		"kb:NVDA+;":"getInfo",
		"kb:NVDA+shift+;":"getClipInfo",
		"kb:NVDA+control+;":"getLast",
	}