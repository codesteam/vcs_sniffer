import re
import os
import string
import subprocess

class VcsSnifferException(Exception):
    pass

class VcsSniffer:
    options = {
        'php' : {
            'extensions'   : ['php', 'php4', 'php5'],
            'check_syntax' : 'php -l %file%',
            'check_cs'     : 'phpcs --standard=zend --report=emacs %file%'
        }
    }

    # Sniffers list
    CHECK_PHP_SYNTAX  = 'php_syntax'
    CHECK_PHP_CS      = 'php_cs'
    CHECK_JS_SYNTAX   = 'js_syntax'
    CHECK_JS_CS       = 'js_cs'
    CHECK_RUBY_SYNTAX = 'ruby_syntax'
    CHECK_RUBY_CS     = 'ruby_cs'
    CHECK_UTF_BOM     = 'utf_bom'

    # def __init__(self):
        # self.options = {}

    def run_command(self, command):
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        return output

    def is_php_file(self, file):
        return bool(re.match('.*\.('+')|('.join(self.options['php']['extensions'])+')', file))

    # Check PHP syntax
    def check_php_syntax(self, file):
        # Check file extension and file existence
        if not self.is_php_file(file) or not os.path.isfile(file):
            return

        # Run check PHP syntax command
        output = self.run_command(self.options['php']['check_syntax'].replace('%file%', file))

        # Is PHP file valid?
        if not re.match('No syntax errors detected', output):
            raise VcsSnifferException('PHP syntax error in '+file+': '+output)

    # Check PHP coding standard
    def check_php_cs(self, file):
        # Check file extension and file existence
        if not self.is_php_file(file) or not os.path.isfile(file):
            return

        # Run PHP coding standard check
        output = self.run_command(self.options['php']['check_cs'].replace('%file%', file))

        # Is PHP file coding standard valid?
        if output != '':
            raise VcsSnifferException("PHP coding standard errors: \n"+output)

# sniffer = VcsSniffer()

# sniffer.check_php_syntax('/var/www/vcs_commit_sniffer/test.php')
# sniffer.check_php_cs('/var/www/vcs_commit_sniffer/test.php')