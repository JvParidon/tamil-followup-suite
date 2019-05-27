import csv
import audio
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import core, visual, event
from test_tools import pause, get_pp_info


class Experiment(object):


    def __init__(self, subset, pp_info, fps=60.0):
        self.pp_info = pp_info
        self.fps = fps
        # set up file paths, etc.
        self.trials_fname = 'trial_structure/ravens/' + subset + '.tsv'
        self.log_fname = 'logs/ravens/' + subset + '_' + pp_info['literate'] + '_' + pp_info['number'] + '.tsv'
        self.stimuli_folder = 'stimuli/ravens_color/'
        self.instructions_folder = 'instructions/ravens/'


    def run(self):
        # set up presentation window color, and size
        bgcolor = 'white'
        txtcolor = 'black'
        self.win = visual.Window(fullscr=True, color=bgcolor)
        #self.win = visual.Window((1200, 900), color=bgcolor)  # temporary presentation window setup, exchange for line above when running actual experiment

        # set up timing related stuff
        self.frame_dur = 1.0 / self.fps
        self.clock = core.Clock()  # trial timer
        self.expclock = core.Clock()  # whole experiment timer

        # various stimulus presentation boxes for text and images
        self.title = visual.TextStim(self.win, color=txtcolor)
        self.title.wrapWidth = 1.5
        #self.title.setAutoLog()  # is this still necessary?
        self.image = visual.ImageStim(self.win, size=(.6, 1))

        # actually run the experiment routines
        self.skipped = []
        with open(self.trials_fname, 'rU') as trial_file, open(self.log_fname, 'w', newline='') as log_file:
            # read trial structure
            trials = csv.DictReader(trial_file, delimiter='\t')

            # set up log file
            log_fields = trials.fieldnames + ['keypress', 'RT', 'ACC', 't', 'skipped'] + list(self.pp_info.keys())
            log = csv.DictWriter(log_file, fieldnames=log_fields, delimiter='\t')
            log.writeheader()

            # present the trials
            for trial in trials:
                trial.update(self.pp_info)
                self.clock.reset()  # reset the trial clock
                trial = self.present_trial(trial)  # present the trial

                # check if the trial has been skipped, if so, put it in the repetition queue
                if trial['keypress'] == 'right':
                    self.skipped.append(trial)

                log.writerow(trial)  # log trial data

                # check if the 20 minutes alotted for the Raven's have expired
                #if self.expclock.getTime() > 20 * 60.0:
                #    core.quit()

            # run the skipped trials again
            while len(self.skipped) > 0:
                self.clock.reset()  # reset the trial clock
                trial = self.present_trial(self.skipped[0])  # present first trial in the repetition queue

                # requeue trial if it's skipped again
                if trial['keypress'] == 'right':
                    self.skipped.append(trial)

                log.writerow(trial)  # log trial data

                # check if the 20 minutes alotted for the Raven's have expired
                #if self.expclock.getTime() > 20 * 60.0:
                #    core.quit()

                self.skipped.pop(0)  # remove repeated trial from the repetition queue
                
            self.win.close()


    # select the appriopriate trial subroutine
    def present_trial(self, trial):
        type = trial['type']
        if type == 'message':
            trial = self.message_trial(trial)
        elif type == 'practice':
            trial = self.practice_trial(trial)
        elif type == 'test':
            trial = self.test_trial(trial)
        else:
            # unknown trial type, return some kind of error?
            print('ERROR: unknown trial type')

        # log experiment timer and return trial data
        trial['t'] = self.expclock.getTime()
        return trial


    def message_trial(self, trial):
        # present instruction trial
        self.title.text = trial['title']
        self.title.draw()
        self.win.callOnFlip(self.clock.reset)
        self.win.flip()
        audio.play(audio.read(self.instructions_folder + 'ravens.wav'), wait=True)
        keys = event.waitKeys(keyList=['escape'] + trial['keyboard'].split(','), timeStamped=self.clock)
        trial['keypress'], trial['RT'] = keys[0]
        if trial['keypress'] == 'escape':
            core.quit()
        self.expclock.reset()
        return trial


    def practice_trial(self, trial):
        # present practice trial
        self.image.image = self.stimuli_folder + trial['picture']
        self.image.draw()
        self.win.callOnFlip(self.clock.reset)
        self.win.flip()
        keys = event.waitKeys(keyList=['escape'] + trial['keyboard'].split(','), timeStamped=self.clock)
        trial['keypress'], trial['RT'] = keys[0]
        if trial['keypress'] == 'escape':
            core.quit()
        if trial['keypress'] == trial['key']:
            trial['ACC'] = 1
        else:
            trial['ACC'] = 0
        return trial


    def test_trial(self, trial):
        # present instruction trial
        self.image.image = self.stimuli_folder + trial['picture']
        self.image.draw()
        self.win.callOnFlip(self.clock.reset)
        self.win.flip()
        keys = event.waitKeys(keyList=['escape', 'right'] + trial['keyboard'].split(','), timeStamped=self.clock)
        trial['keypress'], trial['RT'] = keys[0]
        if trial['keypress'] == 'escape':
            core.quit()
        if trial['keypress'] == trial['key']:
            trial['ACC'] = 1
        else:
            trial['ACC'] = 0
        return trial


if __name__ == '__main__':
    pp_info = get_pp_info()
    for mode in ['a', 'b']:
        pause()
        Experiment(mode, pp_info).run()
