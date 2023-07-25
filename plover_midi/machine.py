
from fnmatch import fnmatchcase

from rtmidi import MidiIn
import plover_midi.fluidsynth as fluidsynth
import time

from plover.machine.base import ThreadedStenotypeBase
from plover import log

BASE_NOTES = 'C C# D D# E F F# G G# A A# B'.split()
NUM_OCTAVES = 10

KEYMAPS = {
    'C#2': '#',
    'C2': 'S-',
    'D#2': 'T-',
    'E2': 'K-',
    'D2': 'T-',
    'F#2': 'P-',
    'F2': 'W-',
    'G#2': 'H-',
    'G2': 'R-',
    'A2': 'A-',
    'B2': 'O-',
    'C#3': '*',
    'A#2': '-P',
    'C3': '-E',
    'D3': '-U',
    'D#3': '-F',
    'E3': '-R',
    'F#3': '-P',
    'F3': '-B',
    'G#3': '-L',
    'G3': '-G',
    'B3': '-T',
    'A3': '-S',
    'C4': '-D',
    'A#3': '-Z'
}


class MidiStenotype(ThreadedStenotypeBase):

    PORT = '*'

    KEYS_LAYOUT = '''
        C2  C#2  D2  D#2  E2  F2  F#2  G2  G#2  A2  A#2  B2
        C3  C#3  D3  D#3  E3  F3  F#3  G3  G#3  A3  A#3  B3
        C4
    '''

    def __init__(self, params):
        super().__init__()
        self._params = params
        self._midi = MidiIn()
        self._midi.set_callback(self._on_message, None)
        self._note_to_key = []
        for octave in range(10):
            for note in 'C C# D D# E F F# G G# A A# B'.split():
                self._note_to_key.append(note + str(octave - 2))
        self._pressed = set()
        self._stroke = set()
        self.fs = fluidsynth.Synth()
        self.fs.start()
        sfid = self.fs.sfload("C:/Users/origa/Desktop/python_stuff/plover_midi/plover_midi/Touhou.sf2")
        self.fs.program_select(0, sfid, 0, 0)
        self.volume = 1

    def run(self):
        log.info('available ports: %s', ', '.join(self._midi.get_ports()))
        port_glob = self._params['port'].lower()
        for port, port_name in enumerate(self._midi.get_ports()):
            if fnmatchcase(port_name.lower(), port_glob):
                break
        else:
            log.warning('no port found, matching: %s', port_glob)
            self._error()
            return
        log.info('opening port: %s', port_name)
        try:
            self._midi.open_port(port)
        except:
            log.warning('error opening port: %s', port_name, exc_info=True)
            self._error()
            return
        self._ready()
        self.finished.wait()
        self._midi.close_port()

    def _on_message(self, params, data):
        message, delta = params
        log.debug('message: [%#x ,%d, %d]', *message)
        if message[0] == 0xB0 and message[1] == 75:
            self.fs.cc(0, 7, message[2])
            return
        if message[0] not in (0x80, 0x90):
            return
        # Note: some keyboards indicate key release by sending a note on
        # message with a velocity of zero (instead of a note off message).
        pressed = message[0] == 0x90 and message[2] != 0
        key = self._note_to_key[message[1]]
        log.debug('%s %s', key, 'pressed' if pressed else 'released')
        if pressed:
            self._pressed.add(key)
            self._stroke.add(key)
            self.fs.noteon(0, message[1], int(self.volume*message[2]))
            return
        else:
            self.fs.noteoff(0, message[1])
        self._pressed.discard(key)
        if self._pressed:
            return
        stroke = self._stroke
        self._stroke = set()
        #steno_keys = self.keymap.keys_to_actions(stroke)
        if 48 <= message[1] <= 72:
            steno_keys = [KEYMAPS[key] for key in stroke]
            if not steno_keys:
                return
            log.debug('stroke: %r', steno_keys)
            self._notify(steno_keys)

    @classmethod
    def get_option_info(cls):
        """Get the default options for this machine."""
        return {
            'port': (cls.PORT, str),
        }


def test_machine(port=None):
    import sys
    import time
    if port is None:
        port = sys.argv[1] if len(sys.argv) > 1 else '*'
    log.set_level(log.DEBUG)
    machine = MidiStenotype({'port': port})
    machine.start_capture()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        machine.stop_capture()


if __name__ == '__main__':
    test_machine()
