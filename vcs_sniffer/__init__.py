import os
import vcs_sniffer
import fnmatch

from mercurial import cmdutil

cmdtable  = {}
command   = cmdutil.command(cmdtable)
separator = '\n------------------------------------\n'

# Repository precommit hook
def precommit(ui, repo, **kwargs):
    try:
        sniffer = vcs_sniffer.VcsSniffer(repo.root)
        for file in repo[None].files():
            sniffer.sniff(file)
        return 0
    except vcs_sniffer.VcsSnifferException as e:
        ui.warn(separator)
        ui.warn(str(e))
        ui.warn(separator)
        return 1

# Configure repository-specific hooks
def reposetup(ui, repo):
    ui.setconfig("hooks", "precommit.vcs_sniffer", precommit)

# Sniff all files in repo folder
@command('sniff')
def sniff(ui, repo, remote_name=None):
    repo_files = []
    for root, dirs, files in os.walk(repo.root):
        for filename in fnmatch.filter(files, '*.*'):
            file = os.path.join(root, filename)
            if not file.lower().startswith(repo.root+'/.hg'):
                repo_files.append(file.replace(repo.root+'/', ''))

    sniffer   = vcs_sniffer.VcsSniffer(repo.root)
    errors    = []
    for file in repo_files:
        try:
            sniffer.sniff(file)
        except vcs_sniffer.VcsSnifferException as e:
            errors.append(str(e).strip('\n'))

    if len(errors):
        print separator
        print separator.join(errors)
        print separator
    else:
        print 'No errors found'