# Lights Out

A small Django implementation of the Lights Out puzzle. Click a light to toggle it and its adjacent lights; the goal is to turn the complete board off.

## Quick setup and run

From the repository root:

```bash
cd lightsOut
python3 -m venv venv
source venv/bin/activate       # Windows: ..\venv\Scripts\activate
pip install django
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ in a browser. The tutorial is the landing screen; its continue button opens `/game/`. The project uses Django sessions for each browser's board and move count, so no model migration is needed for gameplay.

## File guide

- `lightsOut/manage.py` — Django command-line entry point for running the server and management commands.
- `lightsOut/lightsOut/settings.py` — installed apps, middleware, templates, sessions, database, and static-file settings.
- `lightsOut/lightsOut/urls.py` — includes the application URLs at the site root and exposes the admin route.
- `lightsOut/lightsOutApp/urls.py` — maps `/` to the game page and `/ajax/` to the move endpoint.
- `lightsOut/lightsOutApp/views.py` — creates the page response, stores the board and move count in the session, validates moves, and returns JSON.
- `lightsOut/lightsOutApp/models.py` — contains the `LightsOut` game logic: validating positions, toggling neighbours, and checking for a win. It is currently not backed by a database table (`managed = False`).
- `lightsOut/lightsOutApp/templates/lightsOutApp/index.html` — renders the board and uses `fetch()` to send each clicked cell to Django without reloading the page.
- `lightsOut/lightsOutApp/templates/lightsOutApp/tutorial.html` — the simple landing tutorial with the continue button.
- `lightsOut/lightsOutApp/static/css/style.css` — contains the centered game card, responsive five-by-five grid, tile states, and visual styling.
- `logic.py` — standalone copy of the core puzzle logic, useful for experimenting outside Django.

## Important code flow

The template gives every button its zero-based coordinates:

```html
data-row="{{ forloop.parentloop.counter0 }}"
data-col="{{ forloop.counter0 }}"
```

Clicking a button sends those coordinates as JSON. The CSRF header is required because this is a POST request:

```javascript
fetch("{% url 'lightsOutApp:ajax_view' %}", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": "{{ csrf_token }}"
    },
    body: JSON.stringify({
        row: Number(button.dataset.row),
        col: Number(button.dataset.col)
    })
});
```

The view restores the session board, creates a new board after the move, and returns it to the browser:

```python
obj.board = request.session.get("board", obj.get_board())
obj.board = obj.toggle(obj.board, row, col)
request.session["board"] = obj.board
```

The model keeps the puzzle rules modular. Each function has one responsibility:

### Validate a position

`is_valid_position()` rejects booleans and non-integers, then checks that the coordinates are inside the five-by-five grid. This keeps coordinate validation in one place for all other model functions.

```python
def is_valid_position(self, row, col):
    if isinstance(row, bool) or isinstance(col, bool):
        return False
    if not isinstance(row, int) or not isinstance(col, int):
        return False
    return 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE
```

### Toggle a cell and its neighbours

`toggle()` copies the board instead of changing the original. It then uses `offsets` to switch the selected cell and its four direct neighbours. Returning a new board makes the function reusable for player moves, board generation, and hint calculations.

```python
new_board = [list(row) for row in board]
for row_offset, col_offset in self.offsets:
    target_row = row + row_offset
    target_col = col + col_offset
    if self.is_valid_position(target_row, target_col):
        new_board[target_row][target_col] = 1 - new_board[target_row][target_col]
return new_board
```

### Check whether the puzzle is complete

`is_solved()` returns `True` only when every cell contains `LIGHTS_OFF`. The AJAX view uses this after each move to decide whether to stop the timer and show the completion message.

```python
def is_solved(self, board):
    return all(light == self.LIGHTS_OFF for row in board for light in row)
```

### Generate a solvable board

`generate_board()` begins with an all-off board and applies random valid toggles. Because every generated state comes from a sequence of legal moves, the result is solvable. The final check prevents the game from starting already completed.

```python
board = [[self.LIGHTS_OFF] * self.GRID_SIZE for _ in range(self.GRID_SIZE)]
for _ in range(random.randint(1, self.TOTAL_LIGHTS)):
    board = self.toggle(board, random.randrange(self.GRID_SIZE), random.randrange(self.GRID_SIZE))
return board
```

### Find a hint

`get_hint()` tests each possible combination of presses in the first row. Once a first-row combination is selected, every later row is forced: if a light is still on in the row above, the cell below it must be pressed because later presses cannot affect that row. When the resulting board is solved, the function returns the first move from that solution. It returns `None` if no solution is found.

### Keep board state separate from game rules

`get_board()` and `set_board()` provide simple access to the model’s current board. The view owns the player’s session state: the board, move count, timer start/completion data, and reset behavior. This separation means the model calculates puzzle states while the view decides how those states are stored and sent to the browser.

Finally, JavaScript applies the returned values to the existing buttons, updates their `on`/`off` classes, and updates the move count. The board and counter are session values, so they persist across page requests for the same browser session.

The small supporting endpoints are:

- `/reset/` creates a fresh board and resets the move count.
- `/hint/` finds and returns one move from a solution without changing the board or move count.

## Attributions and learning resources

These resources were used for guidance while developing the project:

- [Project discussion and guidance](https://chatgpt.com/share/6b03146f-5e58-83ea-92c5-c44a3e698a63) — discussion about adapting the AJAX requests to Django, handling sessions, and structuring the game flow.
- [Django Templates documentation](https://docs.djangoproject.com/en/6.1/topics/templates/) — reference for template rendering, variables, loops, and template tags.
- [Django official tutorial](https://docs.djangoproject.com/en/6.1/intro/tutorial01/) — guidance for the initial Django project structure, URL configuration, views, and development server.
- [GeeksforGeeks: Django Templates](https://www.geeksforgeeks.org/python/django-templates/) — supplementary examples for Django template syntax.
- [GeeksforGeeks: Accessing array elements in Django templates](https://www.geeksforgeeks.org/python/access-array-elements-in-a-django-template/) — reference for iterating through nested board data in a template.
- [GeeksforGeeks: Two-dimensional Python lists](https://www.geeksforgeeks.org/python/python-using-2d-arrays-lists-the-right-way/) — guidance for copying and working with nested board lists.
- [W3Schools: Django `if` tags](https://www.w3schools.com/django/django_tags_if.php) — supplementary reference for conditional styling of on and off tiles.
- [GeeksforGeeks: Integrating AJAX with Django](https://www.geeksforgeeks.org/python/how-to-integrate-ajax-with-django-applications/) — reference for sending asynchronous browser requests to Django views and returning JSON responses.
- [Python Guides: Run a Python function from an HTML button in Django](https://pythonguides.com/run-python-function-by-clicking-on-html-button-in-django/) — supplementary guidance for connecting HTML button clicks to Django-backed actions.

Codex used for debugging and filling in template.