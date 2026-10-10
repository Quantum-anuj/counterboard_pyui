"""
pyui - a tiny UI framework in pure Python (zero dependencies, zero JavaScript).

How it works (the whole idea in 4 lines):
  1. You describe the UI as a TREE of Elements:   div(h1("Hi"), button("+", on_click=fn))
  2. The Renderer walks the tree and turns it into an HTML string.
  3. Buttons/forms become real HTML <form>s. Clicking one POSTs to the Python server.
  4. Server runs your handler -> handler changes State -> page is re-rendered.
     (click -> state change -> re-render, exactly like the task asks)
"""
import html
import inspect
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs


# ---------- 1. COMPONENTS: a tree of elements with props ----------
class Element:
    def __init__(self, tag, props, children):
        self.tag = tag
        self.props = props
        self.children = children


def h(tag, *children, **props):
    """Create an element. Lists of children are flattened. cls= means class=."""
    flat = []
    for c in children:
        if isinstance(c, (list, tuple)):
            flat.extend(c)
        else:
            flat.append(c)
    if "cls" in props:
        props["class"] = props.pop("cls")
    return Element(tag, props, flat)


# Friendly helpers: div(...), h1(...), button(...) etc.
def div(*c, **p):    return h("div", *c, **p)
def span(*c, **p):   return h("span", *c, **p)
def h1(*c, **p):     return h("h1", *c, **p)
def h2(*c, **p):     return h("h2", *c, **p)
def p(*c, **p_):     return h("p", *c, **p_)
def button(*c, **p): return h("button", *c, **p)
def form(*c, **p):   return h("form", *c, **p)
def input_(**p):     return h("input", **p)
def select(*c, **p): return h("select", *c, **p)
def option(*c, **p): return h("option", *c, **p)


# ---------- 3. STATE: when data changes, UI updates ----------
class State:
    def __init__(self, **initial):
        self._data = dict(initial)
        self.version = 0          # goes up on every change

    def get(self, key):
        return self._data[key]

    def set(self, key, value):
        self._data[key] = value
        self.version += 1


# ---------- 2. RENDERER: Element tree -> HTML string ----------
VOID_TAGS = {"input", "br", "hr", "img"}


class Renderer:
    def __init__(self):
        self.handlers = {}        # id -> python function (for events)

    def _register(self, fn):
        hid = f"h{len(self.handlers)}"
        self.handlers[hid] = fn
        return hid

    def _attrs(self, props):
        out = ""
        for k, v in props.items():
            if v is True:
                out += f" {k}"
            elif v not in (False, None):
                out += f' {k}="{html.escape(str(v), quote=True)}"'
        return out

    def render(self, node):
        if node is None or node is False:
            return ""
        if not isinstance(node, Element):          # plain text -> escaped (XSS safe)
            return html.escape(str(node))

        props = dict(node.props)
        on_click = props.pop("on_click", None)
        on_submit = props.pop("on_submit", None)
        anchor = props.pop("anchor", None)      # id to scroll back to after the event
        anchor_field = (f'<input type="hidden" name="__anchor" value="{html.escape(anchor)}">'
                        if anchor else "")
        inner = "".join(self.render(c) for c in node.children)

        # 4. EVENTS: button with on_click -> tiny form that POSTs its handler id
        if node.tag == "button" and on_click:
            hid = self._register(on_click)
            btn = f'<button name="__event" value="{hid}"{self._attrs(props)}>{inner}</button>'
            return f'<form method="post" action="/event" class="inline">{anchor_field}{btn}</form>'

        # form with on_submit -> handler receives the typed fields as a dict
        if node.tag == "form" and on_submit:
            hid = self._register(on_submit)
            hidden = f'<input type="hidden" name="__event" value="{hid}">'
            return f'<form method="post" action="/event"{self._attrs(props)}>{hidden}{inner}</form>'

        if node.tag in VOID_TAGS:
            return f"<{node.tag}{self._attrs(props)}>"
        return f"<{node.tag}{self._attrs(props)}>{inner}</{node.tag}>"


# ---------- APP: ties state + view + server together ----------
class App:
    def __init__(self, view, state, title="pyui app", css="", static_dir="static"):
        self.view, self.state, self.title, self.css = view, state, title, css
        self.static_dir = os.path.realpath(static_dir)   # files here are served at /static/...
        self.handlers = {}

    def render_page(self):
        r = Renderer()
        body = r.render(self.view(self.state))      # view(state) -> Element tree
        self.handlers = r.handlers
        return (f"<!doctype html><html><head><meta charset='utf-8'>"
                f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
                f"<title>{html.escape(self.title)}</title><style>{self.css}</style></head>"
                f"<body>{body}</body></html>")

    def handle_event(self, fields):
        hid = fields.pop("__event", None)
        anchor = fields.pop("__anchor", "")
        fn = self.handlers.get(hid)
        if fn is None:
            return anchor                            # stale page, ignore
        if inspect.signature(fn).parameters:         # on_submit handlers take the form data
            fn(fields)
        else:                                        # on_click handlers take nothing
            fn()
        return anchor

    def run(self, port=8000):
        app = self

        class Handler(BaseHTTPRequestHandler):
            def _send(self, code, body, ctype="text/html; charset=utf-8", cache=False):
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                if cache:
                    self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                path = self.path.split("?")[0]
                if path.startswith("/static/"):                       # static files (images etc.)
                    full = os.path.realpath(os.path.join(app.static_dir, path[len("/static/"):]))
                    inside = full.startswith(app.static_dir + os.sep)  # block ../ path tricks
                    if inside and os.path.isfile(full):
                        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
                        with open(full, "rb") as f:
                            return self._send(200, f.read(), ctype, cache=True)
                    return self._send(404, b"Not found", "text/plain")
                if path != "/":
                    return self._send(404, b"Not found", "text/plain")
                self._send(200, app.render_page().encode())

            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0))
                raw = parse_qs(self.rfile.read(n).decode(), keep_blank_values=True)
                anchor = app.handle_event({k: v[0] for k, v in raw.items()})
                self.send_response(303)              # redirect -> GET -> fresh render
                self.send_header("Location", "/#" + anchor if anchor else "/")
                self.end_headers()

            def log_message(self, *a):
                pass

        print(f"Running at http://localhost:{port}  (Ctrl+C to stop)")
        HTTPServer(("", port), Handler).serve_forever()
