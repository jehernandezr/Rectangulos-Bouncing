---
name: ecs-pygame-gamedev
display-name: ECS Pygame Game Dev
description: "Build Python pygame-ce + esper 2.5 ECS games the way the MISW-4407 course teaches: async main loop for pygbag, scenes with deferred switching, services, JSON-driven input commands, an in-game editor built from systems, debug views and level cfg files."
---

# ECS Pygame Game Dev (Python + pygame-ce + esper 2.5)

Use this skill when creating, extending or debugging a Python game built on **pygame-ce + esper** with **ECS (Entity Component System)**: entities are integer IDs, components are plain data classes, systems are functions that iterate component queries.

Sources of truth, in this order: `docs/notas_curso.md` (what the course teaches), `docs/project-course/PLAN_DE_TRABAJO.md` (architecture and spec of the final project) and the code already in the game repository. When this skill and the game repository disagree on a name, keep the repository's name.

## 1. Project layout

```
main.py                         # imports pygame and asyncio, runs GameEngine
requirements.txt                # pygame-ce, pygbag
esper/                          # esper 2.5 vendored inside the repo
assets/
  cfg/   window.json, scenes.json, input.json, level_NN.json, <entity>.json
  fnt/   img/   snd/ (OGG only)
src/
  engine/
    game_engine.py              # loop, window, scene registry, deferred switch
    scenes/scene.py             # Scene base class (template method)
    service_locator.py          # configs, images, fonts, sounds, session, editor
    services/
  ecs/
    components/                 # c_*.py, plain data
    components/tags/            # empty classes
    components/editor/          # CEditorDraggable, CEditorPlacer, CEditorFollowMouse
    systems/                    # s_*.py, one job each
    systems/editor/             # place, delete, duplicate, drag, save
    systems/debug/              # read-only debug renderers
  create/
    prefab_creator.py           # create_* is the only place entities are built
  game/                         # concrete scenes
```

## 2. Main loop

The loop order is a contract: time, events, update, draw, scene switch.

```python
# main.py
import asyncio
import pygame

from src.engine.game_engine import GameEngine

if __name__ == "__main__":
    engine = GameEngine()
    asyncio.run(engine.run())
```

`import pygame` must appear in `main.py`: pygbag only packages pygame-ce when it sees it there.

```python
# src/engine/game_engine.py
import asyncio
import pygame

from src.engine.service_locator import ServiceLocator


class GameEngine:
    def __init__(self) -> None:
        self.window_cfg = ServiceLocator.configs_service.get("assets/cfg/window.json")
        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        size = (self.window_cfg["size"]["w"], self.window_cfg["size"]["h"])
        scale = self.window_cfg["scale"]
        self.window = pygame.display.set_mode((size[0] * scale, size[1] * scale))
        self.screen = pygame.Surface(size).convert(24)
        self.scaled_screen = pygame.Surface(self.window.get_size()).convert(24)
        self.clock = pygame.time.Clock()
        self.delta_time = 0.0
        self.is_running = False
        self._scenes = build_scenes(self)
        self._current_scene = None
        self._scene_name_to_switch = None

    async def run(self) -> None:
        scenes_cfg = ServiceLocator.configs_service.get("assets/cfg/scenes.json")
        self._current_scene = self._scenes[scenes_cfg["start"]]
        self._current_scene.do_create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            self._handle_switch_scene()
            await asyncio.sleep(0)
        self._current_scene.clean()
        pygame.quit()

    def switch_scene(self, new_scene_name: str) -> None:
        self._scene_name_to_switch = new_scene_name

    def _calculate_time(self) -> None:
        self.clock.tick(self.window_cfg["framerate"])
        self.delta_time = min(self.clock.get_time() / 1000.0,
                              1.0 / self.window_cfg["min_framerate"])

    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            else:
                self._current_scene.do_process_events(event)

    def _update(self) -> None:
        self._current_scene.simulate(self.delta_time)

    def _draw(self) -> None:
        self.screen.fill(self.window_cfg["bg_color"])
        self._current_scene.do_draw(self.screen)
        pygame.transform.scale(self.screen, self.window.get_size(), self.scaled_screen)
        self.window.blit(self.scaled_screen, (0, 0))
        pygame.display.flip()

    def _handle_switch_scene(self) -> None:
        if self._scene_name_to_switch is None:
            return
        self._current_scene.clean()
        self._current_scene = self._scenes[self._scene_name_to_switch]
        self._scene_name_to_switch = None
        self._current_scene.do_create()
```

