import time
import os
import sys

# Text to output
text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis 
aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat 
nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui 
officia deserunt mollit anim id est laborum."""


def erase_lines(text: str):
    lines = (
        text.count("\n") + 1
    )  # Calculate number of lines by counting newline characters

    sys.stdout.write("\033[{}A".format(lines))  # Move up 'lines' lines

    for _ in range(lines):
        sys.stdout.write("\033[K")  # 'Erase' the line
        if _ != lines - 1:  # No need to move down on the last iteration
            sys.stdout.write("\033[B")  # Move down a line

    sys.stdout.flush()  # Make sure all output is flushed


# Split the text into a list of characters
characters = list(text)

# For each character in the list
for char in characters:
    # Print the character
    sys.stdout.write(char)
    sys.stdout.flush()  # ensuring the character prints as soon as it's received
    # Sleep for a short period to simulate typing
    time.sleep(0.01)

# os.system("clear")
erase_lines(text)
# # Backspace through all characters
# for char in reversed(characters):
#     # If the character is a newline, move the cursor up, otherwise backspace
#     if char == "\n":
#         sys.stdout.write("\033[F")  # Move up a line
#     else:
#         sys.stdout.write("\b \b")  # Backspace a character

#     sys.stdout.flush()
#     time.sleep(0.01)  # Sleep to animate the backspacing


# Usage:
# erase_lines(Your_text_here)
