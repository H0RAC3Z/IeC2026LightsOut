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

Finally, JavaScript applies the returned values to the existing buttons, updates their `on`/`off` classes, and updates the move count. The board and counter are session values, so they persist across page requests for the same browser session.

The small supporting endpoints are:

- `/reset/` creates a fresh board and resets the move count.
- `/hint/` finds and returns one move from a solution without changing the board or move count.
