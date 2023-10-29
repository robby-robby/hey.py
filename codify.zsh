#!/bin/zsh

# Used for 'codify' feature dependent on iterm2
#
# Copy or Open code blocks CMD+Click in Iterm2
#
# To install in Iterm2
# - Go to Profiles->Advanced->Semantic History
# - Selectbox 'Run Coprocess', <FULL FILE PATH OF THIS SHELLSCRIPT>/copy.codify.zsh \1 \2
#
# hey.py will output the snippet and copy file paths to output, this script will intercept
# the CMD+click based on the filename and behave accordingly.
#
# the output will look like this:
#
#        function(){ console.log('hello world') }
#
#        copy:
#        /var/folders/_9/p8ggjlmn71b0jc_mjp32_nlc0000gn/T/tmpotazlf09/geawJ_TyCFbv4r_dQFTaL4IJXDs40Rk4.hey_copy_codify.js
#
#        snippet:
#        /var/folders/_9/p8ggjlmn71b0jc_mjp32_nlc0000gn/T/tmpotazlf09/geawJ_TyCFbv4r_dQFTaL4IJXDs40Rk4.hey_snippet_codify.js
#
# -------
# CMD+Click under copy: will copy to clipboard
# CMD+Click under snippet: will open in editor

# validate argument
if [ $# -eq 0 ]; then
  echo "No file name provided"
  exit 1
fi

file_path=$1
line_number=$2

# check if file name contains 'hey_copy_codify'
if [[ $file_path =~ "hey_copy_codify" ]]; then
  pbcopy <"$file_path"
else
  #default behavior for either hey_snippet_codify or any other file outside of hey.py
  #for Vscode try this: '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code' --goto $file_path
  if [ -z "$line_number" ]; then
    echo vim $file_path
  else
    echo vim +$line_number $file_path
  fi

fi
