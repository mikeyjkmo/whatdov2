from datetime import datetime, timedelta

import pytest

from whatdo2.domain.task.core import (
    AddDependentTasks,
    CreateTask,
    RemoveDependentTasks,
    TaskType,
)
from whatdo2.domain.task.typedefs import DependentTask
from whatdo2.domain.utils import pipe

create_task = CreateTask(current_time=datetime.now() + timedelta(days=1))


@pytest.mark.parametrize(
    "importance, time, expected_density",
    [
        (
            5,  # Importance
            5,  # Time
            1.0,  # Density
        ),
        (
            5,  # Importance
            10,  # Time
            0.5,  # Density
        ),
        (
            8,  # Importance
            5,  # Time
            1.6,  # Density
        ),
    ],
)
def test_created_task_has_correct_density(
    importance: int,
    time: int,
    expected_density: float,
) -> None:
    """
    Given a name, importance, time + task_type
    When we create a new task
    Then we should get a task with the expected density and effective density,
      which will be the same.
    """
    container = create_task(
        name="hello",
        importance=importance,
        time=time,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )

    assert container.task.density == expected_density
    assert container.task.effective_density == expected_density


def test_task_takes_max_density_of_dependents_and_self() -> None:
    """
    Given a task When we make it a prerequisite of other tasks
    Then the task's effective_density should be the maximum of its own
      and all of its dependent tasks and the task's density shall remain
      the same

    NOTE: if it's taking on the density of one of the dependent tasks,
    then there will be a margin of 0.1 added to it, to ensure that
    the task is higher priority than those that depend on it.
    """
    container = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )

    t2 = create_task(
        name="hello",
        importance=8,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    ).task
    t3 = create_task(
        name="hello",
        importance=4,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    ).task

    container = AddDependentTasks(
        current_time=datetime.now(),
        dependent_tasks=[t2, t3],
    )(container)

    assert container.task.is_prerequisite_for == (
        DependentTask.from_task(t2),
        DependentTask.from_task(t3),
    )
    assert container.task.effective_density == pytest.approx(1.7)
    assert container.task.density == 1.0


def test_task_takes_max_density_of_effective_density() -> None:
    """
    Given two tasks, both with dependent tasks
    When we make the first one a prerequisite of the other
    Then the task's effective_density should be the maximum of its own and the other's
      effective density
    """
    container = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )
    container2 = create_task(
        name="hello",
        importance=4,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )

    t3 = create_task(
        name="hello",
        importance=8,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    ).task

    container2 = AddDependentTasks(
        current_time=datetime.now(),
        dependent_tasks=[t3],
    )(container2)

    container = AddDependentTasks(
        current_time=datetime.now(),
        dependent_tasks=[container2.task],
    )(container)

    assert container.task.is_prerequisite_for == (
        DependentTask.from_task(container2.task),
    )
    assert container.task.effective_density == pytest.approx(1.8)
    assert container.task.density == 1.0


def test_task_cannot_depend_on_another_one_more_than_once() -> None:
    """
    Given a task with a dependency
    When we make it a prerequisite of the same dependency
    Then dependents for the task will not change
    """
    container = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )
    t2 = create_task(
        name="hello",
        importance=8,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    ).task

    add_dependent_task = AddDependentTasks(
        current_time=datetime.now(),
        dependent_tasks=[t2],
    )
    container = pipe(add_dependent_task, add_dependent_task)(container)

    assert container.task.is_prerequisite_for == (DependentTask.from_task(t2),)
    assert container.task.effective_density == pytest.approx(1.7)
    assert container.task.density == 1.0


def test_removing_dependent_task_leads_to_correct_density() -> None:
    """
    Given a task with a dependency
    When we remove the dependency
    Then the task's density should be recalculated correctly
    """
    container = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )
    t2 = create_task(
        name="hello",
        importance=8,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    ).task

    container = pipe(
        AddDependentTasks(current_time=datetime.now(), dependent_tasks=[t2]),
        RemoveDependentTasks(current_time=datetime.now(), dependent_tasks=[t2]),
    )(container)

    assert container.task.is_prerequisite_for == ()
    assert container.task.effective_density == 1.0
    assert container.task.density == 1.0


def test_task_will_ignore_effective_density_of_inactive_tasks() -> None:
    """
    Given two tasks, one the denser of the two being inactive
    When we make the denser one dependent on the other
    The density of the other will not change
    """
    container = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )
    inactive_task = create_task(
        name="hello",
        importance=8,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now() + timedelta(days=1),
    ).task

    container = AddDependentTasks(
        current_time=datetime.now(), dependent_tasks=[inactive_task]
    )(container)

    assert container.task.is_prerequisite_for == (
        DependentTask.from_task(inactive_task),
    )
    assert container.task.effective_density == 1.0  # unchanged
    assert container.task.density == 1.0


def test_task_will_have_effective_density_of_zero_if_it_is_inactive() -> None:
    inactive_task = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now() + timedelta(days=1),
    ).task
    assert inactive_task.effective_density == 0
