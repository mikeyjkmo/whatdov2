import dataclasses as dc
from typing import List
import uuid
from datetime import datetime

from whatdo2.domain.task.typedefs import TaskType, PartiallyInitializedTask, Task
from whatdo2.domain.task.private import _calculate_density


def create_task(
    name: str,
    importance: int,
    time: int,
    task_type: TaskType,
    activation_time: datetime,
) -> Task:
    """
    Public constructor for a Task
    """
    partially_initialized = PartiallyInitializedTask(
        id=uuid.uuid4(),
        name=name,
        importance=importance,
        time=time,
        task_type=task_type,
        depends_on=(),
        activation_time=activation_time,
    )
    return _calculate_density(partially_initialized)


def make_dependent_on(task: Task, dependencies_to_add: List[Task]) -> Task:
    """
    Make this task dependent on another one

    The task's effective_density will be recalculated as the maximum of its own
    and its dependencie's densities
    """
    # Filter out tasks that are already parents
    new_dependencies = [t for t in dependencies_to_add if t not in task.depends_on]
    result = dc.replace(
        task,
        depends_on=(*task.depends_on, *new_dependencies),
    )
    return _calculate_density(result)


def remove_dependencies(task: Task, dependencies_to_remove: List[Task]) -> Task:
    """
    Remove dependent tasks from a given task

    The task's effective_density will be recalculated as the maximum of its own
    and its dependencie's densities
    """
    result = dc.replace(
        task,
        depends_on=tuple(t for t in task.depends_on if t not in dependencies_to_remove),
    )
    return _calculate_density(result)


def is_task_active_at(task: Task, time: datetime) -> bool:
    """
    Given a task and time, return whether it is active at this time
    """
    return bool(task.activation_time < time)


__all__ = [
    "create_task",
    "make_dependent_on",
    "remove_dependencies",
    "is_task_active_at",
    "TaskType",
]
