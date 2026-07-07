from pawpal_system import Task, Pet, Owner, Scheduler

mochi = Pet("Mochi", 8.5, "brown", "labrador")
mochi.add_task(Task("Morning walk", "08:00", "daily"))
mochi.add_task(Task("Vet checkup", "10:00", "once"))

whiskers = Pet("Whiskers", 4.2, "gray", "tabby")
whiskers.add_task(Task("Litter box cleaning", "09:00", "daily"))

owner = Owner({"name": "Jordan"}, [mochi, whiskers])
scheduler = Scheduler(owner)

print("Today's Schedule")
print(scheduler.explain_plan())
