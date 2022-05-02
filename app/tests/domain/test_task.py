import pytest
from datetime import datetime, timedelta
from whatdo2.domain.task.public import (
    create_task,
    TaskType,
    is_task_active_at,
    make_dependent_on,
    remove_dependencies,
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
def test_created_task_has_correct_density(importance, time, expected_density):
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


def test_task_takes_max_density_of_dependencies_and_self():
    """
    Given a task
    When we make it dependent on other tasks
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

    t = make_dependent_on(t1, [t2, t3])

    assert t.depends_on == (t2, t3)
    assert t.effective_density == 1.6
    assert t.density == 1.0


def test_task_cannot_depend_on_another_one_more_than_once():
    """
    Given a task with a dependency
    When we make it dependent on the same dependency
    Then dependencies for the task will not change
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

    t1 = make_dependent_on(t1, [t2])
    t1 = make_dependent_on(t1, [t2])

    assert t1.depends_on == (t2,)
    assert t1.effective_density == 1.6
    assert t1.density == 1.0


def test_removing_dependent_task_leads_to_correct_density():
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

    t1 = make_dependent_on(t1, [t2])
    t1 = remove_dependencies(t1, [t2])

    assert t1.depends_on == ()
    assert t1.effective_density == 1.0
    assert t1.density == 1.0


def test_task_should_be_active_if_activation_time_is_in_the_past():
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


def test_task_should_be_inactive_if_activation_time_is_in_the_future():
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
