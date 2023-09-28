# ~/.zshrc

export OPENAI_API_KEY="xxxxxx-xxxxxx-xxxxxx"

# hey command with syntax highlighting 🎨
# install glow : https://github.com/charmbracelet/glow
function hey() {
	local hey_path="$HOME/hey.py"
	export HEY_OUT=$(mktemp)
	python3 $hey_path $@ && cat $HEY_OUT | glow
}

#super quick no editor hey command / add --one_shot to disregard convo and context
function hy() {
	local hey_path="$HOME/hey.py"
	export HEY_OUT=$(mktemp)
	python3 $hey_path --no_editor $@ && cat $HEY_OUT | glow
}

# Utilize zsh to search through convos title names and preview contents of convo
function heyb() {
	hey --set_convo $(hey --convos_with_files | fzf -i --preview 'echo {} | awk -F"@" "{print \$2}" | xargs cat' | awk -F: '{print $1}')
	hey --recent
}
