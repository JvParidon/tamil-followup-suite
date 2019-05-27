from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import core, visual, event, gui
import reading
import cambridge
import illusions
import repetition
import span
import ravens
from test_tools import pause, get_pp_info

def check_current():
    with open('current', 'r') as currentfile:
        return int(currentfile.read())

def save_current(current):
    with open('current', 'w') as currentfile:
        currentfile.write(str(current))

def run_experiment(pp_info, experiment, condition=False):
    if condition:
        experiment.Experiment(condition, pp_info).run()
    else:
        experiment.Experiment(pp_info).run()

def run(pp_info):
    if (int(pp_info['number']) % 2) == 1:
        experiments = [
            [illusions],
            [language_music, 'language'],
            [language_music, 'music'],
            [repetition, 'word'],
            [repetition, 'pseudoword'],
            [span, 'forward'],
            [span, 'backward'],
            [ravens, 'a'],
            [ravens, 'b']
        ]
    elif (int(pp_info['number']) % 2) == 0:
        experiments = [
            [illusions],
            [language_music, 'music'],
            [language_music, 'language'],
            [repetition, 'word'],
            [repetition, 'pseudoword'],
            [span, 'forward'],
            [span, 'backward'],
            [ravens, 'b'],
            [ravens, 'a']
        ]

    current = check_current()
    for i in range(current, len(experiments)):
        save_current(i)
        pause()
        run_experiment(pp_info, *experiments[i])
    save_current(0)

if __name__ == '__main__':
    run(get_pp_info())
