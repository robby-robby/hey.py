### User
Lets build the apple script for this together,

It should open an Iterm2 application window and run the following command,

hey --img <FILE>

replacing <FILE> with the full path of the file that was right clicked
          
### Assistant
Sure, here is a simple AppleScript that will do this.

1. Open Automator according to the instructions given before.

2. Below is a template for the AppleScript:

```
on run {input, parameters}
	tell application "iTerm"
		activate
		set newWindow to (create window with default profile) 
		tell newWindow
			select
			tell current session	
				write text "hey --img " & quoted form of POSIX path of (item 1 of input)
			end tell
		end tell	
	end tell
end run
```

This will open a new iTerm window and run your command.

3. Paste this into the AppleScript section in Automator.

Remember to select "files or folders" in "Finder" at the top of the Automator workflow. Then you can save it, as instructed above, and it will appear in the right-click menu in Finder. Right-clicking on a file will run this script with the full path of that file.
          
### User
Give me the complete directions for writing this in automator
          
### Assistant
Sure, here are the complete directions:

1. Open Automator. You can do this by clicking the spotlight (magnifying glass on the top right corner of the screen) and typing "Automator".

2. Once the Automator application is open, click on "File" from the menu bar, then "New" from the dropdown menu.

3. Automator will prompt you for a document type. Click on “Service” or "Quick Action" (Depending on your macOS version), then click "Choose".

4. At the top of the Automator, you will see a bar that says "Service receives selected" or "Workflow receives current". In the dropdown, select "files or folders".

5. To the right of the above dropdown, there is another dropdown that says "in". In this dropdown menu, select "Finder".

6. In the leftmost column (Library), you will find a few folders. Click on the "Utilities" folder.

7. In the middle column, you will find several actions. Drag and drop "Run AppleScript" from this column to the column on the right.

8. In the right column, you will now see an editable AppleScript block. Replace the default script with this:

```
on run {input, parameters}
	tell application "iTerm"
		activate
		set newWindow to (create window with default profile) 
		tell newWindow
			select
			tell current session	
				write text "hey --img " & quoted form of POSIX path of (item 1 of input)
			end tell
		end tell	
	end tell
end run
```

9. Now, you can save your Service or Quick Action. Go to File -> Save, and name your Service (something like "Run Hey Command in iTerm").

The menu items in Finder's right-click menu are arranged alphabetically, so you can use that to regulate where you want your right-click action to appear. If you want it on top of the list, you might want to give it a name that will put it there alphabetically.

Feed in the name, and after that every time you right-click a file or folder, you will see the option to run your AppleScript by selecting "Run Hey Command in iTerm" from the context menu, under the Services or Quick Action submenu.
          
