import os
import vcs_sniffer

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
    onlyfiles = [ f for f in os.listdir(repo.root) if os.path.isfile(os.path.join(repo.root,f)) ]
    sniffer   = vcs_sniffer.VcsSniffer(repo.root)
    errors    = []
    for file in onlyfiles:
        try:
            sniffer.sniff(file)
        except vcs_sniffer.VcsSnifferException as e:
            errors.append(str(e).strip('\n'))

    print separator
    print separator.join(errors)
    print separator