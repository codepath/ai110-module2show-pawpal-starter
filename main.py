from pawpal_system import CareTask, DailySchedule, Owner, Pet


def main():
    owner = Owner(name="Jordan", available_minutes=60)

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(CareTask("Morning walk", 30, "high"))
    mochi.add_task(CareTask("Breakfast", 10, "high"))
    luna.add_task(CareTask("Playtime", 15, "medium"))
    luna.add_task(CareTask("Feed Luna", 5, "high"))

    print("Today's Schedule")
    for pet in owner.pets:
        schedule = DailySchedule(pet=pet)
        schedule.generate(owner)
        print()
        print(schedule.get_summary())


if __name__ == "__main__":
    main()
