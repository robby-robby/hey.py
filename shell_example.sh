# ~/.zshrc

export OPENAI_API_KEY="xxxxxx-xxxxxx-xxxxxx"

# hey command with syntax highlighting 🎨
# install glow : https://github.com/charmbracelet/glow
function hey() {
  local hey_path="$HOME/hey.py"
  export HEY_OUT=$(mktemp)
  python3 "$hey_path" "$@" && glow <"$HEY_OUT"
}

#super quick no editor hey command / add --one_shot to disregard convo and context
function hy() {
  local hey_path="$HOME/hey.py"
  export HEY_OUT=$(mktemp)
  python3 "$hey_path" --no_editor "$@" && glow <"$HEY_OUT"
}

# Utilize zsh to search through convos title names and preview contents of convo
function heyb() {
  hey --set_convo "$(hey --convos_with_files | fzf -i --preview 'echo {} | awk -F"@" "{print \$2}" | xargs cat' | awk -F: '{print $1}')"
  hey --recent
}

# Share a convo as a github gist, requires 'hub' and 'qrencode'
# brew install hub qrencode
function heyshare() {
  convo=$@
  output=$(python3 $HOME/etc/projects/hey/hey.py --ctx $convo md_file) || {
    echo "Python script failed, stopping execution."
    echo $output
    return 1
  }
  file=$output
  hub gist create --public -c $file
  echo "\n 👉 $(pbpaste)\n"
  qrencode -m 2 -t utf8 <<<"$(pbpaste)"
}
