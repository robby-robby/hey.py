# hey.py

## ChatGPT for the command-line power-user using iterm2, python3 and vim, with syntax highlighting cmd+click-to-copy or cmd+click-to-snippet features

# Demo

![Demo](https://github.com/robby-robby/hey.py/blob/demo/hey_demo.gif)

### Just say hey!

```sh
$> hey

[ vim ]

give me fizzbuzz in js

:wq
```

```markdown
### User

give me fizzbuzz in js

### Assistant

Sure, here's a simple implementation of FizzBuzz in JavaScript:

for (var i = 1; i <= 100; i++) {
var output = '';
if (i % 3 === 0) { output += 'Fizz'; }
if (i % 5 === 0) { output += 'Buzz'; }
console.log(output || i);
}

#### copy:

/var/folders/9/p8ggjlmn71b0jcmjp32nlc0000gn/T/tmp01zszp6j/cFSUdc4WnQEwHSC9qFAKvWR3eJ4LM.hey_copy_codify.js

#### snippet:

/var/folders/9/p8ggjlmn71b0jcmjp32nlc0000gn/T/tmp01zszp6j/cFSUdc4WnQEwHSC9qFAKvWR3eJ4LM.hey_snippet_codify.js
```

## _No dependencies to install! (except python3)_

- less headache

# Added --fork flag

- forks off the current conversation but stays on the current one

# 📸 📸 📸 📸 _New image file upload support!_ 📸 📸 📸 📸 📸 Added: Nov 17 2023

- `hey --img <path to image file>/URL> <prompt>`
- Currently works in 'one shot' mode only, does not save prompts

# 🌀🌀🌀🌀*New stream support!* 🫶 🫶 🫶 🫶 🫶 Added: Oct 24 2023

- Enable with `--stream` flag
- Typing effect for faster response time
- The clear terminal command is sent after typing, then the formatted response will be output to the terminal. Therefore, it is not recommended if piping to another process.

# ⚡️⚡️⚡️️*NEW BONUS Prompt Explorer* 👇👇👇👇 Added Sep 9th 2023

💥 _drop prompts.html into the prompts directory in `$HOME/.hey_py`_
then run: 💥

```sh
$> cd $HOME/.hey_py && python3 -m http.server 8000
```

Also, take a look at `prompts.zsh` which uses a slightly different approach to the prompt explorer.

# Setup

- Look in [shell_example.sh](https://github.com/robby-robby/hey.py/blob/main/shell_example.sh)

- [Install glow (optional)](https://github.com/charmbracelet/glow)

- [Install fzf (optional)](https://github.com/junegunn/fzf)

- [Install vim (optional)](https://www.vim.org/download.php)

### _No vim!? no problem!_

[Install micro editor ](https://micro-editor.github.io/)

```sh
$> hey --editor micro
```

**Note: The editor should be terminal based and 'blocking' (hey.py waits for editor to close to run the prompt)**

## Usage

```sh
usage: hey.py [-h] [--codify] [--codify_on] [--stream] [--codify_off] [--no_editor] [--reset]
              [--qk] [--qk4] [--get_model] [--delete_convo DELETE_CONVO]
              [--archive] [--one_shot] [--tidy] [--pins] [--pin] [--unpin UNPIN]
              [--models] [--temp TEMP] [--set_model SET_MODEL] [--dir DIR]
              [--editor EDITOR] [--new_convo] [--set_pin SET_PIN]
              [--set_convo SET_CONVO] [--show SHOW] [--convos]
              [--convos_with_files] [--recent] [--info] [--trim TRIM] [--new]
              [--retry] [--init]
              ...
```

## Instructions

`hey.py --help`

CLI for model configuration and prompt management.

**Positional Arguments**

`sentence` - Capture remaining input after flags

**Options**

`-h, --help` - show this help message and exit

`--fork` - Fork a conversation

`--codify` - output with codify

`--codify_on` - turn on codify

`--codify_off` - turn off codify

`--no_editor` - do not open the editor

`--reset` - reset the context and config

`--qk` - quick and dirty mode, one-liner from cli, no editor, does not save prompts, uses gpt-3.5 for speed and cost

`--qk4` - gpt4 quick and dirty mode, one-liner from cli, no editor, does not save prompts

`--get_model` - get the current model

`--delete_convo DELETE_CONVO` - delete prompt convo

`--archive` - move all convos to archive

`--one_shot` - one shot gpt4, does not save prompts

`--tidy` - tidy orphaned contexts

`--pins` - list all pins

`--stream` - text stream output; 'typing effect'

`--pin` - pin the current context

`--unpin UNPIN` - unpin the given pin

`--models` - list all models

`--temp TEMP` - set temperature: 1-10

`--set_model SET_MODEL` - set the current model to the nth model in the list

`--dir DIR` - set the prompts directory and subsequent config and context files

`--editor EDITOR` - set the editor path

`--new_convo` - new prompt convo

`--set_pin SET_PIN` - set prompt convo to pin

`--set_convo SET_CONVO` - set prompt convo

`--show SHOW` - show prompt convo

`--convos` - list convos

`--convos_with_files` - list convos with files

`--recent` - output the most recent prompt read from the context file

`--info` - context, config and prompts directory

`--trim TRIM` - trim the first <n> responses from the context when fetching the next prompt

`--new` - create new conversation / context

`--retry` - retry the last prompt

`--init` - init the last prompt

## _New CODIFY.zsh Feature!_

- Enabled with `--codify_on` flag

### Copy or Open code blocks CMD+Click in Iterm2 !!!

### To install in Iterm2

- Go to Profiles->Advanced->Semantic History
- Selectbox 'Run Coprocess', <FULL FILE PATH OF THIS SHELLSCRIPT>/copy.codify.zsh \1 \2

`hey.py` will output the snippet and copy file paths to output, this script will intercept
the **CMD+CLICK** based on the filename and behave accordingly.

the output will look like this:

```js
   function(){ console.log('hello world') }
```

        copy:
        /var/folders/_9/p8ggjlmn71b0jc_mjp32_nlc0000gn/T/tmpotazlf09/geawJ_TyCFbv4r_dQFTaL4IJXDs40Rk4.hey_copy_codify.js

        snippet:
        /var/folders/_9/p8ggjlmn71b0jc_mjp32_nlc0000gn/T/tmpotazlf09/geawJ_TyCFbv4r_dQFTaL4IJXDs40Rk4.hey_snippet_codify.js

---

- **CMD+CLICK** the file under 'copy:' will copy the contents to clipboard
- **CMD+CLICK** under 'snippet:' will open in editor
