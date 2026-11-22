from django.shortcuts import render
from django.views.decorators.http import require_POST
from .models import LightsOut
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import time

# game page
def index(request):
    obj = LightsOut()
    board = obj.generate_board()
    # Initialize board only if this is a new game
    if "board" not in request.session:
        request.session["board"] = board
    if "move_counter" not in request.session:
        request.session["move_counter"] = 0
    if "started_at" not in request.session:
        request.session["started_at"] = time.time()
    if "completed" not in request.session:
        request.session["completed"] = False

    elapsed = request.session.get("elapsed_seconds")
    if elapsed is None:
        elapsed = int(time.time() - request.session["started_at"])
    return render(request, "lightsOutApp/index.html", {
        "obj": obj,
        "board": request.session["board"],
        "move_counter": request.session["move_counter"],
        "elapsed_seconds": elapsed,
        "completed": request.session["completed"],
    })

# renders tutorial page template
def tutorial(request):
    return render(request, "lightsOutApp/tutorial.html")

@require_POST
def reset_view(request):
    obj = LightsOut()
    request.session["board"] = obj.generate_board()
    request.session["move_counter"] = 0
    request.session["started_at"] = time.time()
    request.session["completed"] = False
    request.session.pop("elapsed_seconds", None)
    return JsonResponse({"board": request.session["board"], "move_counter": 0, "elapsed_seconds": 0})

@require_POST
def hint_view(request):
    obj = LightsOut()
    board = request.session.get("board", obj.get_board())
    hint = obj.get_hint(board)
    return JsonResponse({"row": hint[0], "col": hint[1]} if hint else {"error": "No hint available"})

# View to handle the Ajax request
@require_POST
def ajax_view(request):
    obj = LightsOut()

    # Restore the existing board
    obj.board = request.session.get("board", obj.get_board()) # get board from session, default to new obj if not there

    try:
        data = json.loads(request.body)
        row = int(data["row"])
        col = int(data["col"])

        # Validate coordinates
        if not (0 <= row < len(obj.board)):
            return JsonResponse({"error": "Invalid row"}, status=400)

        if not (0 <= col < len(obj.board[row])):
            return JsonResponse({"error": "Invalid column"}, status=400)

        # Update game
        obj.set_board(obj.toggle(obj.get_board(), row, col))

        # Update move counter
        request.session["move_counter"] = request.session.get("move_counter", 0) + 1

        # Save updated board
        request.session["board"] = obj.get_board()
        elapsed = request.session.get("elapsed_seconds")
        if elapsed is None:
            elapsed = int(time.time() - request.session["started_at"])

        won = obj.is_solved(request.session["board"])
        if won:
            request.session["completed"] = True
            request.session["elapsed_seconds"] = elapsed

        return JsonResponse({
            "board": obj.get_board(),
            "won": won,
            "move_counter": request.session["move_counter"],
            "elapsed_seconds": elapsed,
        })

    except (KeyError, ValueError, TypeError, json.JSONDecodeError) as error:
        print("AJAX error:", error, request.body)
        return JsonResponse({"error": "Invalid request"}, status=400)
