import vcs_sniffer

# Repository precommit hook
def precommit(ui, repo, **kwargs):
    sniffer = vcs_sniffer.VcsSniffer()

    for file in repo[None].files():
        ui.warn('\n '+file+' \n')

    return 1

# Configure repository-specific hooks
def reposetup(ui, repo):
    ui.setconfig("hooks", "precommit.vcs_sniffer", precommit)
