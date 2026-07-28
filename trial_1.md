Welcome to the project! I'm excited to help you build this Todo application.
### Milestone 1: Data Model
Our goal for this milestone is to define the "shape" of our data. Before we can save or update tasks, we need to decide exactly what a "Task" looks like in our code. By the end of this milestone, we will have a blueprint that ensures every task has a consistent structure.
We will use Python's `dataclasses` module for this. A `dataclass` is a special type of class designed specifically for storing data. It removes the "boilerplate" code (like writing an `__init__` method manually) that is usually required to create objects.
#### Step 1: Defining the Task
Let's start by defining our `Task` structure.
```python
from dataclasses import dataclass
from typing import Optional
@dataclass
class Task:
    title: str
    status: str = "pending"
    due_date: Optional[str] = None
```
**Why `dataclasses`?**
I chose `dataclasses` because they are lightweight and readable. An alternative would be using a simple dictionary (e.g., `{"title": "Buy milk", "status": "pending"}`), but dictionaries are prone to typos (like typing `titel` instead of `title`) and don't provide the helpful type-hinting that `dataclasses` offer. By using a class, we create a "contract"—every task is guaranteed to have these specific fields.
**Why `Optional`?**
We use `Optional[str]` for the `due_date` because not every task requires a deadline. This tells Python (and other developers reading your code) that this field might be a string, or it might be `None`.
---
### 🤔 Reflective Question
If we decided later that every task *must* have a unique ID number, how do you think adding that field to our `Task` dataclass would change the way we create new tasks in our code?
