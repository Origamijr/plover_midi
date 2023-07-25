# Plover MIDI (with remaps)

Fork of plover_midi to directly integrate mappings to a keyboard. This is just so that the MIDI device is used by only one application, meaning this plugin can directly use other MIDI control signals.

Keys are mapped for a normal 24 key MIDI keyboard (I use an minilab mkII) close to the default English steno layout.

Fluidsynth must be installed, as sound is also implemented. fluidsynth.py is directly taken from the original python bindings, but slightly modified. Use your own soundfont specified in  machine.py somewhere.

Install like normal
```
{plover_console path here} -s plover_plugins install -e .
```


Original readme below
# Plover MIDI

Add support for MIDI keyboards/machines to [Plover](http://www.openstenoproject.org/).


## Release history

### 1.0.5

* fix editable installation (ensure UI files are properly generated)

### 1.0.4

* **really** disable unused and broken i18n support...

### 1.0.3

* disable unused and broken i18n support

### 1.0.2

* fix machine settings not being saved

### 1.0.0

* drop support for the Michela Keyboard machine (now part of the [Michela plugin](https://pypi.org/project/plover-michela/))

### 0.2.6

* add support for machine configuration through the Qt GUI
