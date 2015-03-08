Taskwarrior Blocks Capsule
==========================

When defining tasks in taskwarrior, you currently have only one option--
annotating which tasks a given task depends upon using the ``depends:``
argument.  This capsule adds a new argument -- ``blocks:`` which you can
use for creating task dependencies from the opposite side.

Installation
------------

1. Make sure you have `Taskwarrior-Capsules <https://github.com/coddingtonbear/taskwarrior-capsules>`_ installed.
2. Install this library::

    pip install taskwarrior-blocks-capsule

3. That's all!

Use
---

Create a task that blocks another by using the ``blocks:`` argument
with comma-separated list of task UUIDs or IDs; imagine that you have
a task with an ID of ``25`` for which you'd like to create a dependent
task::

    tw add "Make sure to apply peanut butter to bread" blocks:25

The above command will cause two commands to be executed behind the
scenes::

    task add "Make sure to apply peanut butter to bread"
    # let's pretend that this is created as task #26

    task 25 modify depends:26
