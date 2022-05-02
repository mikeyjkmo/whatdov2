from typing import Union
from whatdo2.domain.task.typedefs import Task, PartiallyInitializedTask

PRIORITY_DENSITY_MARGIN = 0.1


def _calculate_density(task: Union[PartiallyInitializedTask, Task]) -> Task:
    """
    Given a self, return a new self with the calculated density
    """
    density = float(task.importance / task.time)
    max_density_of_dependent_tasks = max(
        [t.effective_density for t in task.is_prerequisite_for] + [0]
    )

    effective_density = density
    if max_density_of_dependent_tasks >= density:
        # If the density is smaller than the maximum of its dependent
        # tasks, this task should take on the density of that maximum, plus
        # a small margin -- this ensures that the task is more important
        # than those that depend on it, as it needs to be done first.
        effective_density = max_density_of_dependent_tasks + PRIORITY_DENSITY_MARGIN

    return Task(
        id=task.id,
        name=task.name,
        importance=task.importance,
        is_prerequisite_for=task.is_prerequisite_for,
        time=task.time,
        task_type=task.task_type,
        density=density,
        activation_time=task.activation_time,
        is_active=task.is_active,
        effective_density=effective_density,
    )
