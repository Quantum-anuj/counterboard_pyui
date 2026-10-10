"""Counter Board - demo app built ONLY with pyui (our own framework)."""
from pyui import App, State, div, span, h1, p, button, form, input_, select, option

CSS = """
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0}
.app{
  --bg1:#0a0f24;--bg2:#1b1147;--card:rgba(12,16,40,.55);--line:rgba(255,255,255,.14);
  --text:#f1f4ff;--muted:#9ea8cf;--btn:rgba(255,255,255,.10);--btn-h:rgba(255,255,255,.20);
  --track:rgba(255,255,255,.10);--shadow:rgba(0,0,0,.40);
  position:relative;min-height:100vh;padding:30px 18px 70px;color:var(--text);
  font-family:'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif}
/* wallpaper: fixed layer behind everything (works on mobile too) */
.app:before{content:"";position:fixed;left:0;top:0;right:0;bottom:0;z-index:-1;
  background-color:var(--bg1);
  background-image:
    linear-gradient(180deg,rgba(6,10,28,.45) 0%,rgba(6,10,28,.25) 45%,rgba(6,10,28,.60) 100%),
    url(/static/wallpaper.jpg);
  background-size:cover;background-position:center bottom;background-repeat:no-repeat}
.app.light{
  --bg1:#eef2ff;--bg2:#fdf2f8;--card:rgba(255,255,255,.80);--line:rgba(30,40,100,.10);
  --text:#1b2140;--muted:#5d6794;--btn:rgba(30,40,100,.07);--btn-h:rgba(30,40,100,.14);
  --track:rgba(30,40,100,.10);--shadow:rgba(60,70,140,.18)}
.app.light:before{background-image:linear-gradient(rgba(244,246,255,.78),rgba(250,244,252,.82)),url(/static/wallpaper.jpg)}
.wrap{max-width:1000px;margin:auto}

/* ---------- header ---------- */
.hero{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:26px;flex-wrap:wrap}
.brand h1{margin:0;font-size:clamp(30px,5.5vw,48px);font-weight:800;letter-spacing:-1.2px;
  background:linear-gradient(90deg,#22d3ee,#a78bfa 55%,#f472b6);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--muted);margin:6px 0 0;font-size:15px}
button.theme{border-radius:99px;padding:10px 18px;font-weight:600;border:1px solid var(--line)}

/* ---------- stats ---------- */
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:16px 18px;
  display:flex;align-items:center;gap:14px;box-shadow:0 10px 30px var(--shadow)}
.ico{font-size:26px;width:50px;height:50px;border-radius:15px;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,rgba(167,139,250,.40),rgba(34,211,238,.30))}
.lbl{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:1.3px}
.val{font-size:24px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:190px}

/* ---------- add form ---------- */
.add{display:flex;gap:10px;align-items:center;background:var(--card);border:1px solid var(--line);
  padding:8px;border-radius:22px;margin-bottom:28px;box-shadow:0 10px 30px var(--shadow);flex-wrap:wrap}
.add select,.add input{background:var(--btn);border:0;outline:0;color:var(--text);font-size:16px;
  border-radius:14px;padding:12px 14px;font-family:inherit}
.add select{cursor:pointer;font-size:20px;padding:10px 8px}
.add select option{color:#111;background:#fff}
.add input[name=name]{flex:1;min-width:150px}
.add input[name=goal]{width:130px}
.add input::placeholder{color:var(--muted)}
.add input:focus,.add select:focus{box-shadow:0 0 0 2px #a78bfa}
.add button{border-radius:14px;padding:13px 26px;font-weight:700;color:#0b1020;font-size:16px;
  background:linear-gradient(90deg,#22d3ee,#a78bfa)}
.add button:hover{filter:brightness(1.1)}

/* ---------- cards ---------- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(285px,1fr));gap:20px}
.card{--accent:#22d3ee;--rgb:34,211,238;position:relative;background:var(--card);border:1px solid var(--line);
  border-radius:26px;padding:20px;overflow:hidden;box-shadow:0 14px 36px var(--shadow);
  transition:transform .2s,box-shadow .2s;scroll-margin-top:90px}
.card:before{content:"";position:absolute;left:0;right:0;top:0;height:5px;background:var(--accent)}
.card:after{content:"";position:absolute;width:190px;height:190px;right:-70px;top:-70px;border-radius:50%;
  background:rgba(var(--rgb),.22);pointer-events:none}
.card:hover{transform:translateY(-4px);box-shadow:0 20px 44px var(--shadow)}
.card.leader{box-shadow:0 0 0 2px #facc15,0 0 44px rgba(250,204,21,.28)}

.top{display:flex;align-items:center;gap:12px;position:relative;z-index:1}
.badge{font-size:24px;width:46px;height:46px;border-radius:14px;display:flex;align-items:center;justify-content:center;
  background:rgba(var(--rgb),.22);flex:none}
.info{flex:1;min-width:0}
.name{font-weight:700;font-size:18px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.goal{font-size:12.5px;color:var(--muted);margin-top:2px}
.goal.done{color:#34d399;font-weight:700}

.ring-wrap{display:flex;justify-content:center;margin:20px 0 18px;position:relative;z-index:1}
.ring{--p:0;width:176px;height:176px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  background:conic-gradient(var(--accent) calc(var(--p) * 1%),var(--track) 0);
  box-shadow:0 0 34px rgba(var(--rgb),.35)}
.ring-in{width:146px;height:146px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  background:var(--bg1);}
.app.light .ring-in{background:#fff}
.value{font-size:60px;font-weight:800;color:var(--accent);line-height:1;animation:pop .35s ease}
@keyframes pop{0%{transform:scale(.6);opacity:.4}60%{transform:scale(1.15)}100%{transform:scale(1);opacity:1}}

.controls{display:flex;align-items:center;justify-content:center;gap:16px;position:relative;z-index:1}
.chips{display:flex;justify-content:center;gap:8px;margin-top:16px;position:relative;z-index:1}
.controls form,.chips form,.top form{display:contents}

/* ---------- buttons ---------- */
button{font-family:inherit;border:0;cursor:pointer;color:var(--text);font-size:15px;background:var(--btn);
  border-radius:12px;padding:8px 14px;transition:transform .12s,background .15s,filter .15s}
button:hover{background:var(--btn-h);transform:translateY(-1px)}
button:active{transform:scale(.93)}
button.round{width:62px;height:62px;border-radius:50%;font-size:30px;font-weight:700;padding:0;line-height:1}
button.plus,button.plus:hover{background:var(--accent);color:#0b1020}
button.plus:hover{filter:brightness(1.12)}
button.chip{font-size:13px;font-weight:600;padding:7px 15px;border-radius:99px;color:var(--muted)}
button.x{padding:4px 10px;font-size:14px;border-radius:9px;background:transparent;color:var(--muted)}
button.x:hover{background:rgba(239,68,68,.22);color:#ef4444}

.footer{text-align:center;margin-top:34px}
button.resetall{background:rgba(239,68,68,.14);color:#ef4444;border:1px solid rgba(239,68,68,.35);
  padding:11px 24px;border-radius:99px;font-weight:600}
button.resetall:hover{background:rgba(239,68,68,.26)}
.empty{text-align:center;color:var(--muted);padding:56px 10px;border:2px dashed var(--line);border-radius:26px;font-size:16px}
.empty .big{font-size:48px;margin-bottom:6px}

@media(max-width:640px){.stats{grid-template-columns:1fr}.val{max-width:none}.add input[name=goal]{width:100%}
  .add button{width:100%}.hero{justify-content:center;text-align:center}}
"""

