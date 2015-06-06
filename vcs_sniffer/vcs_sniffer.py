import collections
import os
import re
import string
import subprocess
import yaml

class VcsSnifferException(Exception):
    pass

class VcsSniffer:
    # Sniffers options
    options = {
        'php' : {
            'extensions'   : ['php', 'php4', 'php5'],
            'check_syntax' : 'php -l %file%',
            'check_cs'     : 'phpcs --standard=zend --report=emacs %file%'
        },
        'utf_bom' : True
    }

    # Setup sniffer options
    def __init__(self, config_file):
        if os.path.isfile(config_file):
            self.options = self.merge_two_dicts(self.options, yaml.load(open(config_file, 'r')))

    # Update value of a nested dictionary of varying depth
    def merge_two_dicts(self, d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = self.merge_two_dicts(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    # Run CLI command
    def run_command(self, command):
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        return output

    # Return true if file contain PHP code
    def is_php_file(self, file):
        return bool(file.lower().endswith(tuple(self.options['php']['extensions'])))

    # Check PHP syntax
    def check_php_syntax(self, file):
        output = self.run_command(self.options['php']['check_syntax'].replace('%file%', file))
        if not re.match('No syntax errors detected', output):
            raise VcsSnifferException('PHP syntax error in '+file+': '+output)

    # Check PHP coding standard
    def check_php_cs(self, file):
        output = self.run_command(self.options['php']['check_cs'].replace('%file%', file))
        if output != '':
            raise VcsSnifferException("PHP coding standard errors: \n"+output)

    # Check valid file encoding
    def check_utf_bom(self, file):
        f     = open(file, "rb")
        byte0 = ord(f.read(1))
        byte1 = ord(f.read(1))
        byte2 = ord(f.read(1))
        if byte0 == int("EF", 16) and byte1 == int("BB", 16) and byte2 == int("BF", 16):
            raise VcsSnifferException("File '"+file+"' starts with invalid bytes EF BB BF (UTF-8 with BOM). Please remove this bytes from file use HEX editor or mc editor.")

    # Sniff current file
    def sniff(self, file):
        if not os.path.isfile(file):
            return

        if self.options['php'] and self.is_php_file(file):
            self.check_php_syntax(file)
            self.check_php_cs(file)

        if self.options['utf_bom']:
            self.check_utf_bom(file)