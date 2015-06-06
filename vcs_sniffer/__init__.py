import vcs_sniffer

# Repository precommit hook
def precommit(ui, repo, **kwargs):
    try:
        sniffer = vcs_sniffer.VcsSniffer(repo.root+'/vcs_sniffer.yaml')
        for file in repo[None].files():
            sniffer.sniff(repo.root+'/'+file)
        return 0
    except vcs_sniffer.VcsSnifferException as e:
        ui.warn('\n------------------------------------\n')
        ui.warn(str(e))
        ui.warn('\n------------------------------------\n')
        return 1

# Configure repository-specific hooks
def reposetup(ui, repo):
    ui.setconfig("hooks", "precommit.vcs_sniffer", precommit)
