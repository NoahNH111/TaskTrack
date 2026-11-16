"""
TaskTrack: a simple personal to-do list website for CISC 106.

This program uses Drafter routes, dataclasses, form inputs, loops,
conditionals, and state updates.
"""

from dataclasses import dataclass
from drafter import *


# Global constants are allowed by the project requirements.
APP_NAME = "TaskTrack"
PRIORITIES = ["Low", "Medium", "High"]
PRIORITY_FILTERS = ["All", "Low", "Medium", "High"]


@dataclass
class Task:
    """Store the information for one task."""
    task_id: int
    title: str
    description: str
    priority: str
    completed: bool


@dataclass
class State:
    """Store all information the website needs between routes."""
    tasks: list[Task]
    username: str
    selected_priority: str
    status_message: str
    next_task_id: int


def navigation() -> list:
    """Create the navigation links shown on every page."""
    return [
        Link("Home", index),
        " | ",
        Link("Add a task", add_task),
        " | ",
        Link("All tasks", all_tasks),
        " | ",
        Link("Pending", pending_tasks),
        " | ",
        Link("Completed", completed_tasks),
        " | ",
        Link("Priority", priority_tasks),
        " | ",
        Link("About", about),
        HorizontalRule()
    ]


def add_status_message(state: State, content: list) -> None:
    """Add a status message to a page when one is available."""
    if state.status_message != "":
        content.append(state.status_message)
        content.append("\n")


def task_list_content(state: State, mode: str) -> list:
    """Build the task display for all, pending, completed, or priority tasks."""
    content = []
    found_task = False

    # This loop meaningfully checks every Task instance in the State list.
    for task in state.tasks:
        show_task = False

        if mode == "all":
            show_task = True
        elif mode == "pending" and not task.completed:
            show_task = True
        elif mode == "completed" and task.completed:
            show_task = True
        elif mode == "priority":
            if state.selected_priority == "All":
                show_task = True
            elif task.priority == state.selected_priority:
                show_task = True

        if show_task:
            found_task = True
            content.append("Task #" + str(task.task_id))
            content.append("\nTitle: " + task.title)
            content.append("\nDescription: " + task.description)
            content.append("\nPriority: " + task.priority)

            if task.completed:
                content.append("\nStatus: Completed")
                content.append(
                    Button(
                        "Reopen task",
                        task_action,
                        {"task_id": task.task_id, "action": "reopen"}
                    )
                )
            else:
                content.append("\nStatus: Pending")
                content.append(
                    Button(
                        "Mark complete",
                        task_action,
                        {"task_id": task.task_id, "action": "complete"}
                    )
                )

            content.append(
                Button(
                    "Delete task",
                    task_action,
                    {"task_id": task.task_id, "action": "delete"}
                )
            )
            content.append(HorizontalRule())

    if not found_task:
        content.append("No tasks found in this section yet.")

    return content


@route
def index(state: State) -> Page:
    """Show the home page and a short overview of the user's tasks."""
    content = navigation()
    content.append(Header(APP_NAME))
    content.append("Welcome, " + state.username + "!")
    content.append("\nYour personal space to organize everyday tasks.")
    content.append("\nTotal tasks: " + str(len(state.tasks)))

    pending_count = 0
    completed_count = 0

    for task in state.tasks:
        if task.completed:
            completed_count = completed_count + 1
        else:
            pending_count = pending_count + 1

    content.append("\nPending tasks: " + str(pending_count))
    content.append("\nCompleted tasks: " + str(completed_count))
    content.append("\n")
    add_status_message(state, content)

    content.append(Header("Change your display name"))
    content.append("Name: ")
    content.append(TextBox("new_username", state.username))
    content.append(Button("Save name", change_name))

    content.append("\n")
    content.append(Link("Add a new task", add_task))
    content.append(Link("View all tasks", all_tasks))

    return Page(state, content)


