# pyui + Counter Board

A tiny UI framework in **pure Python** (no JavaScript, no pip installs) and a counter board demo built only with it.

## Run
    python3 app.py      # then open http://localhost:8000

## Files
- `pyui.py` - the framework (~170 lines)
- `app.py`  - the Counter Board demo (uses only pyui)
- `static/wallpaper.jpg` - background image (served by pyui at `/static/wallpaper.jpg`)

## How it maps to the task
| Requirement | Where |
|---|---|
| 1. Components as a tree of elements with props | `Element`, `h()`, `div()`, `button()`... + components like `CounterCard()` in app.py |
| 2. Renderer -> HTML | `Renderer.render()` |
| 3. State -> UI updates | `State.set()`, then page re-renders from state every time |
| 4. Click -> state change -> re-render | `on_click` -> POST /event -> handler -> `state.set()` -> redirect -> re-render |
| 5. Demo app | Counter Board: add/delete counters, +1/-1/+5/reset, total, leader highlight |

## Design choice
Buttons become real HTML `<form>`s, so events go to the Python server (like Phoenix LiveView / htmx style).
Trade-off: full page reload per click - simple and explainable, not the fastest.
