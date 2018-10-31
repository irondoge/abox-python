from sys import argv, stdout, stderr
from collections import namedtuple as nt
from requests import get, post, codes
from urllib.parse import quote, urlencode
from mpv import MPV

USER_AGENT = " ".join([
	"Mozilla/5.0 (X11; Linux x86_64)",
	"AppleWebKit/537.36 (KHTML, like Gecko)",
	"Chrome/69.0.3497.100",
	"Safari/537.36",
	"OPR/56.0.3051.52"
])

USAGE = """AcapelaBox Python

Usage: %s [options]... <text>...

  -L, --lang-list
    List all available languages

  -l <lang>, --voice-list <lang>
    List all available voices for a specified language

  -u, --url
    Print the result sound file URL
    This is the default action

  -c, --cat
    Write the result sound output to the standard output STDOUT

  -p, --play
    Play the result sound

  -d, --download
    Download the result sound file
    The file will be renamed if specified with the output option

  -v <voice>, --voice <voice>
    Specify a voice [default: antoinefromafar22k]

  -S <value>, --shaping <value>
    Specify a voice shaping value [default: 100]

  -s <value>, --speed <value>
    Specify a speech speed [default: 180]

  -m, --mp3
    Specify if MP3 codecs should be used

  -o <path>, --output <path>
    Specify an output file for download option

  -h, -help
    Show this help
"""

def ab_print_err(*args):
	print("%s failed: %s" % args, file=stderr)

AboxEndpoint = nt("AbEndpoint", [ "base", "home", "dovaas", "voice_l" ])
AboxOptionList = nt("AboxOptionList", [ "voice", "shaping", "speed", "mp3", "output" ])

AB_COOKIE = "/tmp/abox.cookie"
AB_ENDPOINT = AboxEndpoint(
	"https://acapela-box.com/AcaBox",
	"/index.php",
	"/dovaas.php",
	"/filtervoices.php"
)

def ab_cookie_fetch():
	headers = { "User-Agent": USER_AGENT }
	rep = get(AB_ENDPOINT.base + AB_ENDPOINT.home, headers=headers)
	if rep.status_code == codes.ok:
		url = "/" + "=".join(rep.headers["refresh"].split("; ")[1].split("=")[1:])
		headers["Cookie"] = "acabox=" + rep.cookies["acabox"]
		rep = get(AB_ENDPOINT.base + url, headers=headers)
		if rep.status_code == codes.ok:
			return rep.cookies["acabox"]
		else:
			ab_print_err(AB_ENDPOINT.base + url + " request", rep.reason)
	else:
		ab_print_err(AB_ENDPOINT.base + AB_ENDPOINT.home + " request", rep.reason)

def ab_cookie():
	cookie = str()
	try:
		with open(AB_COOKIE, 'r') as f:
			cookie = f.readline()
	except IOError:
		cookie = ab_cookie_fetch()
		with open(AB_COOKIE, 'w') as f:
			f.write(cookie)
	return "acabox=" + cookie

def ab_cookie_refresh():
	cookie = ab_cookie_fetch()
	with open(AB_COOKIE, 'w') as f:
		f.write(cookie)
	return "acabox=" + cookie

def ab_request_header(l, cookie):
	return {
		"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
		"Content-Length": str(l),
		"User-Agent": USER_AGENT,
		"Cookie": cookie
	}

def ab_request_data(text, voice, spd, vct, mp3):
	return {
		"text": "%s%s%s%s%s%s" % ("%5Cvct%3D", vct, "%5C%20%5Cspd%3D", spd, "%5C%20", quote(text)),
		"voice": voice,
		"listen": "1",
		"codecMP3": str(int(mp3)),
		"spd": str(spd),
		"vct": str(vct)
	}

def ab_lang_list(cookie):
	headers = { "User-Agent": USER_AGENT, "Cookie": "acabox=" + cookie }
	rep = get(AB_ENDPOINT.base + AB_ENDPOINT.home, headers=headers)
	if rep.status_code == codes.forbidden:
		ab_cookie_refresh()
		return ab_lang_list(cookie)
	if rep.status_code == codes.ok:
		pattern = "data-language="
		a = len(pattern) + 1
		lang_l = [ j[a:][:-1] for i in rep.text.split() for j in i.split(" ") if pattern in j ]
		return lang_l
	else:
		ab_print_err(AB_ENDPOINT.base + AB_ENDPOINT.home + " request", rep.reason)
		return None

def ab_voice_list(lang, cookie):
	lang = "ISO=" + lang
	headers = {
		"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
		"Content-Length": str(len(lang)),
		"User-Agent": USER_AGENT,
		"Cookie": "acabox=" + cookie
	}
	rep = post(AB_ENDPOINT.base + AB_ENDPOINT.voice_l, headers=headers, data=lang)
	if rep.status_code == codes.forbidden:
		ab_cookie_refresh()
		return ab_voice_list(lang, cookie)
	if rep.status_code == codes.ok:
		pattern = "data-id="
		a = len(pattern) + 1
		voice_l = [ j[a:][:-1] for i in rep.text.split() for j in i.split(" ") if pattern in j ]
		return voice_l
	else:
		ab_print_err(AB_ENDPOINT.base + AB_ENDPOINT.voice_l + " request", rep.reason)
		return None

