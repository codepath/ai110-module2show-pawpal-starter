"""Core behavior suite for the PawPal+ logic layer (real objects, no mocks)."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


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


def two_pet_household() -> Owner:
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")
    mochi.add_task(make_task("Morning walk", "08:00"))
    whiskers.add_task(make_task("Feeding", "09:00"))
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    return owner


def test_scheduler_collects_tasks_across_multiple_pets():
    scheduler = Scheduler(two_pet_household())
    pet_names = {pet.name for pet, _task in scheduler.all_tasks()}
    assert pet_names == {"Mochi", "Whiskers"}


def test_tasks_for_today_excludes_future_days():
    from datetime import timedelta

    owner = two_pet_household()
    owner.get_pet("Mochi").add_task(
        make_task("Vet visit", "10:00", date=date.today() + timedelta(days=3))
    )
    descriptions = [
        task.description for _pet, task in Scheduler(owner).tasks_for_today()
    ]
    assert "Vet visit" not in descriptions


def test_tasks_for_today_includes_all_today_tasks():
    from datetime import timedelta

    owner = two_pet_household()
    owner.get_pet("Mochi").add_task(
        make_task("Vet visit", "10:00", date=date.today() + timedelta(days=3))
    )
    descriptions = [
        task.description for _pet, task in Scheduler(owner).tasks_for_today()
    ]
    assert len(descriptions) == 2
