"""Core behavior suite for the PawPal+ logic layer (real objects, no mocks)."""

from datetime import date

from pawpal_system import Owner, Pet, Task


def make_task(description: str = "Morning walk", time: str = "08:00", **kwargs) -> Task:
    return Task(
        description=description,
        time=time,
        date=kwargs.pop("date", date.today()),
        **kwargs
    )


def test_mark_complete_changes_task_status():
    task = make_task()
    task.mark_complete()
    assert task.completed is True


def test_new_task_starts_incomplete():
    assert make_task().completed is False


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(make_task())
    assert len(pet.list_tasks()) == 1


def test_pending_tasks_excludes_completed_ones():
    pet = Pet(name="Mochi", species="dog")
    done = make_task("Feeding", "09:00")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task("Evening walk", "18:00"))
    assert [t.description for t in pet.pending_tasks()] == ["Evening walk"]


def test_owner_add_and_get_pet():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    owner.add_pet(mochi)
    assert owner.get_pet("Mochi") is mochi


def test_get_pet_returns_none_for_unknown_name():
    assert Owner(name="Jordan").get_pet("Ghost") is None
