import vcs_sniffer

# Repository precommit hook
def precommit(ui, repo, **kwargs):
    try:
        sniffer = vcs_sniffer.VcsSniffer(repo.root)
        for file in repo[None].files():
            sniffer.sniff(file)
        return 0
    except vcs_sniffer.VcsSnifferException as e:
        ui.warn('\n------------------------------------\n')
        ui.warn(str(e))
        ui.warn('\n------------------------------------\n')
        return 1

# Configure repository-specific hooks
def reposetup(ui, repo):
    ui.setconfig("hooks", "precommit.vcs_sniffer", precommit)
