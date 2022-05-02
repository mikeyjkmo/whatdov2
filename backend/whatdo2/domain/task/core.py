import dataclasses as dc
import uuid
from datetime import datetime
from typing import List, Union

from whatdo2.domain.task.typedefs import (
    DependentTask,
    PartiallyInitializedTask,
    Task,
    TaskType,
)

PRIORITY_DENSITY_MARGIN = 0.1


def _calculate_density(task: Union[PartiallyInitializedTask, Task]) -> Task:
    """
    Given a self, return a new self with the calculated density
    """
    density = float(task.importance / task.time)
    max_density_of_dependent_tasks = max(
        [t.effective_density for t in task.is_prerequisite_for if t.is_active] + [0]
    )

    effective_density = density
    if max_density_of_dependent_tasks >= density:
        # If the density is smaller than the maximum of its dependent
        # tasks, this task should take on the density of that maximum, plus
        # a small margin -- this ensures that the task is more important
        # than those that depend on it, as it needs to be done first.
        effective_density = max_density_of_dependent_tasks + PRIORITY_DENSITY_MARGIN

    task_proto = dc.asdict(task)
    task_proto["density"] = density
    task_proto["effective_density"] = effective_density
    return Task(**task_proto)


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
    partially_initialized = update_task_active_state(
        partially_initialized, creation_time
    )
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


def update_task_active_state(
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
    "update_task_active_state",
    "TaskType",
    "Task",
]
