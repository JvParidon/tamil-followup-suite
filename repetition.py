import audio
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import core, visual, event
from test_tools import pause, get_pp_info

# experiment routines for presenting word reading stimuli and recording spoken responses

class Experiment(object):


    def __init__(self, mode, pp_info, fps=60.0):
        self.mode = mode
        self.pp_info = pp_info
        self.fps = fps
        # set up file paths, etc.
        self.instructions_folder = 'instructions/repetition/'
        self.stimuli_prefix = 'stimuli/repetition/' + mode + '/' + mode
        self.log_prefix = 'logs/repetition/' + mode + '/' + mode + '_' + pp_info['literate'] + '_' + pp_info['number'] + '_'


    def run(self):
        # set up presentation window color, and size
        bgcolor = 'black'
        txtcolor = 'white'
        self.win = visual.Window(fullscr=True, color=bgcolor)
        #self.win = visual.Window((1200, 900), color=bgcolor)  # temporary presentation window setup, exchange for line above when running actual experiment
        self.text = visual.TextStim(self.win, color=txtcolor)

        words = [audio.read(self.stimuli_prefix + str(i + 1) + '.wav') for i in range(24)]
        recordings = []

        self.text.text = '||'
        self.text.draw()
        self.win.flip()
        audio.play(audio.read(self.instructions_folder + self.mode + '.wav'), wait=True)
        key = event.waitKeys(keyList=['return'])

        for word in words:
            self.text.text = '+'
            self.text.draw()
            self.win.flip()
            audio.play(word, wait=True)
            self.text.text = '-'
            self.text.draw()
            self.win.flip()
            recordings += [audio.record(((len(word) / 44100) + 1), wait=True)]

        for i in range(len(words)):
            audio.write(self.log_prefix + str(i + 1) + '.wav', recordings[i])

        self.win.close()


if __name__ == '__main__':
    pp_info = get_pp_info()
    for mode in ['word', 'pseudoword']:
        pause()
        Experiment(mode, pp_info).run()