Why each piece:
- **`async def run` + `await asyncio.sleep(0)`**: the browser needs a turn every frame or the page freezes (week 4).
- **No `pygame.SCALED`**: it breaks the web build (course errata). Draw on a fixed canvas and scale it by hand.
- **`min(..., 1 / min_framerate)`**: caps delta time so a slow frame cannot make an object jump through a wall (tunnelling, week 5).
- **The engine only manages the window and the scenes.** It loads no game configuration and stores no game data.

`window.json`:

```json
{
    "title": "GAME TITLE",
    "size": {"w": 256, "h": 208},
    "scale": 3,
    "framerate": 60,
    "min_framerate": 30,
    "bg_color": [0, 0, 0]
}
```

## 3. Services

Everything that is global to the game is a service of the `ServiceLocator`. Nothing reads files or caches assets on its own.

```python
class ServiceLocator:
    configs_service = ConfigsService()
    images_service = ImagesService()
    fonts_service = FontsService()
    sounds_service = SoundsService()
    session_service = SessionService()
    editor_service = EditorService()
```

- **`configs_service.get(path)`**: loads a JSON once and caches it. Scenes, prefabs and systems ask it for their cfg.
- **`images_service.get(path)`**: `pygame.image.load(path).convert_alpha()` cached by path.
- **`fonts_service.get(path, size)`**: cache key is `(path, size)` for both the lookup and the store. The week 5 demo checks `path` and stores `(path, size)`, so it never hits the cache.
- **`sounds_service.play(path)`**: `pygame.mixer.Sound` cached by path. Audio files are OGG so they play on the web.
- **`session_service`**: score, high score, lives, round, continues. It survives scene changes and saves the record: a JSON file on desktop, `platform.window.localStorage` when `sys.platform == "emscripten"`. The professor asked for exactly this service; never carry game state in the engine.
- **`editor_service`**: what the editor has selected (placeable types and current index) while the editor is active.

## 4. Scenes

One `esper.World` per scene. The base class runs the template; each scene fills its hooks.

```python
import esper
import pygame

from src.ecs.components.c_input_command import CInputCommand
from src.ecs.systems.s_input_command import system_input_event


class Scene:
    def __init__(self, game_engine) -> None:
        self.ecs_world = esper.World()
        self._game_engine = game_engine

    def do_process_events(self, event: pygame.event.Event) -> None:
        system_input_event(self.ecs_world, event, self.do_action)

    def simulate(self, delta_time: float) -> None:
        self.do_update(delta_time)
        self.ecs_world._clear_dead_entities()

    def clean(self) -> None:
        self.ecs_world.clear_database()
        self.do_clean()

    def switch_scene(self, new_scene_name: str) -> None:
        self._game_engine.switch_scene(new_scene_name)

    def do_create(self) -> None:
        return None

    def do_update(self, delta_time: float) -> None:
        raise NotImplementedError

    def do_draw(self, screen: pygame.Surface) -> None:
        return None

    def do_action(self, action: CInputCommand) -> None:
        return None

    def do_clean(self) -> None:
        return None
```

