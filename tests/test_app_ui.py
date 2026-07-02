"""End-to-end UI tests: drive the real Streamlit app via AppTest (no mocks)."""

import datetime

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app() -> AppTest:
    # Generous timeout: the first run on a cold cache (fresh CI runner) compiles
    # imports and can exceed AppTest's 3s default.
    return AppTest.from_file("app.py", default_timeout=30).run()


def add_pet(app: AppTest, name: str) -> AppTest:
    app.text_input(key="pet_name").input(name)
    app.button(key="add_pet").click().run()
    return app


def add_task(app: AppTest, pet: str, description: str, time: datetime.time) -> AppTest:
    app.selectbox(key="task_pet").select(pet)
    app.text_input(key="task_description").input(description)
    app.time_input(key="task_time").set_value(time)
    app.button(key="add_task").click().run()
    return app


def test_adding_a_pet_creates_a_real_pet_object(app: AppTest):
    add_pet(app, "Rex")
    assert [pet.name for pet in app.session_state["owner"].pets] == ["Rex"]


def test_added_task_reaches_the_logic_layer(app: AppTest):
    add_pet(app, "Rex")
    add_task(app, "Rex", "Morning walk", datetime.time(8, 0))
    tasks = app.session_state["owner"].get_pet("Rex").list_tasks()
    assert [(t.description, t.time) for t in tasks] == [
        ("Morning walk", datetime.time(8, 0))
    ]


def test_schedule_table_shows_tasks_sorted_by_time(app: AppTest):
    add_pet(app, "Rex")
    add_pet(app, "Whiskers")
    add_task(app, "Rex", "Evening walk", datetime.time(18, 30))
    add_task(app, "Whiskers", "Feeding", datetime.time(9, 0))
    table = app.table[0].value
    assert list(table["Time"]) == ["09:00", "18:30"]


def test_same_time_tasks_show_a_conflict_warning(app: AppTest):
    add_pet(app, "Rex")
    add_pet(app, "Whiskers")
    add_task(app, "Rex", "Walk", datetime.time(8, 0))
    add_task(app, "Whiskers", "Meds", datetime.time(8, 0))
    warnings = " ".join(w.value for w in app.warning)
    assert "Conflict at 08:00" in warnings


def test_order_by_priority_puts_high_priority_task_first(app: AppTest):
    add_pet(app, "Rex")
    add_task(app, "Rex", "Morning walk", datetime.time(8, 0))
    app.selectbox(key="task_pet").select("Rex")
    app.text_input(key="task_description").input("Vet visit")
    app.time_input(key="task_time").set_value(datetime.time(16, 0))
    app.selectbox(key="task_priority").select("high")
    app.button(key="add_task").click().run()
    app.radio(key="order_by").set_value("Priority").run()
    table = app.table[0].value
    assert list(table["Task"]) == ["Vet visit", "Morning walk"]


def test_find_slot_reports_first_free_time(app: AppTest):
    add_pet(app, "Rex")
    add_task(app, "Rex", "Morning walk", datetime.time(7, 0))
    app.button(key="find_slot").click().run()
    assert "07:15" in app.info[0].value


def test_completing_a_recurring_task_marks_it_complete(app: AppTest):
    add_pet(app, "Rex")
    app.selectbox(key="task_pet").select("Rex")
    app.text_input(key="task_description").input("Feeding")
    app.time_input(key="task_time").set_value(datetime.time(9, 0))
    app.selectbox(key="task_frequency").select("daily")
    app.button(key="add_task").click().run()
    app.button(key="mark_complete").click().run()
    rex_tasks = app.session_state["owner"].get_pet("Rex").list_tasks()
    assert rex_tasks[0].completed is True


def test_completing_a_recurring_task_adds_follow_up(app: AppTest):
    add_pet(app, "Rex")
    app.selectbox(key="task_pet").select("Rex")
    app.text_input(key="task_description").input("Feeding")
    app.time_input(key="task_time").set_value(datetime.time(9, 0))
    app.selectbox(key="task_frequency").select("daily")
    app.button(key="add_task").click().run()
    app.button(key="mark_complete").click().run()
    rex_tasks = app.session_state["owner"].get_pet("Rex").list_tasks()
    assert len(rex_tasks) == 2


def test_completing_a_recurring_task_reschedules_for_tomorrow(app: AppTest):
    add_pet(app, "Rex")
    app.selectbox(key="task_pet").select("Rex")
    app.text_input(key="task_description").input("Feeding")
    app.time_input(key="task_time").set_value(datetime.time(9, 0))
    app.selectbox(key="task_frequency").select("daily")
    app.button(key="add_task").click().run()
    app.button(key="mark_complete").click().run()
    rex_tasks = app.session_state["owner"].get_pet("Rex").list_tasks()
    assert rex_tasks[1].date == datetime.date.today() + datetime.timedelta(days=1)


def test_app_save_creates_json_file(app: AppTest, tmp_path):
    app.text_input(key="owner_name").input("Alex").run()
    add_pet(app, "Fido")
    save_file = tmp_path / "app_data.json"
    app.text_input(key="save_path").input(str(save_file)).run()
    app.button(key="save_btn").click().run()
    assert save_file.exists()


def test_app_load_restores_owner_name(app: AppTest, tmp_path):
    app.text_input(key="owner_name").input("Alex").run()
    add_pet(app, "Fido")
    save_file = tmp_path / "app_data.json"
    app.text_input(key="save_path").input(str(save_file)).run()
    app.button(key="save_btn").click().run()
    app.text_input(key="owner_name").input("Jordan").run()
    app.button(key="load_btn").click().run()
    assert app.session_state["owner"].name == "Alex"


def test_app_load_restores_pet_object(app: AppTest, tmp_path):
    app.text_input(key="owner_name").input("Alex").run()
    add_pet(app, "Fido")
    save_file = tmp_path / "app_data.json"
    app.text_input(key="save_path").input(str(save_file)).run()
    app.button(key="save_btn").click().run()
    app.text_input(key="owner_name").input("Jordan").run()
    app.button(key="load_btn").click().run()
    assert app.session_state["owner"].get_pet("Fido") is not None
