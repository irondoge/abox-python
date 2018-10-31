Acapela-Box Python
======
**Acapela-Box Python** is a python module implementation of the non-official API to [acapela-box.com](https://acapela-box.com/AcaBox/index.php).

## Code Example
```python
import abox

box = abox.Abox(output="hello.ogg", voice="willbadguy22k")
url = box.query("hello, world")
ret = abox.ab_download(url, box.option_l)
if not ret:
	print("Aborting")
	exit(1);
```
```
$ python test.py
Downloaded to hello.ogg
$ python -m abox -dmo hello.mp3 --voice willbadguy22k "hello, world"
Downloaded to hello.mp3
```

## Download

* [Version 1.0]()
* Bash implementation - see [abox-bash]()

## Installation
Installation through [pip](https://pip.pypa.io/en/stable/) is planned for future releases.

#### Prerequisities
The module is entirely wrtitten in pure python using the python standard library except for the playback feature. The [mpv](https://github.com/jaseg/python-mpv) package is required to make this feature to work.

#### Install
For this current release, just download the module and add it to the python [module search path](https://docs.python.org/3/tutorial/modules.html#the-module-search-path).

## Usage
```
AcapelaBox Python

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
```

## API Reference
Comment will be added to the code for future releases, before that just refer to the `main()` function in the module file.

## Contributors
#### Contributors on GitHub
* [Contributors](https://github.com/irondoge/abox-python/graphs/contributors)

#### Third party libraries
* see [python-mpv](https://github.com/jaseg/python-mpv) package

## License
License will be available for future releases.