Rules:
- **Scene registry from data.** Build the dict from `scenes.json`: named scenes plus one play scene per level path, e.g. `PlayScene("assets/cfg/levels/level_01.json", engine)`. The same play scene class plays every level, the boss level and editor levels.
- **Transitions are requests.** `switch_scene(name)` only stores the name; the engine applies it after `_draw`. Input-driven and system-driven transitions are both safe.
- **A system that triggers a transition receives the scene** (`system_block_count(world, scene)`) and calls `scene.switch_scene(...)`.
- **`do_create` re-reads its level** through the config service on every entry, so editor saves are picked up.
- **The scene only builds its world and calls its systems.** If `do_update` or `do_draw` fills up with math, ifs and assignments, that logic needs a component and a system.
- **Pause is a flag in the play scene**, as in the course demo: while paused, `do_update` skips the gameplay systems and discards one-shot presses; drawing continues. Hiding entities during pause is a system that toggles visibility.

## 5. Input: commands are data

Keys live in `input.json`; prefabs turn them into entities with `CInputCommand`; the scene reacts in `do_action`. No scene or system asks pygame for a key directly.

```python
from enum import Enum
import pygame


class CommandPhase(Enum):
    NA = 0
    START = 1
    END = 2


class CInputCommand:
    def __init__(self, name: str, key: int) -> None:
        self.name = name
        self.key = key
        self.phase = CommandPhase.NA
        self.mouse_pos = pygame.Vector2(0, 0)
```

```json
{
    "pause": {"name": "PAUSE", "keys": ["escape", "p"]},
    "editor": {"name": "TOGGLE_EDITOR", "keys": ["tab"]},
    "debug_view": {"name": "TOGGLE_DEBUG_VIEW", "keys": ["left ctrl"]}
}
```

```python
def create_input_action(world: esper.World, action_cfg: dict) -> None:
    for key_name in action_cfg["keys"]:
        world.add_component(world.create_entity(),
                            CInputCommand(action_cfg["name"],
                                          pygame.key.key_code(key_name)))
```

`system_input_event` matches `KEYDOWN`/`KEYUP` to `START`/`END`, mouse buttons to `START`/`END` with `mouse_pos`, and `MOUSEMOTION` to `NA` with `mouse_pos`, then calls `do_action`. Use `START` for one-shot actions (toggle, place, delete, switch) and `START`/`END` pairs for held actions (move, drag). If the game repository already has a richer `CInputCommand` (scancodes, one-shot flag, command objects), extend that one instead of writing a second input path.

## 6. Components, tags and prefabs

- **A component only holds data.** Construction helpers are fine (`CSurface.from_surface`, `CSurface.from_text`, `CSurface.get_area_relative`).
- **A tag is an empty class** in `components/tags/` (`CTagEnemy`, `CTagRock`). The kind of an entity comes from its tags, never from a string checked with `if`.
- **Data that must be saved goes in a component, not in a tag.** For the editor, the placeable type is `CEditorType(type_name)`; systems still filter by tag.
- **Pick one position convention and keep it.** The course stores the top-left corner in `CTransform.pos`. If the game stores the center (because sprites rotate), `system_rendering`, the debug views and the editor all subtract half the size the same way.
- **Prefabs are the only place entities are built.** They read the entity cfg (`<entity>.json`) and the level cfg (positions and per-level values) and attach components and tags. Systems that need new entities call prefabs.
- **No numbers in code.** Every value lives in a JSON read through `configs_service`.

## 7. Systems

- **One job over every entity with a component signature.** `system_movement` moves everything with `CTransform` and `CVelocity`, whatever it is.
- **State machines**: the state lives in a component (`CEnemyState`), the logic in a system (`system_enemy_state`).
- **Systems talk through components or one-frame event entities**, never by calling each other. One system creates `CEventBaseDestroyed`; another reads it and deletes it in the same frame.
- **Deferred deletion**: `world.delete_entity` inside systems; `simulate` clears the dead entities.
- **No copy-paste systems.** When several systems differ in two lines, extract the shared part (for collisions: one function that builds the rects from `CTransform` + `CHitbox` and yields overlapping pairs) and keep each system to its own outcome.
- **Steering for moving enemies** (week 7): compute the desired velocity toward the target and move the current velocity toward it gradually (`vel.lerp(desired, delta_time * k)` or a capped turn rate). Seek, flee and separation add up.
- **Measure before optimizing** (week 7): `python -m cProfile -o perfil.prof main.py`, then `snakeviz perfil.prof`. Build spatial grids only if the profile shows collisions are the bottleneck.

