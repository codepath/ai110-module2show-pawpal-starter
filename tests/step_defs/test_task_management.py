"""Step definitions for task_management.feature — drives real objects only."""

from datetime import date

from pytest_bdd import given, parsers, scenarios, then, when

from pawpal_system import Owner, Pet, Task

scenarios("../features/task_management.feature")


@given("an owner with a dog named Mochi", target_fixture="owner")
def owner_with_dog() -> Owner:
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))
    return owner


@given(parsers.parse('Mochi has a "{description}" task at "{time}"'))
def pet_has_task(owner: Owner, description: str, time: str):
    owner.get_pet("Mochi").add_task(
        Task(description=description, time=time, date=date.today())
    )


@when(parsers.parse('the owner schedules a "{description}" at "{time}" for Mochi'))
def schedule_task(owner: Owner, description: str, time: str):
    owner.get_pet("Mochi").add_task(
        Task(description=description, time=time, date=date.today())
    )


@when(parsers.parse('the owner marks the "{description}" task complete'))
def complete_task(owner: Owner, description: str):
    task = next(
        t for t in owner.get_pet("Mochi").list_tasks() if t.description == description
    )
    task.mark_complete()


@then(parsers.parse("Mochi has {count:d} task on their list"))
def pet_task_count(owner: Owner, count: int):
    assert len(owner.get_pet("Mochi").list_tasks()) == count


@then(parsers.parse('the "{description}" task is completed'))
def task_is_completed(owner: Owner, description: str):
    task = next(
        t for t in owner.get_pet("Mochi").list_tasks() if t.description == description
    )
    assert task.completed is True
