import dataclasses as dc
import uuid
from datetime import datetime
from typing import List

from whatdo2.domain.task.private import _calculate_density
from whatdo2.domain.task.typedefs import (DependentTask,
                                          PartiallyInitializedTask, Task,
                                          TaskType)


def create_task(
    name: str,
    importance: int,
    time: int,
    task_type: TaskType,
    activation_time: datetime,
    creation_time: datetime,
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
        is_prerequisite_for=(),
        activation_time=activation_time,
        is_active=False,
    )
    partially_initialized = set_task_active_state(partially_initialized, creation_time)
    return _calculate_density(partially_initialized)


def make_prerequisite_of(task: Task, dependents_to_add: List[Task]) -> Task:
    """
    Make this task a prerequisite of another one

    The task's effective_density will be recalculated as the maximum of its own
    and its dependencie's densities
    """
    existing_dependency_ids = set(t.id for t in task.is_prerequisite_for)
    new_dependents_to_add = [
        DependentTask.from_task(t)
        for t in dependents_to_add
        if t.id not in existing_dependency_ids
    ]

    result = dc.replace(
        task,
        is_prerequisite_for=(
            *task.is_prerequisite_for,
            *new_dependents_to_add,
        ),
    )
    return _calculate_density(result)


def remove_as_prequisite_of(task: Task, dependents_to_remove: List[Task]) -> Task:
    """
    Remove dependent tasks from a given task

    The task's effective_density will be recalculated as the maximum of its own
    and its dependencie's densities
    """
    remove_ids = [t.id for t in dependents_to_remove]
    result = dc.replace(
        task,
        is_prerequisite_for=tuple(
            t for t in task.is_prerequisite_for if t.id not in remove_ids
        ),
    )
    return _calculate_density(result)


def set_task_active_state(
    task: PartiallyInitializedTask,
    time: datetime,
) -> PartiallyInitializedTask:
    """
    Set the task active state at the given time
    """
    return dc.replace(
        task,
        is_active=bool(
            task.activation_time.replace(tzinfo=None) <= time.replace(tzinfo=None)
        ),
    )


__all__ = [
    "create_task",
    "make_prerequisite_of",
    "remove_as_prequisite_of",
    "set_task_active_state",
    "TaskType",
    "Task",
]
