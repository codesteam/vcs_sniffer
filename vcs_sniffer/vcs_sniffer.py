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
    repo_root = ''
    options   = {
        'php' : {
            'extensions'   : ['.php', '.php4', '.php5'],
            'check_syntax' : 'php -l %file%',
            'check_cs'     : 'phpcs --standard=zend --report=emacs %file%',
            'ignore'       : [
                'vendor',
            ]
        },
        'ruby' : {
            'extensions'   : ['.rb'],
            'check_syntax' : 'ruby -c %file%',
            'check_cs'     : 'rubocop %file%',
            'ignore'       : [
                'vendor',
            ]
        },
        'utf_bom' : True
    }

    # Setup sniffer options
    def __init__(self, repo_root):
        self.repo_root = repo_root+'/'
        config_file    = self.repo_root+'/vcs_sniffer.yaml'
        if os.path.isfile(config_file):
            self.options = self.merge_two_dicts(self.options, yaml.load(open(config_file, 'r')))

        for k, v in self.options.iteritems():
            if isinstance(self.options[k], dict) and 'ignore' in self.options[k]:
                self.options[k]['ignore'] = [self.repo_root + s for s in self.options[k]['ignore']]

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
        return (
            bool(not file.lower().startswith(tuple(self.options['php']['ignore']))) and
            bool(file.lower().endswith(tuple(self.options['php']['extensions'])))
        )

    # Return true if file contain ruby code
    def is_ruby_file(self, file):
        return (
            bool(not file.lower().startswith(tuple(self.options['ruby']['ignore']))) and
            bool(file.lower().endswith(tuple(self.options['ruby']['extensions'])))
        )

    # Check PHP syntax
    def check_php_syntax(self, file):
        output = self.run_command(self.options['php']['check_syntax'].replace('%file%', file))
        if not re.match('No syntax errors detected', output):
            raise VcsSnifferException('PHP syntax error in '+file+': '+output)

    # Check ruby syntax
    def check_ruby_syntax(self, file):
        output = self.run_command(self.options['ruby']['check_syntax'].replace('%file%', file))
        if not re.match('Syntax OK', output):
            raise VcsSnifferException('ruby syntax error in '+file+': '+output)

    # Check PHP coding standard
    def check_php_cs(self, file):
        output = self.run_command(self.options['php']['check_cs'].replace('%file%', file))
        if output != '':
            raise VcsSnifferException("PHP coding standard errors: \n"+output)

    # Check ruby coding standard
    def check_ruby_cs(self, file):
        output = self.run_command(self.options['ruby']['check_cs'].replace('%file%', file))
        if 'no offenses detected' not in output:
            raise VcsSnifferException("ruby coding standard errors: \n"+output)

    # Check valid file encoding
    def check_utf_bom(self, file):
        try:
            f     = open(file, "rb")
            byte0 = ord(f.read(1))
            byte1 = ord(f.read(1))
            byte2 = ord(f.read(1))
        except Exception as e:
            return

        if byte0 == int("EF", 16) and byte1 == int("BB", 16) and byte2 == int("BF", 16):
            raise VcsSnifferException("File '"+file+"' starts with invalid bytes EF BB BF (UTF-8 with BOM). Please remove this bytes from file use HEX editor or mc editor.")

    # Sniff current file
    def sniff(self, file):
        file = self.repo_root + file
        if not os.path.isfile(file):
            return

        if self.options['php'] and self.is_php_file(file):
            self.check_php_syntax(file)
            self.check_php_cs(file)

        if self.options['ruby'] and self.is_ruby_file(file):
            self.check_ruby_syntax(file)
            self.check_ruby_cs(file)

        if self.options['utf_bom']:
            self.check_utf_bom(file)