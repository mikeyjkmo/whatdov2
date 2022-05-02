from typing import Union
from whatdo2.domain.task.typedefs import Task, PartiallyInitializedTask


def _calculate_density(task: Union[PartiallyInitializedTask, Task]) -> Task:
    """
    Given a self, return a new self with the calculated density
    """
    density = float(task.importance / task.time)
    return Task(
        id=task.id,
        name=task.name,
        importance=task.importance,
        is_prerequisite_for=task.is_prerequisite_for,
        time=task.time,
        task_type=task.task_type,
        density=density,
        activation_time=task.activation_time,
        effective_density=max(
            [t.effective_density for t in task.is_prerequisite_for] + [density]
        ),
    )
