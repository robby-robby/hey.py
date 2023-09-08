# ~/.zshrc

OPENAI_API_KEY="xxxxxx-xxxxxx-xxxxxx"

# hey command with syntax highlighting 🎨
# install glow : https://github.com/charmbracelet/glow
function hey() {
	local hey_path="$HOME/hey.py"
	export HEY_OUT=$(mktemp)
	python3 $hey_path $@ && cat $HEY_OUT | glow
}

function hy() {
	local hey_path="$HOME/hey.py"
	export HEY_OUT=$(mktemp)
	python3 $hey_path --no_editor $@ && cat $HEY_OUT | glow
}

function heyb() {
	hey --set_branch $(hey --branches_with_files | fzf -i --preview 'echo {} | awk -F"@" "{print \$2}" | xargs cat' | awk -F: '{print $1}')
	hey --recent
}