@route
def add_task(state: State) -> Page:
    """Show the form for creating a task."""
    content = navigation()
    content.append(Header("Add a New Task"))
    add_status_message(state, content)

    content.append("Task title:")
    content.append(TextBox("title"))
    content.append("\nDescription:")
    content.append(TextArea("description"))
    content.append("\nPriority:")
    content.append(SelectBox("priority", PRIORITIES, "Medium"))
    content.append("\n")
    content.append(Button("Save task", save_task))

    return Page(state, content)


@route
def save_task(
    state: State,
    title: str,
    description: str,
    priority: str
) -> Page:
    """Validate the form and add a new Task instance to State."""
    if title.strip() == "":
        state.status_message = "Please enter a task title."
        return add_task(state)

    if priority not in PRIORITIES:
        priority = "Medium"

    new_task = Task(
        state.next_task_id,
        title.strip(),
        description.strip(),
        priority,
        False
    )

    state.tasks.append(new_task)
    state.next_task_id = state.next_task_id + 1
    state.status_message = "Your task was added successfully."

    return all_tasks(state)


@route
def all_tasks(state: State) -> Page:
    """Display every task in the task list."""
    content = navigation()
    content.append(Header("All Tasks"))
    add_status_message(state, content)
    content.extend(task_list_content(state, "all"))
    return Page(state, content)


@route
def pending_tasks(state: State) -> Page:
    """Display tasks that have not been completed."""
    content = navigation()
    content.append(Header("Pending Tasks"))
    add_status_message(state, content)
    content.extend(task_list_content(state, "pending"))
    return Page(state, content)


@route
def completed_tasks(state: State) -> Page:
    """Display tasks that have been completed."""
    content = navigation()
    content.append(Header("Completed Tasks"))
    add_status_message(state, content)
    content.extend(task_list_content(state, "completed"))
    return Page(state, content)


@route
def priority_tasks(state: State) -> Page:
    """Show the priority filter and matching tasks."""
    content = navigation()
    content.append(Header("Tasks by Priority"))
    add_status_message(state, content)

    content.append("Choose which priority level to display:")
    content.append(
        SelectBox(
            "priority",
            PRIORITY_FILTERS,
            state.selected_priority
        )
    )
    content.append(Button("Apply filter", filter_tasks))
    content.append("\nShowing: " + state.selected_priority + " priority")
    content.append(HorizontalRule())
    content.extend(task_list_content(state, "priority"))

    return Page(state, content)


@route
def filter_tasks(state: State, priority: str) -> Page:
    """Save the selected priority filter and show matching tasks."""
    if priority in PRIORITY_FILTERS:
        state.selected_priority = priority
    else:
        state.selected_priority = "All"

    state.status_message = "Task filter updated."
    return priority_tasks(state)


@route
def task_action(state: State, task_id: int, action: str) -> Page:
    """Complete, reopen, or delete the task identified by task_id."""
    task_found = False

    if action == "delete":
        remaining_tasks = []

        for task in state.tasks:
            if task.task_id == task_id:
                task_found = True
            else:
                remaining_tasks.append(task)

        state.tasks = remaining_tasks

        if task_found:
            state.status_message = "Task deleted."
        else:
            state.status_message = "That task could not be found."

    elif action == "complete":
        for task in state.tasks:
            if task.task_id == task_id:
                task.completed = True
                task_found = True

        if task_found:
            state.status_message = "Task marked as completed."
        else:
            state.status_message = "That task could not be found."

    elif action == "reopen":
        for task in state.tasks:
            if task.task_id == task_id:
                task.completed = False
                task_found = True

        if task_found:
            state.status_message = "Task moved back to pending."
        else:
            state.status_message = "That task could not be found."

    else:
        state.status_message = "Unknown task action."

    return all_tasks(state)


