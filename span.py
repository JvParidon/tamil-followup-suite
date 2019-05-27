import audio
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import core, visual, event
import random
import os
import csv
from test_tools import pause, get_pp_info


class Experiment(object):


    def __init__(self, mode, pp_info, fps=60.0):
        self.mode = mode
        self.pp_info = pp_info
        self.fps = fps
        # set up file paths, etc.
        self.stimuli_folder = 'stimuli/span/' + mode + '/'
        self.instructions_folder = 'instructions/span/'
        self.trials_fname = 'trial_structure/span/' + mode + '.tsv'
        self.log_prefix = 'logs/span/' + mode + '/' + pp_info['literate'] + '_' + pp_info['number'] + '_'


    def run(self):
        # set up presentation window color, and size
        bgcolor = 'black'
        txtcolor = 'white'
        self.win = visual.Window(fullscr=True, color=bgcolor)
        #self.win = visual.Window((1200, 900), color=bgcolor)  # temporary presentation window setup, exchange for line above when running actual experiment
        self.text = visual.TextStim(self.win, color=txtcolor)

        with open(self.trials_fname, 'rU') as trial_file:
            # read trial structure
            trials = list(csv.DictReader(trial_file, delimiter='\t'))

            # preload stimuli
            stimuli = [audio.read(self.stimuli_folder + trial['stimulus']) for trial in trials]

            recordings = []

            self.text.text = '||'
            self.text.draw()
            self.win.flip()
            audio.play(audio.read(self.instructions_folder + self.mode + '.wav'), wait=True)
            key = event.waitKeys(keyList=['return'])
            self.win.flip()

            for stimulus in stimuli:
                self.text.text = '+'
                self.text.draw()
                self.win.flip()
                audio.play(stimulus, wait=True)
                self.text.text = '-'
                self.text.draw()
                self.win.flip()
                recordings += [audio.record((len(stimulus) / 44100.0) + 1, wait=True)]
                keys = event.getKeys(['escape'])
                if 'escape' in keys:
                    break

            for i in range(len(recordings)):
                audio.write(self.log_prefix + trials[i]['stimulus'], recordings[i])

            self.win.close()


if __name__ == '__main__':
    pp_info = get_pp_info()
    for mode in ['forward', 'backward']:
        pause()
        Experiment(mode, pp_info).run()
