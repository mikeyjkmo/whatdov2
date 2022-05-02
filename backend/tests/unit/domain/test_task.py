from whatdo2.domain.task.typedefs import DependentTask
import pytest
from datetime import datetime, timedelta
from whatdo2.domain.task.public import (
    create_task,
    TaskType,
    is_task_active_at,
    make_prerequisite_of,
    remove_as_prequisite_of,
)


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
    t1 = create_task(
        name="hello",
        importance=importance,
        time=time,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )
    assert t1.density == expected_density
    assert t1.effective_density == expected_density


def test_task_takes_max_density_of_dependents_and_self() -> None:
    """
    Given a task
    When we make it a prerequisite of other tasks
    Then the task's effective_density should be the maximum of its own
      and all of its dependent tasks and the task's density shall remain
      the same
    """
    t1 = create_task(
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
    )
    t3 = create_task(
        name="hello",
        importance=4,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )

    t = make_prerequisite_of(t1, [t2, t3])

    assert t.is_prerequisite_for == (
        DependentTask.from_task(t2),
        DependentTask.from_task(t3),
    )
    assert t.effective_density == 1.6
    assert t.density == 1.0


def test_task_takes_max_density_of_effective_density() -> None:
    """
    Given two tasks, both with dependent tasks
    When we make the first one a prerequisite of the other
    Then the task's effective_density should be the maximum of its own and the other's
      effective density
    """
    t1 = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )
    t2 = create_task(
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
    )

    t2 = make_prerequisite_of(t2, [t3])
    t = make_prerequisite_of(t1, [t2])

    assert t.is_prerequisite_for == (
        DependentTask.from_task(t2),
    )
    assert t.effective_density == 1.6
    assert t.density == 1.0


def test_task_cannot_depend_on_another_one_more_than_once() -> None:
    """
    Given a task with a dependency
    When we make it a prerequisite of the same dependency
    Then dependents for the task will not change
    """
    t1 = create_task(
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
    )

    t1 = make_prerequisite_of(t1, [t2])
    t1 = make_prerequisite_of(t1, [t2])

    assert t1.is_prerequisite_for == (DependentTask.from_task(t2),)
    assert t1.effective_density == 1.6
    assert t1.density == 1.0


def test_removing_dependent_task_leads_to_correct_density() -> None:
    """
    Given a task with a dependency
    When we remove the dependency
    Then the task's density should be recalculated correctly
    """
    t1 = create_task(
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
    )

    t1 = make_prerequisite_of(t1, [t2])
    t1 = remove_as_prequisite_of(t1, [t2])

    assert t1.is_prerequisite_for == ()
    assert t1.effective_density == 1.0
    assert t1.density == 1.0


def test_task_should_be_active_if_activation_time_is_in_the_past() -> None:
    """
    Given a task created with activation_time = now
    When we call is_task_active_at now + 1 day
    Then the result should be true
    """
    t1 = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now(),
    )
    assert is_task_active_at(t1, datetime.now() + timedelta(days=1))


def test_task_should_be_inactive_if_activation_time_is_in_the_future() -> None:
    """
    Given a task created with activation_time = now + 1 day
    When we call is_task_active_at now
    Then the result should be false
    """
    t1 = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=datetime.now() + timedelta(days=1),
    )
    assert not is_task_active_at(t1, datetime.now())