@route
def change_name(state: State, new_username: str) -> Page:
    """Update the username shown on the home page."""
    if new_username.strip() == "":
        state.status_message = "Please enter a name before saving."
    else:
        state.username = new_username.strip()
        state.status_message = "Your name was updated."

    return index(state)


@route
def about(state: State) -> Page:
    """Explain the purpose and features of TaskTrack."""
    content = navigation()
    content.append(Header("About TaskTrack"))
    content.append(
        "TaskTrack is a simple personal to-do list website. "
        "It helps users organize tasks and keep track of their progress."
    )
    content.append("\n")
    content.append("You can use TaskTrack to:")
    content.append(BulletedList([
        "Create tasks with a title and description.",
        "Choose a Low, Medium, or High priority.",
        "Mark tasks as completed or reopen them.",
        "Delete tasks you no longer need.",
        "Filter tasks by priority."
    ]))
    content.append(
        "Note: this beginner project stores information in the current "
        "Drafter session. Reloading the page may reset the task list."
    )
    return Page(state, content)


# -------------------------
# Unit tests for the routes
# -------------------------
def run_tests() -> None:
    """Run basic tests for the website routes and state changes."""

    test_task = Task(1, "Read chapter", "Read the assigned chapter.", "High", False)
    test_state = State([test_task], "Student", "All", "", 2)

    assert_has(index(test_state), "TaskTrack")
    assert_has(add_task(test_state), "Add a New Task")
    assert_has(all_tasks(test_state), "Read chapter")
    assert_has(pending_tasks(test_state), "Read chapter")
    assert_has(completed_tasks(test_state), "No tasks found")
    assert_has(priority_tasks(test_state), "Tasks by Priority")
    assert_has(about(test_state), "About TaskTrack")

    added_state = State([], "Student", "All", "", 1)
    added_page = save_task(
        added_state,
        "Finish homework",
        "Complete the programming assignment.",
        "Medium"
    )
    assert_state(
        added_page,
        State(
            [Task(1, "Finish homework",
                  "Complete the programming assignment.", "Medium", False)],
            "Student",
            "All",
            "Your task was added successfully.",
            2
        )
    )

    filtered_state = State(
        [Task(1, "Read chapter", "Read the assigned chapter.", "High", False)],
        "Student",
        "All",
        "",
        2
    )
    filter_page = filter_tasks(filtered_state, "High")
    assert_state(
        filter_page,
        State(
            [Task(1, "Read chapter", "Read the assigned chapter.", "High", False)],
            "Student",
            "High",
            "Task filter updated.",
            2
        )
    )

    completed_state = State(
        [Task(1, "Read chapter", "Read the assigned chapter.", "High", False)],
        "Student",
        "All",
        "",
        2
    )
    task_action(completed_state, 1, "complete")
    assert_state(
        completed_state,
        State(
            [Task(1, "Read chapter", "Read the assigned chapter.", "High", True)],
            "Student",
            "All",
            "Task marked as completed.",
            2
        )
    )

    renamed_state = State([], "Student", "All", "", 1)
    change_name(renamed_state, "Alex")
    assert_state(
        renamed_state,
        State([], "Alex", "All", "Your name was updated.", 1)
    )

    deleted_state = State(
        [Task(1, "Read chapter", "Read the assigned chapter.", "High", False)],
        "Student",
        "All",
        "",
        2
    )
    task_action(deleted_state, 1, "delete")
    assert_state(
        deleted_state,
        State([], "Student", "All", "Task deleted.", 2)
    )

run_tests()

# Required website information for the project.
set_site_information(
    "Noah Hagos",
    "TaskTrack is a personal to-do list website built with Python and Drafter.",
    ["Drafter documentation: https://drafter-edu.github.io/drafter/"],
    "A personal task manager with task creation, priority filtering, "
    "completion tracking, and task deletion.",
    ["CISC 106 Final Project"]
)

start_server(
    State([], "Student", "All", "Welcome to TaskTrack!", 1),
    site_title="TaskTrack"
)
