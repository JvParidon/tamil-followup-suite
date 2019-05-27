import csv
import os
import random
import audio
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import core, visual, event
from test_tools import pause, get_pp_info


class Experiment(object):


    def __init__(self, mode, pp_info, fps=60.0):
        self.pp_info = pp_info
        self.fps = fps
        # set up file paths, etc.
        self.trials_fname = 'trial_structure/language_music/' + mode + '.tsv'
        self.log_prefix = 'logs/language_music/' + mode + '/' + pp_info['literate'] + '_' + pp_info['number']
        self.log_fname = self.log_prefix + '.tsv'
        self.stimuli_folder = 'stimuli/language_music/' + mode + '/'
        self.instructions_folder = 'instructions/language_music/'


    def run(self):
        # set up presentation window color, and size
        bgcolor = 'black'
        txtcolor = 'white'
        #self.win = visual.Window(fullscr=True, color=bgcolor)
        self.win = visual.Window((1200, 900), color=bgcolor)  # temporary presentation window setup, exchange for line above when running actual experiment

        # set up timing related stuff
        self.frame_dur = 1.0 / self.fps
        self.clock = core.Clock()  # trial timer
        self.expclock = core.Clock()  # whole experiment timer
        # inter trial interval setup
        self.isi = core.StaticPeriod()
        self.isi.start(.5)

        # various stimulus presentation boxes for text and images
        self.text = visual.TextStim(self.win, color=txtcolor)
        self.message = visual.TextStim(self.win, color=txtcolor)
        self.message.wrapWidth = 1.5
        self.title = visual.TextStim(self.win, pos=(0, .8), color=txtcolor)
        self.title.wrapWidth = 1.5
        self.image = visual.ImageStim(self.win)

        # actually run the experiment routines
        with open(self.trials_fname, 'rU') as trial_file, open(self.log_fname, 'w', newline='') as log_file:
            # read trial structure
            trials = csv.DictReader(trial_file, delimiter='\t')

            # set up log file
            log_fields = trials.fieldnames + ['keypress', 'RT', 'ACC', 't'] + list(self.pp_info.keys())
            log = csv.DictWriter(log_file, fieldnames=log_fields, delimiter='\t')
            log.writeheader()

            # counterbalance order of addition and deletion blocks across participants
            trials = list(trials)
            if (int(pp_info['number']) % 4) > 2:
                for i in range(len(trials)):
                    if trials[i]['condition'] == 'addition':
                        trials[i]['block'] = str(int(trials[i]['block']) - 2)
                    elif trials[i]['condition'] == 'deletion':
                        trials[i]['block'] = str(int(trials[i]['block']) + 2)

            # preload block and instructions
            blocks = {}
            self.instructions = {}
            self.questions = {}
            for trial in trials:
                trial.update(self.pp_info)
                if (trial['Instruction'] != '') and (trial['Instruction'] not in self.instructions.keys()):
                    self.instructions[trial['Instruction']] = audio.read(self.instructions_folder + trial['Instruction'])
                if (trial['Question'] != '') and (trial['Question'] not in self.questions.keys()):
                    self.questions[trial['Question']] = audio.read(os.path.join(self.stimuli_folder, trial['condition'], trial['Question']))
                if trial['block'] not in blocks.keys():
                    blocks[trial['block']] = [trial]
                else:
                    blocks[trial['block']].append(trial)

            for i in range(5, 0, -1):
                self.text.text = '+' * (2 * i - 1)
                self.text.draw()
                self.win.flip()
                core.wait(1)

            # present the trials
            random.seed(self.pp_info['number'])
            for block_number in sorted(blocks.keys()):
                trials = blocks[block_number]
                if trials[0]['randomize'] == 'yes':
                    random.shuffle(trials)
                for trial in trials:
                    self.clock.reset()  # reset trial clock
                    trial = self.present_trial(trial)  # present the trial
                    log.writerow(trial)  # log the trial data

            self.win.close()


    # select the appriopriate trial subroutine
    def present_trial(self, trial):
        type = trial['type']
        if type == 'instructions':
            trial = self.instruction_trial(trial)
        elif type == 'learn':
            trial = self.learn_trial(trial)
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


    def instruction_trial(self, trial):
        # present instruction trial
        self.text.text = '+'
        self.text.draw()
        self.win.callOnFlip(self.clock.reset)
        self.isi.complete()
        self.win.flip()
        if trial['Instruction'] != '':
            self.text.text = '||'
            self.text.draw()
            self.win.callOnFlip(self.clock.reset)
            audio.play(self.instructions[trial['Instruction']], wait=True)
            self.win.flip()
        keys = event.waitKeys(keyList=['escape'] + trial['keyboard'].split(' '), timeStamped=self.clock)
        trial['keypress'], trial['RT'] = keys[0]
        if trial['keypress'] == 'escape':
            core.quit()
        self.win.callOnFlip(self.isi.start, float(trial['ITI']) / 1000 - self.frame_dur)
        # flip buffer again and start ISI timer
        self.win.flip()
        return trial


    def learn_trial(self, trial):
        # present learn trial
        # set up trial display
        #self.win.callOnFlip(self.clock.reset)
        # run out ISI clock
        self.isi.complete()
        # flip frame buffer and reset trial clock
        self.win.flip()
        # wait for prespecified duration while stimulus is on screen
        core.wait(float(trial['presTime']) / 1000 - self.frame_dur)
        self.win.callOnFlip(self.isi.start, float(trial['ITI']) / 1000 - self.frame_dur)
        # flip buffer again and start ISI timer
        self.win.flip()
        return trial


    def practice_trial(self, trial):
        # present practice trial
        self.text.text = '+'
        #self.text.text = trial['Question']
        self.text.draw()
        self.win.callOnFlip(self.clock.reset)
        self.isi.complete()
        self.win.flip()
        if trial['Question'] != '':
            self.text.text = '-'
            self.text.draw()
            self.win.callOnFlip(self.clock.reset)
            audio.play(self.questions[trial['Question']], wait=True)
            audio.play(self.questions[trial['Question']], wait=True)
            self.win.flip()
        keys = event.waitKeys(keyList=['escape'] + trial['keyboard'].split(' '), timeStamped=self.clock)
        trial['keypress'], trial['RT'] = keys[0]
        if trial['keypress'] == 'escape':
            core.quit()
        if trial['keypress'] == trial['key']:
            trial['ACC'] = 1
        else:
            trial['ACC'] = 0
            self.win.callOnFlip(self.clock.reset)
            self.win.flip()
            core.wait(3.0 - self.frame_dur)
        self.win.callOnFlip(self.isi.start, float(trial['ITI']) / 1000 - self.frame_dur)
        # flip buffer again and start ISI timer
        self.win.flip()
        return trial


    def test_trial(self, trial):
        # present instruction trial
        self.text.text = '+'
        self.text.draw()
        self.win.callOnFlip(self.clock.reset)
        self.isi.complete()
        self.win.flip()
        if trial['Question'] != '':
            self.text.text = '-'
            self.text.draw()
            self.win.callOnFlip(self.clock.reset)
            audio.play(self.questions[trial['Question']], wait=True)
            audio.play(self.questions[trial['Question']], wait=True)
            self.win.flip()
        keys = event.waitKeys(keyList=['escape'] + trial['keyboard'].split(' '), timeStamped=self.clock)
        trial['keypress'], trial['RT'] = keys[0]
        if trial['keypress'] == 'escape':
            core.quit()
        if trial['keypress'] == trial['key']:
            trial['ACC'] = 1
        else:
            trial['ACC'] = 0
        self.win.callOnFlip(self.isi.start, float(trial['ITI']) / 1000 - self.frame_dur)
        # flip buffer again and start ISI timer
        self.win.flip()
        return trial


if __name__ == '__main__':
    pp_info = get_pp_info()
    Experiment('language', pp_info).run()
