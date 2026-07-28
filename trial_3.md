Welcome to the first milestone of our Todo application!
### Milestone 1: The Data Model
Our goal here is to define the "DNA" of a task. Before we can save tasks to a file or interact with them via the command line, we need to decide exactly what a "Task" looks like in our code. By defining a clear structure now, we avoid "data chaos" later when we start adding, deleting, or updating items.
We will use two components:
1. **`dataclass`**: A Python feature that acts as a blueprint for our task objects.
2. **`TodoList`**: A container class to hold our collection of tasks.
---
### Step 1: Defining the Task structure
In Python, a `dataclass` is a great way to store data. Think of it like a formal template for an object—it ensures that every task has the exact same fields, making our code predictable.
```python
from dataclasses import dataclass
from typing import Optional
@dataclass
class Task:
    title: str
    status: bool = False  # False means incomplete, True means complete
    due_date: Optional[str] = None
```
**Why use a `dataclass`?**
I chose this over a standard dictionary because it provides "type hinting" (e.g., `title: str`). This helps your code editor catch bugs before you even run the program. An alternative would be using a simple dictionary (e.g., `{"title": "Buy milk"}`), but dictionaries are prone to typos like `task["titel"]` instead of `task["title"]`, which would crash your program at runtime. Dataclasses catch those errors much earlier.
---
### Step 2: The TodoList container
Now we need a place to store these tasks. We’ll create a class that manages a list of `Task` objects.
```python
class TodoList:
    def __init__(self):
        self.tasks: list[Task] = []
    def add_task(self, task: Task):
        self.tasks.append(task)
```
**Why a container class?**
You might wonder why we don't just use a global `list` variable. By wrapping the list inside a `TodoList` class, we create a "single source of truth." If we ever decide to change how tasks are stored—for example, if we wanted to sort them automatically by date—we only have to change the logic inside this class, rather than hunting through our entire codebase to find every place where we used a list.
---
### Milestone Check
*   [x] Defined the `Task` dataclass with title, status, and optional due date.
*   [x] Defined a `TodoList` container to hold the tasks.
### 🤔 Reflective Question
If we decided later that a task should also have a "priority" level (like 'High', 'Medium', or 'Low'), how would using a `dataclass` make that change easier to manage compared to using a dictionary?
