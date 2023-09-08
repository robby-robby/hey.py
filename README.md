# hey.py

## _ChatGPT for the command line ! (with the help of vim and python3)_

### Just say hey!

```sh
$> hey --new
$> hey introduce yourself

[ vim ]

introduce yourself


:wq
```

```markdown
> "AI Language Model: Your Virtual Assistant for Any Task!"

### User

introduce yourself

### Assistant

Hello! I am an AI language model developed by OpenAI. I am here to assist you with any questions or tasks
you have. Feel free to ask me anything!
```

Use `hey.py` to configure your model and manage prompts from the Command-Line Interface (CLI).

## No dependencies to install! (except python3)

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

## Usage

```sh
hey.py [-h] [--no_editor] [--reset] [--qk] [--qk4] [--get_model]
       [--delete_convo DELETE_CTX] [--archive] [--one_shot]
       [--tidy] [--pins] [--pin] [--unpin UNPIN] [--models]
       [--temp TEMP] [--set_model SET_MODEL] [--dir DIR]
       [--editor EDITOR] [--new_convo] [--set_pin SET_PIN]
       [--set_convo SET_CTX] [--show SHOW] [--convos]
       [--convos_with_files] [--recent] [--info] [--trim TRIM]
       [--new] [--retry] [--init]
```

## Description

`hey.py` is a CLI for model configuration and prompt management.

### Positional Arguments

### Options

- `-h`, `--help`: Show the help message and exit
- `--no_editor`: Do not open the editor
- `--reset`: Reset the convo and config
- `--qk`: Quick and dirty mode, one-liner from CLI, no editor, does not save prompts, uses GPT-3.5 for speed and cost
- `--qk4`: GPT4 quick and dirty mode, one-liner from CLI, no editor, does not save prompts
- `--get_model`: Get the current model
- `--delete_convo DELETE_CTX`: Delete prompt convo
- `--archive`: Move all convos to archive
- `--one_shot`: One shot GPT4, does not save prompts
- `--tidy`: Tidy orphaned convos
- `--pins`: List all pins
- `--pin`: Pin the current convo
- `--unpin UNPIN`: Unpin the given pin
- `--models`: List all models
- `--temp TEMP`: Set temperature: 1-10
- `--set_model SET_MODEL`: Set the current model to the nth model in the list
- `--dir DIR`: Set the prompts directory and subsequent config and convo files
- `--editor EDITOR`: Set the editor path
- `--new_convo`: New prompt convo
- `--set_pin SET_PIN`: Set prompt convo to pin
- `--set_convo SET_CTX`: Set prompt convo
- `--show SHOW`: Show prompt convo
- `--convos`: List convos
- `--convos_with_files`: List convos with files
- `--recent`: Output the most recent prompt read from the convo file
- `--info`: convo, config, and prompts directory
- `--trim TRIM`: Trim the first <n> responses from the convo when fetching the next prompt
- `--new`: Create new conversation/convo
- `--retry`: Retry the last prompt
- `--init`: Init the last prompt

Each option can be used directly on the command-line when using `hey.py`. Make sure you replace any needed values (like `DELETE_CTX`, `TEMP`, `SET_MODEL`, `DIR`, `EDITOR`, `SET_PIN`, `SET_CTX`, `SHOW`, `TRIM`, `NEW`, `RETRY`, or `INIT`) with your actual values when using the options.
