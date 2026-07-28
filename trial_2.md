Welcome! I'm excited to help you build this Todo application.
### Milestone 1: The Data Model
Our goal for this milestone is to define the "blueprint" for our tasks. Before we can save tasks to a file or interact with them via the command line, we need to decide what a "Task" actually looks like in our code.
We are going to use a Python **dataclass**. Think of a dataclass as a formal template for an object. Instead of just using a loose dictionary (which can be messy and prone to typos), a dataclass allows us to define exactly which fields a task must have, what their types are, and even give them default values.
#### Step 1: Defining the Task
We’ll start by importing `dataclass` and defining our structure.
```python
from dataclasses import dataclass
from typing import Optional
@dataclass
class Task:
    title: str
    status: bool = False  # False means 'incomplete', True means 'complete'
    due_date: Optional[str] = None
```
**Why this approach?**
I chose a `dataclass` because it automatically generates helpful methods for us (like a way to print the object nicely) and makes our code much more readable than using a standard dictionary.
*Alternative considered:* We could have used a standard Python `class` with an `__init__` method. However, that requires writing a lot of "boilerplate" code just to assign variables to `self`. The `dataclass` decorator handles that for us, keeping our code clean and focused.
**What we did:**
1. We imported `dataclass` to enable the template functionality.
2. We defined `title` as a mandatory string.
3. We set `status` to default to `False` (new tasks aren't finished yet).
4. We used `Optional[str]` for the `due_date`, meaning it can be a string or `None`.
Does the distinction between a mandatory field (like `title`) and a field with a default value (like `status`) make sense to you?
### 🤔 Reflective Question
If we decided later that every task *must* have a `priority` level (e.g., "High", "Medium", "Low"), how would you modify the `Task` dataclass to ensure that a task cannot be created without a priority?