PALETTE = [("#22d3ee", "34,211,238"), ("#a78bfa", "167,139,250"), ("#f472b6", "244,114,182"),
           ("#facc15", "250,204,21"), ("#34d399", "52,211,153"), ("#fb923c", "251,146,60")]
ICONS = ["💪", "☕", "💧", "📚", "💻", "🏃", "🎯", "⭐", "🎮", "🍎"]

state = State(
    theme="dark",
    counters=[{"id": 1, "name": "Push-ups", "icon": "💪", "goal": 50, "value": 0},
              {"id": 2, "name": "Chai cups", "icon": "☕", "goal": 5, "value": 0}],
    next_id=3,
)


# ----- event handlers: change data with state.set() -> UI re-renders -----
def change(cid, delta=None, reset=False):
    new = []
    for c in state.get("counters"):
        if c["id"] == cid:
            c = {**c, "value": 0 if reset else c["value"] + delta}
        new.append(c)
    state.set("counters", new)


def delete(cid):
    state.set("counters", [c for c in state.get("counters") if c["id"] != cid])


def add_counter(fields):
    name = fields.get("name", "").strip()
    if not name:
        return
    try:
        goal = max(0, int(fields.get("goal") or 0))
    except ValueError:
        goal = 0
    nid = state.get("next_id")
    new = {"id": nid, "name": name, "icon": fields.get("icon", "⭐"), "goal": goal, "value": 0}
    state.set("counters", state.get("counters") + [new])
    state.set("next_id", nid + 1)