## 8. In-game editor

The editor is a mode of the play scene. Its state is a flag in the scene plus `editor_service`; its work is done by **systems**. The scene's `do_action` only turns editor commands into one-frame request entities. This keeps the week 6 recipe while respecting the course's code smells ("Scene only manages worlds and systems").

### 8.1 Components

```python
class CEditorDraggable:
    def __init__(self) -> None:
        self.is_dragging = False


class CEditorFollowMouse:
    pass


class CEditorPlacer:
    pass


class CEditorType:
    def __init__(self, type_name: str) -> None:
        self.type_name = type_name


class CEditorRequest:
    def __init__(self, action: str, mouse_pos: pygame.Vector2) -> None:
        self.action = action
        self.mouse_pos = pygame.Vector2(mouse_pos)
```

Every editable prefab adds `CEditorDraggable()` and `CEditorType(type_name)`. The placer is an entity with `CTransform`, `CSurface`, `CEditorFollowMouse` and `CEditorPlacer`; it is the cursor and the hit-test rect.

### 8.2 Commands and wiring

Editor keys and buttons come from `input.json` like any other command:

| Command | Default input | Phase | Effect |
|---|---|---|---|
| `TOGGLE_EDITOR` | Tab | START | enter or leave editor mode; gameplay systems stop |
| `TOGGLE_DEBUG_VIEW` | Left Ctrl | START | cycle NONE, RECTS, VELOCITY |
| `MOUSE_MOVE` | mouse motion | NA | update the cursor position |
| `PLACE_ENTITY` | left click | START | create the selected type at the cursor |
| `DRAG_ENTITY` | left button held | START/END | grab and release the entity under the cursor when nothing is selected |
| `DELETE_ENTITY` | middle click | START | delete the entity under the cursor |
| `CHANGE_ENTITY` | right click | START | cycle the selected type |
| `SAVE_LEVEL` | Enter | START | serialize the level |

```python
EDITOR_ACTIONS = ("PLACE_ENTITY", "DRAG_ENTITY", "DELETE_ENTITY",
                  "CHANGE_ENTITY", "SAVE_LEVEL")


def do_action(self, action: CInputCommand) -> None:
    if action.name == "TOGGLE_EDITOR" and action.phase == CommandPhase.START:
        self._editor_mode = not self._editor_mode
    if not self._editor_mode:
        return
    if action.name == "MOUSE_MOVE":
        self._mouse_pos = self._to_world(action.mouse_pos)
    elif action.name in EDITOR_ACTIONS:
        create_editor_request(self.ecs_world, action, self._mouse_pos)


def do_update(self, delta_time: float) -> None:
    if self._editor_mode:
        system_editor_follow_mouse(self.ecs_world, self._mouse_pos)
        system_editor_draggable(self.ecs_world, self._mouse_pos)
        system_editor_change(self.ecs_world)
        system_editor_place(self.ecs_world)
        system_editor_delete(self.ecs_world)
        system_editor_save(self.ecs_world, self.level_path)
        return
    ...
```

`_to_world` converts window coordinates to world coordinates: divide by the window scale, subtract the game area origin and add the camera offset (wrapping if the world wraps). Without it the cursor and the entities do not line up.

### 8.3 Editor systems

- **`system_editor_follow_mouse`**: sets `CTransform.pos` of entities with `CEditorFollowMouse` to the cursor.
- **`system_editor_draggable`**: moves every `CEditorDraggable` with `is_dragging` to the cursor; on `DRAG_ENTITY` requests it sets or clears `is_dragging` for the entity under the placer rect.
- **`system_editor_change`**: on `CHANGE_ENTITY` advances the index in `editor_service` and swaps the placer preview surface.
- **`system_editor_place`**: on `PLACE_ENTITY` calls the prefab of the selected type at the cursor. Entities are always rebuilt through prefabs, never deep-copied.
- **`system_editor_delete`**: on `DELETE_ENTITY` deletes the draggable entity under the placer rect.
- **`system_editor_save`**: on `SAVE_LEVEL` queries `CTransform` + `CEditorType` (and the start markers), builds a dict with the level schema and writes it: a JSON file on desktop, `localStorage` on the web. Then it deletes the request.

