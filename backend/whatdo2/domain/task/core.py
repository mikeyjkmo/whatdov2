import uuid
from dataclasses import replace as dc_replace, fields as dc_fields
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic.dataclasses import dataclass

from whatdo2.domain.task.events import TaskActivated, TaskDeactivated, TaskEvent
from whatdo2.domain.typedefs import Entity

PRIORITY_DENSITY_MARGIN = 0.1


class TaskType(str, Enum):
    HOME = "HOME"
    WORK = "WORK"


@dataclass(frozen=True)
class BaseTask(Entity):
    name: str
    importance: int
    task_type: TaskType
    time: int
    activation_time: datetime
    is_active: bool


@dataclass(frozen=True)
class DependentTask(BaseTask):
    density: float
    effective_density: float

    @classmethod
    def from_task(cls: Type["DependentTask"], t: "Task") -> "DependentTask":
        if t.density is None or t.effective_density is None:
            raise ValueError(
                "Initialized task cannot have None as density or effective_density",
            )

        return cls(
            id=t.id,
            name=t.name,
            importance=t.importance,
            task_type=t.task_type,
            time=t.time,
            activation_time=t.activation_time,
            is_active=t.is_active,
            density=t.density,
            effective_density=t.effective_density,
        )

    @classmethod
    def from_raw(cls: Type["DependentTask"], data: Dict[Any, Any]) -> "DependentTask":
        init_data = data.copy()
        init_data.pop("_id", None)
        init_data.pop("is_prerequisite_for", None)
        return cls(**init_data)


@dataclass(frozen=True)
class Task(BaseTask):
    density: Optional[float] = None
    effective_density: Optional[float] = None
    is_prerequisite_for: Tuple[DependentTask, ...] = ()
    events: Tuple[TaskEvent, ...] = ()

    @classmethod
    def new(
        cls: Type["Task"],
        name: str,
        importance: int,
        time: int,
        task_type: TaskType,
        activation_time: datetime,
        is_active: bool,
    ) -> "Task":
        return cls(
            id=uuid.uuid4(),
            name=name,
            importance=importance,
            time=time,
            task_type=task_type,
            is_prerequisite_for=(),
            activation_time=activation_time,
            is_active=is_active,
        ).ensure_valid_state()

    def _replace(self, **params: Any) -> "Task":
        """
        Create a new Task with the parameters replaced
        """
        return dc_replace(self, **params)

    @classmethod
    def from_raw(
        cls: Type["Task"],
        raw_task: Dict[Any, Any],
        raw_dependencies: Tuple[Dict[Any, Any], ...],
    ) -> "Task":
        raw_task["is_prerequisite_for"] = tuple(
            DependentTask.from_raw(t) for t in raw_dependencies
        )
        raw_task.pop("_id", None)
        return cls(**raw_task)

    @classmethod
    def from_orm(cls, orm: Any) -> "Task":
        fields = dc_fields(cls)
        constr_dict = {
            field.name: getattr(orm, field.name)
            for field in fields
            if hasattr(orm, field.name) and field.name != "is_prerequisite_for"
        }

        constr_dict["is_prerequisite_for"] = [
            DependentTask.from_orm(o) for o in getattr(
                orm,
                "is_prerequisite_for",
                (),
            )
        ]
        return cls(**constr_dict)

    def ensure_valid_state(self) -> "Task":
        """
        Given a task, return a new task with the calculated density
        """
        density = float(self.importance / self.time)
        max_density_of_dependent_tasks = max(
            [t.effective_density for t in self.is_prerequisite_for if t.is_active] + [0]
        )

        effective_density = density
        if max_density_of_dependent_tasks >= density:
            # If the density is smaller than the maximum of its dependent
            # tasks, this self should take on the density of that maximum, plus
            # a small margin -- this ensures that the self is more important
            # than those that depend on it, as it needs to be done first.
            effective_density = max_density_of_dependent_tasks + PRIORITY_DENSITY_MARGIN

        return self._replace(
            density=density,
            effective_density=effective_density if self.is_active else 0,
        )

    def add_dependent_tasks(self, dependent_tasks: List["Task"]) -> "Task":
        """
        Add dependent tasks to the given task.
        """
        existing_dependency_ids = set(t.id for t in self.is_prerequisite_for)
        new_dependents_to_add = [
            DependentTask.from_task(t)
            for t in dependent_tasks
            if t.id not in existing_dependency_ids
        ]

        return self._replace(
            is_prerequisite_for=(
                *self.is_prerequisite_for,
                *new_dependents_to_add,
            ),
        ).ensure_valid_state()

    def remove_dependent_tasks(self, dependent_tasks: List["Task"]) -> "Task":
        """
        Remove dependent tasks from a given task
        """
        remove_ids = [t.id for t in dependent_tasks]
        return self._replace(
            is_prerequisite_for=tuple(
                t for t in self.is_prerequisite_for if t.id not in remove_ids
            ),
        ).ensure_valid_state()

    def _determine_activation_events(
        self, original_is_active: bool, new_is_active: bool
    ) -> List[TaskEvent]:
        """
        Given the original and new is_active states, determine the domain
        events that have happened.
        """
        if original_is_active == new_is_active:
            return []

        if new_is_active:
            return [TaskActivated(self.id)]

        return [TaskDeactivated(self.id)]

    def update_is_active(self, current_time: datetime) -> "Task":
        """
        Update the is_active state of a Task based on the current_time
        """
        new_is_active = bool(
            current_time.replace(tzinfo=None)
            >= self.activation_time.replace(tzinfo=None)
        )
        new_events = self._determine_activation_events(
            self.is_active,
            new_is_active,
        )

        return self._replace(
            is_active=new_is_active,
            events=(*self.events, *new_events),
        ).ensure_valid_state()


__all__ = [
    "TaskType",
    "Task",
]