def ab_cat(url, _):
	rep = get(url)
	if rep.status_code == codes.ok:
		stdout.buffer.write(rep.content)
	else:
		ab_print_err(url + " request", rep.reason)
		return False
	return True

def ab_play(url, _):
	player = MPV()
	player.play(url)
	player.wait_for_playback()
	player.terminate()
	return True

def ab_download(url, option_l):
	rep = get(url)
	if option_l.output == None:
		option_l.output = url.split("=")[1]
	if rep.status_code == codes.ok:
		with open(option_l.output, "wb") as f:
			f.write(rep.content)
		print("Downloaded to", option_l.output)
	else:
		ab_print_err(url + " request", rep.reason)
		return False
	return True

class Abox:
	OPTION_L = [
		[ "v", "voice", 1 ],
		[ "S", "shaping", 1 ],
		[ "s", "speed", 1 ],
		[ "m", "mp3", 0 ],
		[ "o", "output", 1 ],
		[ "l", "voice-list", 1 ],
		[ "L", "lang-list", 0 ],
		[ "c", "cat", 0 ],
		[ "u", "url", 0 ],
		[ "p", "play", 0 ],
		[ "d", "download", 0 ],
		[ "h", "help", 0 ]
	]

	def __init__(self, **kwargs):
		self.option_l = AboxOptionList("antoinefromafar22k", 100, 180, False, None)
		default = dict(self.option_l._asdict())
		for k, v in kwargs.items():
			if k in default:
				default[k] = int(v) if type(default[k]) is int else v
		self.option_l = AboxOptionList(**default)

	def parse(self, argc, argv):
		action_l = {}
		text = None
		default = dict(self.option_l._asdict())
		short_l, long_l, narg_l = zip(*Abox.OPTION_L)
		short_l = dict(zip(short_l, long_l))
		long_l = dict(zip(long_l, narg_l))

		def set_value(t, narg, arg):
			if narg == 0:
				return True
			if narg == 1:
				return t(arg[0])
			return arg[0:narg]

		def parse_long(op, arg):
			if op in default:
				narg = long_l[op]
				if narg <= len(arg):
					default[op] = set_value(type(default[op]), narg, arg)
					return narg
			elif op in long_l:
				narg = long_l[op]
				if narg <= len(arg):
					action_l.update({ op: set_value(str, narg, arg) })
					return narg
			return -1

		i = 1
		while i < argc:
			op, *arg = argv[i:]
			if op[0:2] == "--":
				step = parse_long(op[2:], arg)
				if step == -1 or i + step > argc:
					return {}, None
				i = i + step + 1
			elif op[0] == "-":
				opc = len(op)
				for j, opj in enumerate(op[1:], start=1):
					if opj in short_l:
						step = parse_long(short_l[opj], arg if j == opc - 1 else [])
						if step == -1 or i + step > argc:
							return {}, None
						i = i + step
					else:
						return {}, None
				i = i + 1
			else:
				text = " ".join([ op ] + arg)
				break
		self.option_l = AboxOptionList(**default)
		return action_l, text

	def query(self, text):
		op_l = [ self.option_l.voice, self.option_l.speed, self.option_l.shaping, self.option_l.mp3 ]
		data = "&".join([ "=".join(i) for i in ab_request_data(text, *op_l).items() ])
		headers = ab_request_header(len(data), ab_cookie())
		rep = post(AB_ENDPOINT.base + AB_ENDPOINT.dovaas, headers=headers, data=data)
		if rep.status_code == codes.forbidden:
			ab_cookie_refresh()
			return self.query(text)
		if rep.status_code == codes.ok:
			return rep.json()["snd_url"]
		ab_print_err(AB_ENDPOINT.base + AB_ENDPOINT.dovaas + " request", rep.reason)
		return None

	def change(self, **kwargs):
		default = dict(self.option_l._asdict())
		default.update(kwargs)
		self.option_l = AboxOptionList(**default)

def ab_usage(name, code):
	print(USAGE % name)
	return code

def main(argv):
	argc = len(argv)
	box = Abox(output="out.ogg")
	action_l, text = box.parse(argc, argv)
	if box.option_l.output == "out.ogg" and box.option_l.mp3:
		box.change(output="out.mp3")

	sound = {
		"cat": ab_cat,
		"url": lambda x, _: print(x) or True,
		"play": ab_play,
		"download": ab_download
	}
	def print_list(l):
		if l != None:
			list(map(print, l))
			return True
		return False

	ret = False
	if action_l:
		for k, v in action_l.items():
			if k in sound and text:
				ret = sound[k](box.query(text), box.option_l)
			if k == "voice-list":
				ret = print_list(ab_voice_list(v, ab_cookie()))
			elif k == "lang-list":
				ret = print_list(ab_lang_list(ab_cookie()))
			elif k == "help":
				ret = ab_usage(argv[0], True)
			if not ret:
				return ab_usage(argv[0], 1)
	elif text:
		ret = sound["url"](box.query(text), box.option_l)
	else: return ab_usage(argv[0], 1)
	if not ret: return ab_usage(argv[0], 1)
	return 0

if __name__ == "__main__":
	exit(main(argv))
