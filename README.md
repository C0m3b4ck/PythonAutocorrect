# PythonAutocorrect ![GitHub All Releases](https://img.shields.io/github/downloads/C0m3b4ck/PythonAutocorrect/total)
A little autocorrect in Python. Corrects the user input to words from wordlist
# Contributors
Started on August 8th, 2025 by C0m3b4ck. Right now, there are no other contributors.
# Requirements
Is coded to support Windows and Linux, tested on Ubuntu Linux.
Tested on Python 3.13
# How it works
1. Uses Levenshtein Distance to compare incorrect word to possible correct one.
2. Uses letters that neighbor others (for example: o is surrounded by 9,0,p,l,k,i) in order to correct words.
3. Uses correct words from list in "wordlist" (no extention) file in the same directory, uses keyboard keymap (like QWERTY) from keymap.conf file.
