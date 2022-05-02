import dataclasses as dc
import uuid
from datetime import datetime
from typing import List

from whatdo2.domain.task.typedefs import DependentTask, Task, TaskType
from whatdo2.domain.utils import pipe

PRIORITY_DENSITY_MARGIN = 0.1


class TaskFunction:
    """
    This can be either the function to create a task or to perform
    a state change on it

    All functions that operate on Task should inherit from this class
    to ensure that the Task is always in a consistent state after an operation.
    """

    def __init__(self, current_time: datetime) -> None:
        self._current_time = current_time

    @staticmethod
    def _calculate_density(task: Task) -> Task:
        """
        Given a task, return a new task with the calculated density
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

        return dc.replace(
            task,
            density=density,
            effective_density=effective_density if task.is_active else 0,
        )

    def _calculate_active_state(self, task: Task) -> Task:
        """
        Set the task active state at the given time
        """
        return dc.replace(
            task,
            is_active=bool(
                task.activation_time.replace(
                    tzinfo=None,
                )
                <= self._current_time.replace(
                    tzinfo=None,
                )
            ),
        )

    def _ensure_valid_state(self, task: Task) -> Task:
        """
        Given a task, ensure that it's state is valid by calculating
        its density and is_active state
        """
        return pipe(
            self._calculate_active_state,
            self._calculate_density,
        )(task)


class StateChange(TaskFunction):
    def __init__(self, current_time: datetime) -> None:
        self._current_time = current_time

    def _transform(self, task: Task) -> Task:
        raise NotImplementedError()

    def __call__(self, task: Task) -> Task:
        return pipe(self._transform, self._ensure_valid_state)(task)


class CreateTask(TaskFunction):
    def __call__(
        self,
        name: str,
        importance: int,
        time: int,
        task_type: TaskType,
        activation_time: datetime,
    ) -> Task:
        t = Task(
            id=uuid.uuid4(),
            name=name,
            importance=importance,
            time=time,
            task_type=task_type,
            is_prerequisite_for=(),
            activation_time=activation_time,
            is_active=False,
        )
        return self._ensure_valid_state(t)


class AddDependentTasks(StateChange):
    def __init__(self, current_time: datetime, dependent_tasks: List[Task]) -> None:
        super().__init__(current_time)
        self._dependent_tasks = dependent_tasks

    def _transform(self, task: Task) -> Task:
        """
        Add dependent tasks to the given task.
        """
        existing_dependency_ids = set(t.id for t in task.is_prerequisite_for)
        new_dependents_to_add = [
            DependentTask.from_task(t)
            for t in self._dependent_tasks
            if t.id not in existing_dependency_ids
        ]

        result = dc.replace(
            task,
            is_prerequisite_for=(
                *task.is_prerequisite_for,
                *new_dependents_to_add,
            ),
        )
        return result


class RemoveDependentTasks(StateChange):
    def __init__(self, current_time: datetime, dependent_tasks: List[Task]) -> None:
        super().__init__(current_time)
        self._dependent_tasks = dependent_tasks

    def _transform(self, task: Task) -> Task:
        """
        Remove dependent tasks from a given task
        """
        remove_ids = [t.id for t in self._dependent_tasks]
        result = dc.replace(
            task,
            is_prerequisite_for=tuple(
                t for t in task.is_prerequisite_for if t.id not in remove_ids
            ),
        )
        return result


__all__ = [
    "TaskType",
    "Task",
]