def reset_all():
    state.set("counters", [{**c, "value": 0} for c in state.get("counters")])


def toggle_theme():
    state.set("theme", "light" if state.get("theme") == "dark" else "dark")


# ----- components (functions that return element trees) -----
def CounterCard(c, top):
    cid, value, goal = c["id"], c["value"], c["goal"]
    is_leader = top > 0 and value == top
    if goal > 0:
        pct, done = max(0, min(100, round(value / goal * 100))), value >= goal
        sub = "🎉 Goal reached!" if done else f"Goal: {goal}  ·  {pct}%"
    else:
        pct, done = (max(0, round(value / top * 100)) if top > 0 else 0), False
        sub = "No goal · vs leader"
    hex_, rgb = PALETTE[cid % len(PALETTE)]
    a = f"c{cid}"                                   # anchor: keeps scroll position after click
    return div(
        div(div(c["icon"], cls="badge"),
            div(div(c["name"] + (" 👑" if is_leader else ""), cls="name"),
                div(sub, cls="goal done" if done else "goal"), cls="info"),
            button("✕", cls="x", title="Delete", anchor=a, on_click=lambda: delete(cid)),
            cls="top"),
        div(div(div(str(value), cls="value"), cls="ring-in"),
            cls="ring", style=f"--p:{pct}"),
        div(button("−", cls="round", anchor=a, on_click=lambda: change(cid, -1)),
            button("+", cls="round plus", anchor=a, on_click=lambda: change(cid, +1)),
            cls="controls"),
        div(button("+5", cls="chip", anchor=a, on_click=lambda: change(cid, +5)),
            button("+10", cls="chip", anchor=a, on_click=lambda: change(cid, +10)),
            button("↺ Reset", cls="chip", anchor=a, on_click=lambda: change(cid, reset=True)),
            cls="chips"),
        cls="card leader" if is_leader else "card",
        id=a, style=f"--accent:{hex_};--rgb:{rgb}",
    )


def Stat(icon, label, value):
    return div(div(icon, cls="ico"),
               div(div(label, cls="lbl"), div(value, cls="val")), cls="stat")


def Stats(counters):
    total = sum(c["value"] for c in counters)
    top = max(counters, key=lambda c: c["value"]) if counters else None
    leader = top["name"] if top and top["value"] > 0 else "—"
    return div(Stat("🗂️", "Counters", str(len(counters))),
               Stat("🔢", "Total", str(total)),
               Stat("🏆", "Leader", leader), cls="stats")


def AddForm():
    return form(
        select([option(i, value=i) for i in ICONS], name="icon", title="Pick an icon"),
        input_(type="text", name="name", placeholder="New counter name…", autocomplete="off", maxlength="28"),
        input_(type="number", name="goal", placeholder="Goal (optional)", min="0", max="99999"),
        button("＋ Add counter"),
        cls="add", on_submit=add_counter)


def view(state):
    counters = state.get("counters")
    light = state.get("theme") == "light"
    top = max((c["value"] for c in counters), default=0)
    body = (div([CounterCard(c, top) for c in counters], cls="grid") if counters else
            div(div("🫥", cls="big"), p("No counters yet - add your first one above!"), cls="empty"))
    return div(
        div(
            div(div(h1("Counter Board"),
                    p("Built from scratch with pyui, my own Python UI framework", cls="sub"), cls="brand"),
                button("🌙 Dark mode" if light else "☀️ Light mode", cls="theme", on_click=toggle_theme),
                cls="hero"),
            Stats(counters),
            AddForm(),
            body,
            div(button("Reset all counters", cls="resetall", on_click=reset_all), cls="footer") if counters else None,
            cls="wrap"),
        cls="app light" if light else "app")


if __name__ == "__main__":
    App(view, state, title="Counter Board", css=CSS).run(8000)
