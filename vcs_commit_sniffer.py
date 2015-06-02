import re
import os
import string
from subprocess import *

def precommit_check(ui, repo, **kwargs):
    # Set folders to check
    foldersToCheck = [
        '(app/commands/)',
        '(app/components/)',
        '(app/config/)',
        '(app/controllers/)',
        '(app/models/)',
        '(app/vendors/)',
    ]
    foldersToIgnore = [
        '(app/vendors)',
    ]

    # Get parent folder path (repo root folder)
    baseRepoPath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))+'/'

    # Loop through each file for the current changeset
    for currentFile in repo[None].files():
        # Check PHP Files
        if re.match('.*\.(php)|(php4)|(php5)', currentFile):
            # Check PHP syntax
            p = Popen("php -l "+baseRepoPath+currentFile, shell=True, stdout=PIPE)
            output = p.communicate()[0]

            # File exist?
            if os.path.isfile(baseRepoPath+currentFile):

                # Is PHP file valid?
                if not re.match('No syntax errors detected', output):
                    ui.warn('\n-----------------------\n')
                    ui.warn("PHP syntax error in file: "+baseRepoPath+currentFile+" please run php -l <file> to get more info.")
                    ui.warn('\n-----------------------\n')
                    return 1

                # Check PHP coding standards for specidied folders
                if re.match(string.join(foldersToCheck, '|'), currentFile) and not re.match(string.join(foldersToIgnore, '|'), currentFile):
                    # Run php CS check
                    p = Popen("phpcs --standard=zend --report=emacs "+baseRepoPath+currentFile, shell=True, stdout=PIPE)
                    output = p.communicate()[0]

                    if output != '':
                        # Show warning for user
                        ui.warn('\n-----------------------\n')
                        ui.warn(output)
                        ui.warn('-----------------------\n')

                        # Reject the changesets
                        return 1

                # Check valid file encoding
                f = open(baseRepoPath+currentFile, "rb")

                byte0 = ord(f.read(1))
                byte1 = ord(f.read(1))
                byte2 = ord(f.read(1))

                if byte0 == int("EF", 16) and byte1 == int("BB", 16) and byte2 == int("BF", 16):
                    ui.warn("File '"+baseRepoPath+currentFile+"' starts with invalid bytes EF BB BF (UTF-8 with BOM). Please remove this bytes from file use HEX editor or mc editor.")
                    return 1

    # All allright
    return 0