Every editor system deletes the requests it consumed. Entering the editor pauses the simulation and resets moving entities to their cfg start positions, so what you see is what you save.

## 9. Debug views

```python
class DebugView(Enum):
    NONE = 0
    RECTS = 1
    VELOCITY = 2
```

- Debug systems live in `systems/debug/` and are **read-only**.
- `system_rendering_debug_rects` draws each collision rect (from `CHitbox` when the game has one, otherwise from `CSurface.area`) with its position and size; it **replaces** normal rendering.
- `system_rendering_debug_velocity` draws a line or the value of each `CVelocity`; it **overlays** normal rendering.
- They use the same world-to-screen conversion as `system_rendering` (camera, wrap, center or top-left convention).
- The cycle is a command (`TOGGLE_DEBUG_VIEW` in `input.json`) handled in `do_action`; `do_draw` picks the renderers.

## 10. Level cfg files

Every level and every editor save share one schema, the one `do_create` consumes:

```json
{
    "player": {"start": {"x": 520, "y": 776}},
    "bases": [{"type": "H", "pos": {"x": 512, "y": 604}}],
    "obstacles": [{"type": "rock_a", "pos": {"x": 100, "y": 200}}]
}
```

Round trip: edit, save, and the play scene loads the saved level by path (register it in `scenes.json` or let the editor's play scene point at it). Nothing runtime-specific is serialized.

## 11. Web build

- `pygbag main.py` builds the web version; check it every week, not at the end.
- Keep esper 2.5 inside the repo (`esper/`). Without it pygbag installs esper 3.x, which has no `esper.World`.
- `import pygame` in `main.py`, async loop, no `pygame.SCALED`, OGG audio.
- Files cannot be written on the web: records and editor saves go to `localStorage`.

## 12. Code smells checklist (week 6)

Review every change against this list before opening a pull request:

1. If something can be a component plus a system, it is not left in the engine or in a scene.
2. Anything outside ECS or the course patterns (events, Service Locator, scenes, Command, State) does not count for the grade.
3. Many questions, assignments, ifs and calculations in `update()` or `draw()` mean a missing system.
4. The engine manages scenes; a scene manages its world, creates entities and runs systems, nothing else.
5. Copy-pasted systems that change little become one system where components make the difference.
6. If fixing a game-specific bug means looking outside components and systems, logic is scattered outside ECS.
7. Turning a system off should only take commenting its call or changing a component property.
8. One component for one system is fine; keep that component (or entity) reachable from the scene or a service.
9. Configs and values that outlive a scene are services.
10. No ad-hoc event calls inside `update` or `draw`; use event components.

## 13. Rules (non-negotiable)

1. Loop order: time, events, update, draw, scene switch; async with `await asyncio.sleep(0)`; delta time capped.
2. The engine owns the window, the canvas scaling and the scene registry, nothing else.
3. One `esper.World` per scene; `clean()` wipes it; `do_create()` rebuilds it from cfg.
4. Scene switches are requests applied after draw.
5. Global data and assets go through the `ServiceLocator`; game state lives in `session_service`.
6. Input is data: keys in `input.json`, `CInputCommand` entities, `do_action` in the scene.
7. Components hold data, tags are empty, kinds come from tags, saved data lives in components.
8. Entities are built only by prefabs; values come only from JSON.
9. Systems do one job, talk through components or event entities and delete deferred.
10. The editor is a scene mode whose work is done by editor systems; the scene only creates requests.
11. Debug views are read-only systems; RECTS replaces drawing, the other views overlay.
12. Saves use the level schema and go to a file on desktop or `localStorage` on the web.
