# Stevens-StudyPlan

Generate a mostly-filled study plan from your Unofficial Transcript. Note that this is only necessary for filling out [these forms](https://www.stevens.edu/directory/office-registrar/study-planac) (see bottom of page, last expanding button). This has nothing to do with workday.

## How to Use

1. `pip install regex`
2. Create file `Transcript.txt`
3. Go to [myStevens](https://my.stevens.edu) `>>` Student/Faculty Web Self Services `>>` Access `>>` (Set Term `>>`) Student Records `>>` Unofficial Transcript
4. Copy all text from your name to the bottom, ideally including "END OF UNDERGRADUATE ACADEMIC RECORD"
5. Paste into the created file
6. Run `python main.py`

## Instability

I'm guessing something didn't work...

### Incorrect output

I'm not actively maintaining this project. [Feel free to create an issue](https://github.com/PMARINA/Stevens-StudyPlan/issues/new) so others are aware. Someone else might fix the problem.

### Error

What kind of error are you getting?

#### ValueError

Something probably went wrong while reading a file. Read the error for more info. If you can't solve it, [post an issue](https://github.com/PMARINA/Stevens-StudyPlan/issues/new). Do NOT post your transcript on the internet. Do provide the entire output of the program (which shouldn't have any private info, but double check before posting). If prompted for more information by someone working on this project, be wary of them (stranger-danger).

#### NotImplementedError

Either the codebase is broken, or more likely, I haven't included your major/entry date's study plan. See [here](https://github.com/PMARINA/Stevens-StudyPlan/tree/main/Study%20Plans/) for all the supported majors and years. Feel free to follow the existing files to create your own. If you do this and get reasonable output, please consider submitting a pull request so others can use your study plan file. 
