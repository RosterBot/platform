
from ansible import playbook
import ansible.callbacks as callbacks
import ansible.utils as utils
import yaml


def run_ansible_in_python(task):
    stats = callbacks.AggregateStats()
    plays = yaml.load("\n\n".join([file(play.abspath()).read() for play in task.inputs]))
    pb = playbook.PlayBook(playbook=plays,
                           host_list=['localhost'],
                           stats=stats,callbacks=callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY),
                           runner_callbacks=callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
    )
    pb.run()


def run_ansible_in_shell(task):
    task.exec_command('ansible-playbook -i "localhost," ' + ' '.join([playbook_file.abspath()
                                                                      for playbook_file in task.inputs]))