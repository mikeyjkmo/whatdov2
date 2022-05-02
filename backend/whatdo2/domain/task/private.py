from whatdo2.domain.task.typedefs import BaseTask, Task


def _calculate_density(task: BaseTask) -> Task:
    """
    Given a self, return a new self with the calculated density
    """
    density = float(task.importance / task.time)
    return Task(
        id=task.id,
        name=task.name,
        importance=task.importance,
        depends_on=task.depends_on,
        time=task.time,
        task_type=task.task_type,
        density=density,
        activation_time=task.activation_time,
        effective_density=max([t.density for t in task.depends_on] + [density]),
    )
