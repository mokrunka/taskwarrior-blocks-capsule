import datetime

import pytz

from taskwarrior_capsules.capsule import CommandCapsule
from taskwarrior_capsules.exceptions import CapsuleError


class Blocks(CommandCapsule):
    """ Allows task add/edits to use 'blocks:' as well as 'depends:'"""
    MIN_VERSION = '0.3'
    MAX_VERSION = '0.9999'
    MIN_TASKWARRIOR_VERSION = '2.2'
    MAX_TASKWARRIOR_VERSION = '2.4.9999'

    def preprocess(self, filter_args, extra_args, command_name, **kwargs):
        self.meta.blocks_add = []
        self.meta.blocks_remove = []
        self.meta.started = datetime.datetime.utcnow().replace(
            tzinfo=pytz.utc,
            microsecond=0,  # We don't get this level of precision from TW
        )
        ids = []

        if command_name not in ('add', 'edit'):
            return filter_args, extra_args, command_name

        final_extra_args = []
        for arg in extra_args:
            if arg.startswith('blocks:'):
                ids = arg[7:].split(',')
                for id in ids:
                    minus = False
                    if id.startswith('-'):
                        minus = True
                        id = id[1:]
                    elif id.startswith('+'):
                        id = id[1:]

                    try:
                        # This value is an ID
                        id = int(id)
                        _, task = self.client.get_task(id=id)
                        if task:
                            if minus:
                                self.meta.blocks_remove.append(task)
                            else:
                                self.meta.blocks_add.append(task)
                        else:
                            raise CapsuleError(
                                "No task with id %s was found." % id
                            )
                    except ValueError:
                        # This value is a UUID
                        _, task = self.client.get_task(uuid=id)
                        if task:
                            if minus:
                                self.meta.blocks_remove.append(task)
                            else:
                                self.meta.blocks_add.append(task)
                        else:
                            raise CapsuleError(
                                "No task with uuid %s was found." % id
                            )
            else:
                final_extra_args.append(arg)

        return filter_args, final_extra_args, command_name

    def postprocess(self, filter_args, extra_args, **kwargs):
        altered_tasks = self.get_tasks_changed_since(self.meta.started)

        for dependency in altered_tasks:
            for task in self.meta.blocks_add:
                task['depends'] = [dependency['uuid']]
                self.client.task_update(task)
            for task in self.meta.blocks_remove:
                task['depends'] = ['-%s' % dependency['uuid']]
                self.client.task_update(task)
