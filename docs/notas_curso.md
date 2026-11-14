# Notas del curso MISW-4407 — Introducción al desarrollo de videojuegos

Guía de estudio del proyecto `Rectangulos-Bouncing`. Para cada semana, en este orden:

- **En palabras simples:** la idea explicada como a una persona.
- **Ejemplo en tu juego:** un caso concreto de tu proyecto.
- **Cómo se ve en el código:** fragmentos reales con los nombres de variables que usamos.
- **Notas técnicas:** el detalle fino que guardé de cada práctica y ejercicio.

Al final están el hilo que une todo, la tabla de nombres y un resumen del proyecto final.

---

## Mapa del curso

Curso Coursera/Uniandes "Introducción al desarrollo de videojuegos" (MISW-4407, cohorte 2026-15). Sitio de recursos: https://misw-4407-desarrollo-de-videojuegos.github.io/web-cohorte-2026-15/ (plantillas `PROYECTO_VACIO.zip`, demos por semana en `pry/0N/`, `PR_ECS_0N_RECURSOS.zip` para la práctica y `EJ_ECS_0N_VERIFICACION.zip` con configs de verificación del ejercicio, y "RESULTADO WEB" en pygbag).

**Módulos (Coursera):** 1) Introducción al desarrollo de videojuegos con ECS. 2) Proceso de desarrollo · Input y acciones · Bases de matemáticas 2D. 3) Game feel · Sprites y animaciones 2D · Bases de IA (FSM con patrón State). 4) Elementos formales y dramáticos · Manejo de recursos (Service Locator) · Distribución. 5) El arte del diseño de videojuegos · Manejo de escenas · Gameloop avanzado. 6) Herramientas · ECS avanzado: data locality y coherencia de caché. 7) Juego emergente · Perfilado · IA: steering behaviours. 8) Conclusiones y entregas finales del proyecto (sin clases; ver «Semana 8»).

**Formato semanal:** videos teóricos + "Video Serie" de práctica (el profesor construye sobre su proyecto `ECS_0N_Proy`; la Práctica 1 de cada semana es un repaso que no se descarga) + "Ejercicio semanal individual" calificado con rúbrica, que se entrega como ZIP y se prueba con **otros** archivos de configuración (la flexibilidad por JSON pesa en la nota). Cada semana parte del ejercicio entregado la semana anterior.

**Esqueleto del motor que se mantiene todo el curso** (`src/engine/game_engine.py`): `run()` → `_create()` y luego el game loop `_calculate_time()` (clock.tick + `delta_time` en segundos) → `_process_events()` → `_update()` (sistemas de lógica, al final `_clear_dead_entities()`) → `_draw()` (fill + `system_rendering` + flip) → `_clean()`. Configuración en `assets/cfg/*.json` cargada en `_load_config_files()`.

**Cómo se conecta todo (hilo del curso):**
- Semana 1 («Semana 1»): game loop + delta time → se refactoriza a ECS (componentes de datos + sistemas) → spawner de enemigos dirigido por JSON.
- Semana 2 («Semana 2»): sobre esos cuadrados aparece el jugador; las **etiquetas** permiten que sistemas que piden los mismos componentes actúen solo sobre unos (rebote solo enemigos); el **patrón Command** separa teclas de acciones; la matemática 2D da colisiones AABB (`colliderect`) y el borrado diferido de entidades; ejercicio: balas.
- Semana 3 («Semana 3»): los cuadrados de color pasan a **sprites**; `CSurface.area` cambia dibujo y colisiones; `CAnimation` + `system_animation` animan cualquier entidad; el **patrón State** (FSM) controla al jugador y al Hunter; ejercicio: Hunter + explosiones como entidades efímeras.
- Semana 4 («Semana 4»): patrón Service Locator para imágenes y sonidos con caché; sonidos en eventos del juego; distribución de escritorio (PyInstaller) y web (pygbag, loop async). Última serie de prácticas; luego viene el proyecto en grupo (reproducir un juego clásico).
- Semana 5 («Semana 5»): desde aquí ya no hay "Video Serie" ni ejercicio individual: clases teóricas + video demostración con un proyecto nuevo (Arkanoid, `pry/05/ECS_05_DEMO.zip`) + avance del proyecto en grupo. **Escenas**: el mundo ECS pasa del motor a cada `Scene`, y el motor cambia de escena al final del frame. Gameloop con tiempo fijo, solo como referencia.
- Semana 6 («Semana 6»): sobre ese mismo demo se agregan **herramientas**: modo editor (arrastrar bloques y guardar el nivel en JSON), vistas de depurado (rects y velocidades) y la razón de fondo de ECS: la **localidad de datos** y la caché. Incluye la lista de "code smells" que se revisará en el proyecto final.
- Semana 7 («Semana 7»): **juego emergente**, **perfilado** (cProfile + SnakeViz, memory-profiler) y **steering behaviours** (seek y flee sumados y suavizados con `lerp`), útiles para el Hunter y los enemigos de Bosconian.
- Patrón que se repite: cada comportamiento nuevo = componente(s) nuevo(s) + sistema nuevo registrado en `_update` + prefab que los combina + datos en JSON. Ver «Qué es ECS».

---

## Qué es ECS

### En palabras simples

Un videojuego es un ciclo que se repite unas 60 veces por segundo, como las páginas de un libro animado. En cada vuelta pasan cuatro cosas: se mide cuánto tiempo pasó, se revisa qué tocó el jugador, se actualiza el mundo y se dibuja.

ECS es una forma de organizar ese mundo:
- **Entidad:** un número, como una cédula. No sabe hacer nada por sí sola.
- **Componente:** una ficha de datos que le pegas a esa cédula, como "posición", "velocidad" o "imagen".
- **Sistema:** un trabajador con una sola tarea, que recorre todas las cédulas que tengan las fichas que le interesan.

### Notas técnicas

Base conceptual del curso MISW-4407 (Uniandes, maestría): todo el proyecto `Rectangulos-Bouncing` se construye con ECS sobre **pygame-ce + esper 2.5**. Ver el mapa del curso en «Mapa del curso».

**Por qué ECS (lo que enseña la semana 1 con sus demos):** el curso contrasta tres formas de organizar un juego. 1) *Patrón Entity con herencia tradicional*: clases `Enemigo(Entidad)` con su propio `update()`; crece en jerarquías rígidas. 2) *Patrón Update ("ECS impuro")*: cada objeto se actualiza a sí mismo en el loop. 3) *ECS*: se separan datos y comportamiento; el comportamiento sale de **qué componentes tiene** la entidad, no de su clase.

**Las tres piezas:**
- **Entidad** = solo un identificador (`int` que devuelve `world.create_entity()`). No tiene lógica ni datos propios.
- **Componente** = solo datos, una clase pequeña con prefijo `C` en `src/ecs/components/c_*.py`. Ej.: `CTransform(pos)`, `CVelocity(vel)`, `CSurface(surf, area)`, `CAnimation`, `CPlayerState`. Un componente "etiqueta" (tag) es una clase vacía que solo marca (`CTagEnemy`, `CTagPlayer`, `CTagBullet`, `CTagHunter`, `CTagExplosion` en `components/tags/`). En esper solo hay **un componente de cada tipo por entidad** (por eso cada comando de input es una entidad aparte).
- **Sistema** = función `system_x(world, ...)` en `src/ecs/systems/s_*.py` que pide un conjunto de componentes y actúa sobre **todas** las entidades que los tienen. Ej.: `system_movement` pide `(CTransform, CVelocity)` y mueve a cualquiera; `system_animation` pide `(CSurface, CAnimation)` y anima jugador, Hunter, explosión o asteroide sin saber qué son.

**Prefabs** (`src/create/prefab_creator.py`): funciones que arman una entidad combinando componentes (en este repo con nombres en español: `crear_sprite`, `crear_cuadrado_jugador`, `crear_bala`...). Cambiar qué es algo = cambiar qué componentes se le ponen.

**API de esper 2.5 que se usa:** `esper.World()`, `create_entity()`, `add_component(ent, Comp())` (¡con paréntesis! error clásico de S2.3), `get_component(C)` → `[(ent, c)]`, `get_components(A, B)` → `[(ent, (a, b))]`, `component_for_entity(ent, C)`, `try_component`, `has_component`, `delete_entity(ent)` (diferido), `_clear_dead_entities()` al final de `_update`, `clear_database()` en `_clean`. esper 2.5 **no** permite consultar "entidades SIN un componente"; se filtra con tags.

**Reglas de buen uso (lo que se revisó el 2026-10-25):** componentes sin lógica (factories como `CSurface.from_surface` o helpers como `get_area_relative` son aceptables), sistemas sin estado propio que se comunican vía componentes (ej.: `system_animation` marca `CAnimation.completed` y `system_explosion_kill` decide borrar), estado de una máquina de estados guardado en un componente y su lógica en un sistema, borrar siempre de forma diferida. Desviaciones aceptadas por el curso: el motor guarda referencias a componentes del jugador y `_do_action` le cambia la velocidad fuera de un sistema; sistemas que llaman prefabs (spawner, colisiones que crean explosiones). Mejoras "más puras" identificadas: filtrar el rebote con una etiqueta positiva en vez de `has_component(CTagHunter)` para excluir, `@staticmethod` en `get_area_relative`, unificar `_set_animation` duplicada en `s_player_state`/`s_hunter_state`.

---

## Semana 1: el corazón del juego y la idea de ECS

### En palabras simples

Se arma el ciclo del juego y se aprende a medir el tiempo entre una vuelta y otra (*delta time*), para que todo se mueva igual de rápido sin importar qué tan rápido sea el computador. Después se reorganiza el código en entidades, componentes y sistemas.

### Ejemplo en tu juego

El sistema de movimiento solo dice: "a todo lo que tenga posición y velocidad, muévelo un poquito". No sabe si es un asteroide, una bala o el jugador, y no le importa. Por eso un mismo pedacito de código mueve todo el juego.

Si el computador va lento y da menos vueltas por segundo, cada movimiento se multiplica por el tiempo que pasó, y así el asteroide recorre la misma distancia en un computador rápido que en uno lento.

### Cómo se ve en el código

**El reloj: cuánto tiempo pasó entre cuadro y cuadro** (`src/engine/game_engine.py`)

```python
def _calculate_time(self):
    self.clock.tick(self.framerate)
    self.delta_time = self.clock.get_time() / 1000.0
```

- **`self.framerate`:** sale de `window.json` (60) y le pide al reloj que no dé más de 60 vueltas por segundo.
- **`self.clock.get_time()`:** dice cuántos **milisegundos** duró la última vuelta, unos 16 ms a 60 cuadros por segundo.
- **`self.delta_time`:** es ese mismo tiempo en **segundos**, unos 0,016. Lo dividimos entre 1000 porque toda la física del juego piensa en segundos.

**Las fichas: dónde está y hacia dónde va**

```python
class CTransform:
    def __init__(self, pos:pygame.Vector2) -> None:
        self.pos = pos

class CVelocity:
    def __init__(self, vel:pygame.Vector2) -> None:
        self.vel = vel
```

Las dos usan `pygame.Vector2`, que es simplemente una pareja de números (x, y).

- **`pos`:** dónde está la esquina superior izquierda de la entidad, en píxeles. En pygame, x crece hacia la derecha y **y crece hacia abajo**, al revés que en matemáticas.
- **`vel`:** cuántos **píxeles por segundo** avanza en cada eje. Por ejemplo, `vel = (100, -50)` significa 100 px/s a la derecha y 50 px/s **hacia arriba** (el negativo es hacia arriba).

**El trabajador que mueve todo** (`src/ecs/systems/s_movement.py`)

```python
def system_movement(world:esper.World, delta_time:float):
    components = world.get_components(CTransform, CVelocity)
    for entity, (c_t, c_v) in components:
        c_t.pos.x += c_v.vel.x * delta_time
        c_t.pos.y += c_v.vel.y * delta_time
```

Si algo va a 100 px/s y pasaron 0,016 s, avanza 1,6 px en esta vuelta. Si el computador va lento y pasaron 0,033 s, avanza 3,3 px. Al final del segundo recorrió 100 px en los dos casos.

Los nombres cortos se repiten en todo el proyecto: `c_t` es "componente transform" y `c_v` es "componente velocity".

**Cómo nace la velocidad de un asteroide** (`src/create/prefab_creator.py`)

```python
vel_mag = random.uniform(enemy_info["velocity_min"],
                         enemy_info["velocity_max"])
vel = pygame.Vector2(vel_mag, 0).rotate(random.uniform(0, 360))
```

Se hace en dos pasos:
1. **`vel_mag` (magnitud):** qué tan rápido va. Es un número al azar entre el mínimo y el máximo de `enemies.json`; para `AsteroidA`, entre 25 y 50 px/s.
2. **Dirección:** se crea una flecha que apunta a la derecha con esa rapidez, `(vel_mag, 0)`, y se **gira** un ángulo al azar entre 0 y 360°. Así cada asteroide sale en cualquier dirección, pero siempre con la rapidez correcta.

**El rebote** (`src/ecs/systems/s_screen_bounce.py`)

```python
cuad_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
if cuad_rect.left < 0 or cuad_rect.right > screen_rect.width:
    c_v.vel.x *= -1
    cuad_rect.clamp_ip(screen_rect)
    c_t.pos.x = cuad_rect.x
```

- **`cuad_rect`:** el rectángulo del asteroide ubicado en su posición actual. Se llama así porque al principio del curso eran cuadrados.
- **`vel.x *= -1`:** invierte la dirección horizontal. Si iba a +80 px/s ahora va a −80 px/s; la rapidez es la misma y solo cambia el sentido.
- **`clamp_ip`:** lo empuja de vuelta adentro de la pantalla. Sin eso, un asteroide lento podría quedar con medio cuerpo afuera, invertirse cada cuadro y quedarse pegado al borde. Por eso usamos `<` y `>` y no `<=` ni `>=`.

### Notas técnicas

Módulo 1: Introducción al desarrollo de videojuegos con ECS. Commits en el repo: S1.1 a S1.6 + ejercicio (PR #1, release `semana-1`).

**Prácticas, en orden:**
1. **Ventana y game loop (S1.1):** `pygame.init()`, `set_mode((640, 360), pygame.SCALED)`, `Clock`, y el loop `_calculate_time → _process_events → _update → _draw` con `_clean()` al salir (`pygame.QUIT` pone `is_running = False`).
2. **Movimiento con delta time (S1.2):** `clock.tick(framerate)` y `delta_time = clock.get_time() / 1000.0`; la posición avanza `pos += vel * delta_time` para que la velocidad sea en píxeles por segundo, no por cuadro.
3. **Rebote con clamp (S1.3):** si el rect se sale (`left < 0 or right > width`) se invierte `vel.x *= -1` y se corrige con `rect.clamp_ip(screen_rect)` para que no quede pegado afuera. (Se usa `<`/`>`, no `<=`, o los cuadrados lentos se quedan pegados al borde.)
4. **Componentes (S1.4):** el cuadrado se descompone en datos: `CTransform(pos)`, `CVelocity(vel)`, `CSurface(size, color)` (crea `pygame.Surface` y la rellena).
5. **Sistemas (S1.5):** `system_movement(world, dt)`, `system_rendering(world, screen)` (`screen.blit(c_s.surf, c_t.pos)`), `system_screen_bounce(world, screen)`; cada uno con `world.get_components(...)`.
6. **Prefab e integración (S1.6):** `crear_cuadrado(world, size, pos, vel, col)` en `prefab_creator.py` arma la entidad; el motor crea `self.ecs_world = esper.World()`, llama sistemas en `_update`/`_draw` y ya no conoce "cuadrados".

**Ejercicio:** `window.json` (título, tamaño, `bg_color`, framerate), `enemies.json` (tipos con size/color/velocity_min/max), `level_01.json` (`enemy_spawn_events` con tiempo, tipo y posición). Componente `CEnemySpawner` (con `SpawnEventData` y `current_time`) + `system_enemy_spawner(world, enemies_cfg, dt)` que acumula tiempo y crea cada enemigo una vez (`triggered`). Velocidad aleatoria entre min y max en dirección aleatoria.

**Conexión:** aquí nace el esqueleto que dura todo el curso (loop + `_load_config_files` + sistemas + prefabs) y la idea clave: el spawner es una entidad más con su componente, no lógica dentro del motor. Siguiente: «Semana 2». Conceptos: «Qué es ECS».

---

## Semana 2: el jugador, los controles y los choques

### En palabras simples

Primero, a distinguir entidades que tienen las mismas fichas. El jugador y un asteroide tienen posición, velocidad e imagen, así que ¿cómo sabe un sistema cuál es cuál? Con **etiquetas**: fichas vacías que solo dicen "soy enemigo" o "soy jugador".

Segundo, el **patrón Command**. Las teclas no mueven al jugador directamente; producen una *orden con nombre*, como "PLAYER_LEFT". El juego reacciona a la orden y no a la tecla.

Tercero, cómo detectar choques entre rectángulos.

### Ejemplo en tu juego

Al principio el jugador rebotaba en los bordes igual que los asteroides, y uno perdía el control. La solución fue decirle al sistema de rebote "solo a los que tengan la etiqueta de enemigo".

Con el patrón Command, si mañana quieres mover al jugador con WASD en vez de flechas, cambias una línea. Toda la lógica de "qué pasa cuando el jugador va a la izquierda" queda igual.

### Cómo se ve en el código

**Etiquetas: fichas vacías que solo dicen qué es algo**

```python
class CTagEnemy:
    def __init__(self) -> None:
        pass
```

No guardan datos; solo marcan. El rebote las usa para filtrar:

```python
components = world.get_components(CTransform, CVelocity, CSurface, CTagEnemy)
```

Eso quiere decir: dame solo las entidades que tengan posición, velocidad, imagen **y** la etiqueta de enemigo. El jugador no tiene `CTagEnemy`, así que el rebote nunca lo toca.

El error clásico de la práctica S2.3 fue escribir `CTagEnemy` sin paréntesis: eso pasa la clase en vez de una ficha. Lo correcto es `CTagEnemy()`.

**El patrón Command: la tecla no mueve, la orden sí** (`c_input_command.py`)

```python
class CInputCommand:
    def __init__(self, name:str, key:int) -> None:
        self.name = name
        self.key = key
        self.phase = CommandPhase.NA

class CommandPhase(Enum):
    NA = 0
    START = 1
    END = 2
```

- **`name`:** el nombre de la orden, por ejemplo `"PLAYER_LEFT"`.
- **`key`:** el número de la tecla en pygame, por ejemplo `pygame.K_LEFT`.
- **`phase`:** si la tecla se acaba de presionar (`START`) o de soltar (`END`).

Cada orden es su propia entidad, porque esper solo permite una ficha de cada tipo por entidad:

```python
ecs_world.add_component(input_left,
                        CInputCommand("PLAYER_LEFT", pygame.K_LEFT))
```

**Cómo la orden se vuelve velocidad** (`_do_action` del motor)

```python
if c_input.name == "PLAYER_LEFT":
    if c_input.phase == CommandPhase.START:
        self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
    elif c_input.phase == CommandPhase.END:
        self._player_c_v.vel.x += self.player_cfg["input_velocity"]
```

- **`self._player_c_v`:** la ficha de velocidad del jugador, guardada en el motor para no buscarla cada vez. El guion bajo inicial indica que es "privada" del motor.
- **`input_velocity`:** sale de `player.json` y vale 100 px/s.
- **Presionar izquierda resta 100 a `vel.x`; soltarla los vuelve a sumar.**

Mira qué pasa al presionar varias teclas:

| Acción | `vel.x` |
|---|---|
| Nada presionado | 0 |
| Presionas ← | −100 (va a la izquierda) |
| Además presionas → | −100 + 100 = 0 (se compensan, queda quieto) |
| Sueltas ← | 0 + 100 = +100 (sigue a la derecha) |

Nunca hay que preguntar "¿qué teclas están presionadas ahora?". Cada evento suma o resta, y la cuenta siempre cuadra. Lo mismo pasa con ↑ y ↓ en `vel.y`, recordando que **arriba resta** porque en pantalla y crece hacia abajo.

**La bala: dirección y rapidez por separado** (`crear_bala`)

```python
player_center = player_pos + (player_size / 2)
direction = mouse_pos - player_center
if direction.length() == 0:
    return
vel = direction.normalize() * bullet_info["velocity"]
pos = player_center - (size / 2)
```

Paso a paso:
1. **`player_center`:** el centro del jugador. `player_pos` es su esquina, así que se le suma la mitad de su tamaño.
2. **`direction`:** la flecha que va del jugador al mouse. Su largo depende de qué tan lejos esté el mouse.
3. **`normalize()`:** convierte esa flecha en una de largo exactamente 1, que conserva la dirección pero pierde la distancia. Esto es clave: sin normalizar, una bala disparada lejos iría más rápido que una disparada cerca.
4. **`* bullet_info["velocity"]`:** le da la rapidez real, 200 px/s según `bullet.json`.
5. **`if direction.length() == 0`:** si el mouse está justo en el centro del jugador no hay dirección, y normalizar daría error.
6. **`pos`:** la bala se ubica de modo que *su* centro quede en el centro del jugador.

**Los choques** (`s_collision_bullet_enemy.py`)

```python
bullet_rect = b_s.area.copy()
bullet_rect.topleft = b_t.pos
...
if bullet_rect.colliderect(ene_rect):
    world.delete_entity(bullet_entity)
    world.delete_entity(enemy_entity)
```

- **`colliderect`:** pygame responde si dos rectángulos se tocan. Es la colisión AABB del video de matemáticas.
- **`b_s`, `b_t`:** "bala surface" y "bala transform". **`e_s`, `e_t`:** lo mismo del enemigo.
- **`delete_entity`:** no borra en ese instante; marca para borrar. El borrado real ocurre al final de `_update`, con `self.ecs_world._clear_dead_entities()`. Así ningún sistema se encuentra una entidad a medio borrar.

### Notas técnicas

Módulo 2: Proceso de desarrollo · Input y acciones · Bases de matemáticas 2D. Transcripciones detalladas en `VideoJuegos/transcripciones/S2.2.md`–`S2.6.md`. Commits S2.2–S2.6 + ejercicio (PR #2, release `semana-2`).

**Teoría que se aplica:** el patrón **Command** (las teclas producen *acciones* con nombre y fase, el juego reacciona a acciones, no a teclas); vectores y colisión de rectángulos alineados a los ejes (AABB). Demo del sitio: "bus de eventos".

**Prácticas:**
- **S2.2 Jugador:** `player.json` (size, color, `input_velocity`) y `level_01.json["player_spawn"]["position"]`; `crear_cuadrado_jugador` lo centra restando la mitad del tamaño y con velocidad 0.
- **S2.3 Etiquetas:** `CTagPlayer`, `CTagEnemy` (clases vacías en `components/tags/`). Los prefabs devuelven la entidad; el motor guarda `_player_entity` y `_player_c_v`. Error del video: `add_component(e, CTagEnemy)` sin `()` (pasa la clase, no instancia) — se corrige en S2.5.
- **S2.4 Command:** `CInputCommand(name, key)` con `phase` (`CommandPhase.NA/START/END`). `system_input_player(world, event, do_action)` corre por cada evento en `_process_events`; si la tecla coincide pone START (KEYDOWN) o END (KEYUP) y llama al callback `self._do_action` (tipado `Callable[[CInputCommand], None]`). Cada comando es una entidad aparte (esper: un componente por tipo por entidad).
- **S2.5 Movimiento:** en `_do_action`, `PLAYER_LEFT` START resta `input_velocity` a `vel.x` y END la suma (teclas opuestas se compensan; en pygame `y` crece hacia abajo). Problema: el jugador rebotaba como enemigo → `system_screen_bounce` pide también `CTagEnemy`. **Lección clave:** las etiquetas existen para que sistemas que piden los mismos componentes actúen solo sobre ciertas entidades.
- **S2.6 Colisión:** `system_collision_player_enemy(world, player_entity, level_cfg)`: `rect = surf.get_rect(topleft=pos)`, `colliderect`; borra el enemigo con `world.delete_entity` y devuelve al jugador al spawn. `delete_entity` es **diferido**: `_clear_dead_entities()` al final de `_update` y `clear_database()` en `_clean`.

**Ejercicio (balas):** `bullet.json` (size, color, velocity), `max_bullets` en `level_01.json["player_spawn"]`; comando `PLAYER_FIRE` con `pygame.BUTTON_LEFT` (el input system también maneja `MOUSEBUTTONDOWN/UP` con `event.button`); `crear_bala` sale del centro del jugador hacia `pygame.mouse.get_pos()` normalizado × velocidad; `CTagBullet`; `system_bullet_boundaries` (borra si `not screen_rect.contains`), `system_player_boundaries` (clamp), `system_collision_bullet_enemy` (borra ambos).

**Conexión:** se apoya en los componentes/sistemas de «Semana 1»; introduce dos ideas que la semana 3 reutiliza: filtrar con etiquetas y separar entrada (Command) de efecto. Siguiente: «Semana 3».

---

## Semana 3: que el juego se vea vivo

### En palabras simples

Los cuadrados de colores pasan a ser **imágenes**. Las animaciones salen de una **hoja de sprites**: una tira con varios dibujos, como un rollo de película, que se muestra un cuadro a la vez.

Luego aparece el **patrón State**: un personaje está siempre en un "modo" (quieto, moviéndose, persiguiendo) y cambia de modo según reglas claras.

### Ejemplo en tu juego

El Hunter tiene tres modos:
1. **Quieto:** espera en su lugar.
2. **Persiguiendo:** si el jugador se acerca a menos de 100 píxeles, pasa a este modo.
3. **Regresando:** si se aleja 200 píxeles de su casa, deja de perseguir y vuelve.

Al llegar a casa vuelve a quedarse quieto, listo para empezar otra vez. Pensarlo así evita ese enredo de `if` que nadie entiende después.

Lo más bonito de esta semana: un solo sistema de animación anima al jugador, al Hunter y a las explosiones. Le basta con que tengan imagen y datos de animación.

### Cómo se ve en el código

**`area`: qué pedazo de la imagen se dibuja** (`c_surface.py`)

```python
@classmethod
def from_surface(cls, surface:pygame.Surface):
    c_surf = cls(pygame.Vector2(0,0), pygame.Color(0,0,0))
    c_surf.surf = surface
    c_surf.area = surface.get_rect()
    return c_surf
```

- **`surf`:** la imagen completa. El jugador es una tira de 128×32 con 4 dibujos.
- **`area`:** el rectángulo que se recorta para dibujar, por ejemplo solo los 32×32 del cuadro actual.
- **`@classmethod`:** Python no permite dos constructores, así que esta es una segunda forma de crear un `CSurface` a partir de una imagen ya cargada.

El dibujo usa ese recorte:

```python
screen.blit(c_s.surf, c_t.pos, area=c_s.area)
```

**La animación: un cronómetro que avanza cuadros** (`c_animation.py`)

```python
self.number_frames = animations["number_frames"]
self.animations_list:List[AnimationData] = []
self.curr_anim = 0
self.curr_anim_time = 0
self.curr_frame = self.animations_list[self.curr_anim].start
```

Y en `AnimationData`:

```python
self.framerate = 1.0 / framerate
```

- **`number_frames`:** cuántos dibujos tiene la tira; 4 para el jugador y 6 para el Hunter.
- **`animations_list`:** las animaciones disponibles, como `MOVE` e `IDLE`.
- **`curr_anim`:** qué animación está sonando, por su posición en la lista.
- **`curr_frame`:** en qué dibujo va.
- **`curr_anim_time`:** cuánto falta para pasar al siguiente dibujo.
- **`1.0 / framerate`:** el JSON dice 10 cuadros por segundo, pero al motor le sirve más saber que cada cuadro dura 0,1 segundos.

En `s_animation.py`:

```python
c_a.curr_anim_time -= delta_time
if c_a.curr_anim_time <= 0:
    c_a.curr_anim_time = c_a.animations_list[c_a.curr_anim].framerate
    c_a.curr_frame += 1
    if c_a.curr_frame > c_a.animations_list[c_a.curr_anim].end:
        c_a.curr_frame = c_a.animations_list[c_a.curr_anim].start
    rect_surf = c_s.surf.get_rect()
    c_s.area.w = rect_surf.w / c_a.number_frames
    c_s.area.x = c_s.area.w * c_a.curr_frame
```

En palabras: le resto el tiempo que pasó al cronómetro. Cuando llega a cero, lo reinicio, avanzo un dibujo (y si me paso del último, vuelvo al primero) y muevo el recorte. Con un ancho de 32 px, el cuadro 2 empieza en x = 64.

**El estado del jugador: quieto o moviéndose** (`s_player_state.py`)

```python
def _do_idle_state(c_v, c_a, c_pst):
    _set_animation(c_a, "IDLE")
    if c_v.vel.magnitude_squared() > 0:
        c_pst.state = PlayerState.MOVE
```

- **`c_pst`:** "componente player state".
- **`magnitude_squared()`:** la rapidez al cuadrado. Para saber si algo se mueve basta con que sea mayor que 0, y así no hay que calcular una raíz cuadrada, que es más lenta. Da igual comparar 5 > 0 que 25 > 0.

**El Hunter: la velocidad se calcula cada cuadro** (`s_hunter_state.py`)

```python
direction = pl_center - hunter_center
if direction.length_squared() > 0:
    c_v.vel = direction.normalize() * c_hst.velocity_chase
...
if c_t.pos.distance_to(c_hst.origin) >= c_hst.distance_start_return:
    c_hst.state = HunterState.RETURN
```

Es la misma idea de la bala (dirección normalizada × rapidez), pero **recalculada en cada vuelta**. Como el jugador se mueve, la flecha cambia, y por eso el Hunter lo sigue en curva.

- **`c_hst`:** "componente hunter state".
- **`origin`:** su casa, guardada al nacer.
- **`velocity_chase`** (75) **y `velocity_return`** (100): sus dos rapideces. Regresa más rápido de lo que persigue.
- **`distance_start_chase`** (100) **y `distance_start_return`** (200): cuándo empieza a perseguir y cuándo se rinde.

Al regresar hay un detalle fino:

```python
if direction.length() <= c_hst.velocity_return * delta_time:
    c_t.pos.xy = c_hst.origin.xy
```

Si en este cuadro avanzaría más de lo que le falta para llegar, lo ponemos exactamente en su casa. Si no, se pasaría y temblaría de un lado a otro sin llegar nunca.

### Notas técnicas

Módulo 3: Game feel · Texturas, sprites y animaciones 2D · Bases de IA y autómatas finitos (FSM) con el patrón State. Videos S3.2–S3.7 en `VideoJuegos/`, recursos en `recursos_semana3/` y `verificacion_semana3/`. Commits S3.2–S3.7 + ejercicio en rama `semana-03` (PR #3). Demos del sitio: "hitbox" y "animación grilla 2D".

**Prácticas:**
- **S3.2 Texturas:** `enemies.json` cambia size/color por `"image": "assets/img/asteroid_01.png"`; `pygame.image.load(...).convert_alpha()`; nueva `crear_sprite(world, pos, vel, surface)`. El video termina incompleto: `CSurface` no acepta una superficie ya hecha.
- **S3.3 `@classmethod` como constructor alterno:** Python no sobrecarga `__init__`, así que `CSurface.from_surface(cls, surface)` crea `cls(Vector2(0,0), Color(0,0,0))` y reemplaza `surf`. La bala también usa imagen (`bullet.json` → `image`, `velocity`).
- **S3.4 Hoja de sprites y `area`:** `player.json` → `"animations": {"number_frames": 4, "list": [{"name": "MOVE", "start": 0, "end": 3}]}`. `CSurface.area = surf.get_rect()` define qué porción se dibuja: `screen.blit(surf, pos, area=area)`. Las colisiones usan `area.copy()` + `rect.topleft = pos` (copiar porque `area` es la referencia del dibujo; el profesor primero escribe `pl_rect.top = pos` → `TypeError: invalid rect assignment` y lo corrige a `topleft`).
- **S3.5 `CAnimation`:** recibe el dict de `animations`; guarda `number_frames`, `animations_list` de `AnimationData(name, start, end, framerate)` donde `framerate = 1.0 / framerate` (de cuadros por segundo a segundos por cuadro), `curr_anim`, `curr_anim_time`. Claves reales: `"animations"`, `"framerate"`, `"MOVE"`, `"IDLE"`.
- **S3.6 `system_animation(world, dt)`:** resta dt a `curr_anim_time`; al llegar a ≤0 la repone con el framerate, avanza `curr_frame`, si pasa de `end` vuelve a `start`, y recalcula `area.w = surf.w / number_frames`, `area.x = area.w * curr_frame`. `CAnimation` arranca con `curr_anim_time = 0` y `curr_frame = start` para que el primer update ya recorte (si no, se ve la hoja completa un instante). El jugador se centra con el ancho de **un cuadro** (`size = (size[0] / number_frames, size[1])`, primero falla con `size[0] = ...` porque es tupla) y la bala usa `player_c_s.area.size`.
- **S3.7 Helper + patrón State:** `CSurface.get_area_relative(area, pos_topleft)` (sin decorador; copia el rect y lo ubica) reemplaza todos los `get_rect(topleft=...)` de bordes y colisiones. `player.json` agrega `IDLE` (start=end=0, framerate 1). `CPlayerState` + enum `PlayerState(IDLE, MOVE)`; `system_player_state` con `_do_idle_state`/`_do_move_state`: cambia de estado según `vel.magnitude_squared() > 0` (evita la raíz cuadrada) y `_set_animation(c_a, n)` solo resetea si la animación cambia. Se registra en `_update` después de `system_movement`.

**Ejercicio (implementado 2026-10-20/25):** enemigo **Hunter** (`enemies.json` con `animations` MOVE/IDLE de 6 cuadros y `velocity_chase`, `velocity_return`, `distance_start_chase`, `distance_start_return`): FSM `CHunterState(IDLE, CHASE, RETURN)` + `system_hunter_state` (persigue si el jugador está a ≤ d; regresa si se aleja ≥ d_o de su origen; al llegar vuelve a IDLE y puede perseguir de nuevo; animado solo en movimiento; no rebota). **Explosiones** (`explosion.json`, 8 cuadros, EXPLODE): entidad aparte con `CTagExplosion` creada en las colisiones al centro del enemigo; `system_animation` marca `CAnimation.completed` al dar la vuelta y `system_explosion_kill` la borra. Para pasar la evaluación con otras configs: animaciones opcionales en cualquier entidad (`crear_animacion`), Hunter detectado por tener `velocity_chase` (no por nombre), animación elegida por nombre (`"MOVE"`/`"IDLE"`), jugador recentrado con `area.w`.

**Conexión:** reutiliza las etiquetas y el patrón de "estado en componente + sistema" de «Semana 2» (Command → State), y demuestra lo central de ECS: un solo `system_animation` sirve para jugador, Hunter, explosiones y asteroides porque solo depende de `(CSurface, CAnimation)`. Conceptos: «Qué es ECS». Mapa: «Mapa del curso».

---

## Semana 4: la bodega de recursos y la publicación

### En palabras simples

El **Service Locator** es como una bodega central. En vez de que cada parte del juego vaya al disco a buscar una imagen o un sonido, todos se lo piden a la bodega. La primera vez la bodega lo carga, y las siguientes lo entrega de una vez, sin volver a buscarlo.

También se aprende a **distribuir** el juego: como programa de escritorio con PyInstaller y como página web con pygbag. Para la web, el ciclo del juego debe "ceder el turno" al navegador en cada vuelta, y por eso se vuelve asíncrono.

### Ejemplo en tu juego

Cada vez que disparas se crea una bala con la misma imagen. Sin la bodega, el juego leería el archivo `bullet.png` del disco en cada disparo; con ella, lo lee una sola vez. Lo mismo pasa con los sonidos, las fuentes y los archivos de configuración.

Y gracias a la distribución, tu juego ahora se puede jugar desde cualquier navegador en itch.io: https://jehernandezr.itch.io/bouncinguniandesrectang

### Cómo se ve en el código

**El Service Locator** (`service_locator.py`)

```python
class ServiceLocator:
    configs_service = ConfigsService()
    fonts_service = FontsService()
    images_service = ImagesService()
    sounds_service = SoundsService()
```

Cada servicio funciona como una bodega con memoria. Por ejemplo, `images_service.py`:

```python
def get(self, path:str) -> pygame.Surface:
    if path not in self._images:
        self._images[path] = pygame.image.load(path).convert_alpha()
    return self._images[path]
```

- **`self._images`:** un diccionario que guarda cada imagen ya cargada, usando su ruta como llave.
- **La primera vez** que alguien pide `"assets/img/bullet.png"` se lee del disco; las siguientes se entrega la misma de memoria.
- **`convert_alpha()`:** prepara la imagen para dibujarse rápido conservando la transparencia.

Así se usa desde cualquier lugar:

```python
bullet_surface = ServiceLocator.images_service.get(bullet_info["image"])
ServiceLocator.sounds_service.play(bullet_info["sound"])
```

**El ciclo asíncrono para la web**

```python
async def run(self) -> None:
    self._create()
    self.is_running = True
    while self.is_running:
        self._calculate_time()
        self._process_events()
        self._update()
        self._draw()
        await asyncio.sleep(0)
    self._clean()
```

`await asyncio.sleep(0)` significa "le cedo un instante al navegador". Sin eso, el navegador se congelaría esperando a que el juego termine, y como el juego nunca termina, la página nunca respondería.

**La pausa en ECS**

```python
def _update(self):
    if self.is_paused:
        self.ecs_world._clear_dead_entities()
        return
```

No hay que congelar entidades una por una. Simplemente no se llama a los trabajadores: sin sistema de movimiento nada se mueve, y sin sistema de colisión nada choca. El dibujo sigue funcionando, por eso se ve el juego quieto con el texto "PAUSA" encima.

**Tu escudo: la receta completa** (`c_shield.py`)

```python
class CShield:
    def __init__(self, shield_info:dict) -> None:
        self.duration = shield_info["duration"]
        self.cooldown = shield_info["cooldown"]
        self.radius = shield_info["radius"]
        self.time_active = 0.0
        self.time_cooldown = 0.0
        self.requested = False
```

- **`duration`** (2 s) **y `cooldown`** (5 s): salen de `shield.json`.
- **`time_active` y `time_cooldown`:** dos cronómetros que bajan con `delta_time`, igual que en la animación.
- **`requested`:** el motor no activa el escudo directamente. Al presionar ESPACIO solo levanta esta bandera, y es el sistema quien decide si se puede activar. Así la lógica queda en el trabajador y no en el motor.

### Notas técnicas

Módulo 4: Elementos formales y dramáticos · Manejo de recursos (patrón "service locator") · Despliegue y distribución en Python. "Video serie - Recursos (service locator) y distribución" = última serie de prácticas del curso. Videos S4.2–S4.5 en `VideoJuegos/` (S4.1 repaso no se baja). Recursos: `recursos_semana4/` (img + `fnt/PressStart2P.ttf` + `snd/*.ogg`), verificación en `verificacion_semana4/` (agrega `shield.png`, `bullet_especial.png`, `laser_special.ogg`). Commits S4.2–S4.5 en rama `semana-04` (2026-10-30). Ejercicio: "Sonidos, personalización y distribución", vence 2026-11-01;

**Prácticas:**
- **S4.2 Esqueleto:** `src/engine/service_locator.py` con `class ServiceLocator:` y atributos de clase `images_service = ImagesService()`, `sounds_service = SoundsService()`; servicios en `src/engine/services/` (`images_service.py` con `get(self, path) -> pygame.Surface`, `sounds_service.py` con `play(self, path)`), al inicio vacíos (`pass`). Idea: un punto global para pedir recursos sin pasar referencias por todo el código.
- **S4.3 Imágenes con caché:** `self._images = {}`; `get` carga con `pygame.image.load(path).convert_alpha()` solo si no está y devuelve la misma superficie (no se recarga del disco por cada bala/explosión). Todos los prefabs cambian `pygame.image.load(...)` por `ServiceLocator.images_service.get(info["image"])`.
- **S4.4 Sonidos:** `self._sounds = {}`, `pygame.mixer.Sound(path)` cacheado y `.play()`. JSON: `"sound"` en `bullet.json` (laser), `explosion.json` (explosion), asteroides en `enemies.json` (asteroid); Hunter `"sound_chase"` (ufo). Se reproduce al crear bala, explosión y asteroide, y en el Hunter al pasar de IDLE a CHASE. En web los sonidos deben ser OGG.
- **S4.5 Distribución:** escritorio `pyinstaller --noconsole --onefile main.py` → `dist/main` (hay que copiar `assets/` junto al ejecutable porque las rutas son relativas). Web `pygbag main.py` (o `--build`) → `build/web/index.html` + `.apk`; requiere loop **async**: `async def run(self)` con `await asyncio.sleep(0)` al final de cada vuelta y `asyncio.run(engine.run())` en `main.py`. Fe de erratas del curso: quitar `pygame.SCALED` (usar `0`) porque rompe la versión web.

**Problemas reales resueltos al construir la web (pygbag 0.9.3, macOS):** 1) SSL `CERTIFICATE_VERIFY_FAILED` al bajar la plantilla → correr con `SSL_CERT_FILE=/etc/ssl/cert.pem`. 2) Sin esper en el proyecto pygbag instala esper 3.9 desde PyPI (sin `esper.World`) → se copió esper 2.5 a `esper/` en la raíz del repo (como el proyecto del profesor). 3) `module 'pygame' has no attribute 'Vector2'` → pygbag solo instala pygame-ce si ve `import pygame` en `main.py`; se agregó. Así se probó jugando en el navegador integrado.

**Conexión:** el Service Locator centraliza lo que antes cada prefab hacía suelto (cargar imágenes de «Semana 3») y es la puerta para sonidos y fuentes; la distribución exige que todo el juego dependa de rutas relativas en `assets/` y de JSON, lo que el curso viene pidiendo desde «Semana 1». Mapa: «Mapa del curso». Conceptos ECS: «Qué es ECS».


**Ejercicio implementado (2026-10-30, PR #4):** `ConfigsService` y `FontsService` en el `ServiceLocator` (todo JSON, imagen, sonido y fuente pasa por él); `CSurface.from_text`, `CTagHud` (se dibuja encima en `system_rendering`) y `CAnchor` + `interface.json` con textos anclados a la pantalla (`midtop`, `center`, `topleft`... + offset); pausa con P (el motor deja de correr los sistemas de `_update` y crea/borra el texto PAUSA); sonidos propios generados `propulsor.ogg` (al pasar a MOVE, `player.json` `sound_move`) e `impacto.ogg` (`sound_hit`); característica única "escudo de energía" con ESPACIO: `CShield` en el jugador (`requested`, tiempos), entidad visual `shield.png` animada, `system_shield` (2 s, destruye enemigos en radio, parpadea al final, recarga 5 s, sonido `escudo_listo.ogg`) y `system_shield_hud` (texto + barra, colores por estado) configurados en `shield.json` e `interface.json`. Web lista en `VideoJuegos/itch/rectangulos-bouncing-web.zip` (`pygbag --archive`); publicada en itch.io con el enlace en `README.txt`.

---

## Semana 5: cada pantalla en su cuarto

### En palabras simples

Esta semana empieza con diseño. Jesse Schell, autor de *The Art of Game Design*, arma un mapa de todo lo que toca un diseñador: el diseñador crea una experiencia, esa experiencia ocurre en un lugar, genera una experiencia de juego, y así sigue. Para no perderse en tanto tema, Schell lo reorganizó en **cartas de lentes**. Cada carta es una forma de mirar tu juego con preguntas concretas. El video pone como ejemplo la carta 17 de la primera edición, el **lente del placer**: ¿qué experiencia placentera le estoy dando al jugador? Hasta propone, medio en broma, dormir con la carta del problema más difícil debajo de la almohada.

El tema que más destaca el video es la **audiencia**: para quién es el juego y qué le parece divertido a esa persona. Schell la mira por edad (por ejemplo, niños de 4 a 6 años que juegan con sus papás, o adultos de 25 a 35 que se dividen entre jugadores casuales con familia y *hardcore gamers*) y por género, con una advertencia clara: son tendencias, no reglas, y no se debe excluir a nadie. También cita las clasificaciones de LeBlanc (ocho placeres) y de Bartle (cuatro tipos de jugador).

Luego viene lo técnico. Una **escena** es un "cuarto" del juego con sus propias entidades, sistemas y controles: el menú, la partida, el game over. En vez de meter todo en `GameEngine`, cada cuarto vive en su propia clase. El motor queda como portero: maneja la ventana, el reloj y el dibujo, y sabe en qué cuarto estás. Cada escena tiene su propio mundo ECS. Para cambiar de cuarto se pide el cambio y el motor lo hace al final de la vuelta, nunca a la mitad.

Por último, el **gameloop avanzado**. Lo que usamos desde la semana 1 es **tiempo variable**: multiplicamos todo por `delta_time`. Funciona, pero si el computador se traba y el delta salta a un segundo, una bola puede atravesar una pared sin chocar (el **problema del túnel**) y el resultado cambia de una máquina a otra (falta de **determinismo**). La solución es el **tiempo fijo**: se acumula el tiempo real y se simula en pasos siempre iguales. Los motores grandes usan las dos cosas a la vez: `Update` variable y `FixedUpdate` fijo. Esto es de referencia; en el curso no se pide implementarlo.

### Ejemplo en tu juego

Hoy tu `GameEngine` del space shooter hace todo: en `_create` crea al jugador, el escudo, el spawner y los textos; en `_update` corre los sistemas del Hunter, las balas y las explosiones; en `_do_action` atiende disparo, escudo y pausa. Con escenas, todo eso se muda a una `PlayScene`. El motor solo conserva la ventana, el reloj y el `while`.

La pausa también cambia de casa. Tú la tienes en el motor con `self.is_paused` y `_toggle_pause`. En el demo la pausa vive dentro de la escena de juego como `self._paused`, porque en el menú no tiene sentido pausar nada.

Con escenas tu juego quedaría así: un `MenuScene` que dice "PRESS Z TO START", la `PlayScene` con el jugador, el Hunter y el escudo, y un `GameOverScene` cuando te destruyen. Cuando una bala enemiga te mata, el sistema de colisión no cierra el juego: llama `scene.switch_scene("GAME_OVER_SCENE")`. Al terminar ese frame, el motor limpia el mundo de la partida y crea el de game over.

Para el proyecto en grupo (Bosconian) esto no es opcional. En la sesión sincrónica dijeron que el patrón de escena **se evalúa**: si no está, es un punto menos. Bosconian necesita al menos menú, juego y game over, y probablemente una pantalla entre rondas. Las vidas, el puntaje y el high score deben sobrevivir al cambio de escena; para eso el profesor sugirió un servicio de estado del juego en el Service Locator.

### Cómo se ve en el código

El demo de esta semana es un Arkanoid (bola, paleta y bloques) en `ECS_05_DEMO/`. Todo lo que sigue es copia exacta de sus archivos.

**El arranque** (`main.py`)

```python
if __name__ == "__main__":
    engine = GameEngine()
    engine.run("MENU_SCENE")
```

- **`run("MENU_SCENE")`:** ahora `run` recibe el nombre de la escena inicial. Antes no recibía nada.

**El motor guarda un diccionario de escenas** (`src/engine/game_engine.py`)

```python
        self._scenes:dict[str, Scene] = {}
        self._scenes["MENU_SCENE"] = MenuScene(self)
        self._scenes["LEVEL_01"] = PlayScene("assets/cfg/level_01.json", self)
        self._scenes["WIN_SCENE"] = WinScene(self)
        self._scenes["GAME_OVER_SCENE"] = GameOverScene(self)
        self._current_scene:Scene = None
        self._scene_name_to_switch:str = None
```

- **`self._scenes`:** un diccionario de nombre a escena. Todas se crean una sola vez, al iniciar.
- **`MenuScene(self)`:** cada escena recibe al motor (`self`) para poder pedirle cambios después.
- **`PlayScene("assets/cfg/level_01.json", self)`:** la escena de juego además recibe su archivo de nivel. Así se sigue respetando el diseño orientado a datos.
- **`self._current_scene`:** la escena que se está ejecutando ahora.
- **`self._scene_name_to_switch`:** el "papelito" donde se anota a qué escena ir. Empieza en `None`.
- **Lo que ya no está:** `self.ecs_world` desapareció del motor. Ahora cada escena tiene el suyo.

**El ciclo, ahora delegando** (`game_engine.py`)

```python
    def run(self, start_scene_name:str) -> None:
        self.is_running = True
        self._current_scene = self._scenes[start_scene_name]
        self._create()
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            self._handle_switch_scene()
        self._do_clean()
```

```python
    def _create(self):
        self._current_scene.do_create()

    def _process_events(self):
        for event in pygame.event.get():
            self._current_scene.do_process_events(event)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        self._current_scene.simulate(self._delta_time)

    def _draw(self):
        self.screen.fill(self._bg_color)        
        self._current_scene.do_draw(self.screen)
        pygame.display.flip()
```

- **Mismo esqueleto de siempre:** `_create`, luego `_calculate_time`, `_process_events`, `_update`, `_draw` dentro del `while`.
- **Cada método le pasa el trabajo a `self._current_scene`.** El motor ya no sabe de bolas ni de bloques.
- **`_calculate_time` no delega:** el reloj y `self._delta_time` son comunes a todas las escenas.
- **`_draw` delega a medias:** el motor limpia la pantalla y hace `flip`; la escena dibuja en medio.
- **`_handle_switch_scene()`:** paso nuevo, siempre el último de la vuelta.
- **Ojo con el nombre:** al final se llama `self._do_clean()`, no `_clean()` como en tu motor.

**Cómo se cambia de escena** (`game_engine.py`)

```python
    def switch_scene(self, new_scene_name:str):
        self._scene_name_to_switch = new_scene_name
```

```python
    def _handle_switch_scene(self):
        if self._scene_name_to_switch is not None:
            self._current_scene.clean()
            self._current_scene = self._scenes[self._scene_name_to_switch]
            self._current_scene.do_create()
            self._scene_name_to_switch = None
```

- **`switch_scene` no cambia nada todavía.** Solo anota el nombre en `_scene_name_to_switch`.
- **`_handle_switch_scene` hace el cambio real al final del frame:** limpia la escena actual con `clean()`, toma la nueva del diccionario, la crea con `do_create()` y borra el papelito.
- **¿Por qué esperar?** Si el cambio pasara en mitad de `_update`, los sistemas que faltan seguirían corriendo sobre un mundo ya borrado. Esperando, el siguiente frame arranca limpio con la escena nueva.
- **No hay manejo de errores:** si pides un nombre que no está en `_scenes`, sale un `KeyError`.

**La clase base `Scene`** (`src/engine/scenes/scene.py`)

```python
class Scene:
    def __init__(self, game_engine:'src.engine.game_engine.GameEngine') -> None:
        self.ecs_world = esper.World()
        self._game_engine:src.engine.game_engine.GameEngine = game_engine
        self.screen_rect = self._game_engine.screen.get_rect()

    def do_process_events(self, event:pygame.event):
        system_input(self.ecs_world, event, self.do_action)

    def simulate(self, delta_time):
        self.do_update(delta_time)
        self.ecs_world._clear_dead_entities()

    def clean(self):
        self.ecs_world.clear_database()
        self.do_clean()
    
    def switch_scene(self, new_scene_name:str):
        self._game_engine.switch_scene(new_scene_name)

    def do_create(self):
        pass

    def do_update(self, delta_time:float):
        pass

    def do_draw(self, screen):
        system_rendering(self.ecs_world, screen)

    def do_action(self, action:CInputCommand):
        pass
    
    def do_clean(self):
        pass
```

- **`self.ecs_world = esper.World()`:** el mundo ECS ahora es de la escena. Un mundo por escena.
- **`self._game_engine`:** referencia al motor. Casi solo se usa para `switch_scene`.
- **`self.screen_rect`:** el rectángulo de la pantalla, para los sistemas de bordes.
- **`simulate` y `clean` son "plantillas":** hacen lo que toda escena necesita (borrar entidades muertas, vaciar el mundo) y llaman al gancho `do_update` o `do_clean` que cada hija rellena.
- **`do_process_events` y `do_draw` ya traen comportamiento:** el input con `system_input` y el dibujo con `system_rendering`. Se pueden sobrescribir si hace falta algo especial.
- **`do_create`, `do_update`, `do_action`, `do_clean`:** vacíos. Cada escena hija los llena.

**Una escena sencilla: el menú** (`src/game/menu_scene.py`)

```python
class MenuScene(Scene):
    
    def do_create(self):
        create_text(self.ecs_world, "MAIN MENU", 16, 
                    pygame.Color(50, 255, 50), pygame.Vector2(320, 150), TextAlignment.CENTER)
        create_text(self.ecs_world, "PRESS Z TO START GAME", 11, 
                    pygame.Color(255, 255, 0), pygame.Vector2(320, 210), TextAlignment.CENTER)
        create_text(self.ecs_world, "Arrows to MOVE - P to PAUSE", 8, 
                    pygame.Color(150, 150, 255), pygame.Vector2(320, 250), TextAlignment.CENTER)
        
        start_game_action = self.ecs_world.create_entity()
        self.ecs_world.add_component(start_game_action,
                                     CInputCommand("START_GAME", pygame.K_z))
        
    def do_action(self, action: CInputCommand):
        if action.name == "START_GAME":
            self.switch_scene("LEVEL_01")
```

- **El menú también es ECS:** los textos son entidades, y la tecla Z es una entidad con `CInputCommand("START_GAME", pygame.K_z)`.
- **`do_action`:** cuando llega `"START_GAME"`, pide ir a `"LEVEL_01"`.
- `GameOverScene` y `WinScene` son casi iguales: Z dispara `"RETRY_GAME"` (vuelve a `"LEVEL_01"`) y ESC dispara `"QUIT_TO_MENU"` (vuelve a `"MENU_SCENE"`).

**La escena de juego** (`src/game/play_scene.py`)

```python
    def __init__(self, level_path:str, engine:'src.engine.game_engine.GameEngine') -> None:
        super().__init__(engine)
        with open(level_path) as level_file:
            self.level_cfg = json.load(level_file)
        with open("assets/cfg/paddle.json") as paddle_file:
            self.paddle_cfg = json.load(paddle_file)
        with open("assets/cfg/ball.json") as ball_file:
            self.ball_cfg = json.load(ball_file)
        with open("assets/cfg/blocks.json") as blocks_file:
            self.blocks_cfg = json.load(blocks_file)
        
        self._paddle_ent = -1
        self._paused = False
```

- **Los JSON se leen en `__init__`, una sola vez.** Las entidades, en cambio, se crean en `do_create` cada vez que se entra a la escena.
- **`self._paused`:** la pausa vive aquí, no en el motor.

```python
    def do_update(self, delta_time: float):
        system_screen_paddle(self.ecs_world, self.screen_rect)
        system_screen_ball(self.ecs_world, self.screen_rect, self)
        system_block_count(self.ecs_world, self)
        
        if not self._paused:
            system_movement(self.ecs_world, delta_time)
            system_collision_ball_block(self.ecs_world, delta_time)
            system_collision_paddle_ball(self.ecs_world, self.ball_cfg["velocity"])
```

- **Esta lista de sistemas antes estaba en `GameEngine._update`.** Ahora es propia de la escena.
- **La pausa es igual a la tuya:** si `_paused` es verdadero, no se llama a los sistemas de movimiento ni de colisión.
- **`self` se pasa a dos sistemas** para que puedan pedir un cambio de escena.

```python
    def do_clean(self):
        self._paused = False
```

```python
        if action.name == "PAUSE" and action.phase == CommandPhase.START:
            self._paused = not self._paused
            self.p_txt_s.visible = self._paused
```

- **`do_clean`:** deja la pausa apagada para la próxima vez que se entre.
- **`self.p_txt_s.visible`:** el texto "PAUSED" se crea siempre en `do_create` y solo se muestra u oculta con el atributo `visible` de `CSurface`. Tú lo creabas y borrabas en cada pausa.

**Un sistema que cambia de escena** (`src/ecs/systems/s_block_count.py`)

```python
def system_block_count(world: esper.World, scene:Scene):
    component_count = len(world.get_components(CTagBlock))
    if component_count <= 0:
        scene.switch_scene("WIN_SCENE")
```

- Cuenta cuántas entidades tienen `CTagBlock`. Si no queda ninguna, ganaste.
- Lo mismo hace `system_screen_ball`: si la bola sale por abajo (`cuad_rect.bottom > screen_rect.height`), llama `scene.switch_scene("GAME_OVER_SCENE")`.

**Texto que cambia** (`c_changing_text.py` y `s_rendering.py`)

```python
class CChangingText:
    def __init__(self, text:str, font:pygame.font.Font) -> None:
        self.font = font
        self.text = text
```

```python
        # CASO ESPECIAL CUANDO EL TEXTO CAMBIA
        # SE DEBE VOLVER A CREAR LA SUPERFICIE
        if world.has_component(ent, CChangingText):
            c_txt = world.component_for_entity(ent, CChangingText)
            c_s.surf = c_txt.font.render(c_txt.text, True, c_s.color)
```

- Sirve para un puntaje o un contador: cambias `c_txt.text` y el sistema de dibujo vuelve a generar la imagen del texto en cada frame.
- En el demo ninguna entidad lo usa todavía. Queda listo para el puntaje de tu proyecto.

### Notas técnicas

**S5.1 El arte del diseño (Jesse Schell)**
- Schell: autor de *The Art of Game Design*, profesor del Entertainment Technology Center de Carnegie Mellon y CEO de Schell Games.
- Mapa conceptual: diseñador → experiencia → lugar → experiencia de juego → etc.
- Cartas de lentes. Ejemplo: carta 17 (primera edición), lente del placer. Uso "dormir sobre la carta".
- Audiencia por edad: 4 a 6 años juegan con sus padres y necesitan cambios de reglas. 25 a 35 años: casuales con familia y *hardcore gamers*.
- Audiencia por género, según Schell: hombres, competencia, destrucción, retos espaciales, ensayo y error. Mujeres, emociones, mundo real, cuidar y crecer personajes, retos verbales, aprender con ejemplos. El video insiste en no discriminar: diseña para un público, pero prepárate para otros.
- Otras clasificaciones: LeBlanc, 8 placeres; Bartle, 4 tipos. El video no las enumera. Por referencia general (no del video): LeBlanc = sensación, fantasía, narrativa, reto, compañerismo, descubrimiento, expresión y sumisión; Bartle = triunfadores, exploradores, socializadores y asesinos.

**S5.2 Manejo de escenas**
- Escena = entorno con lógica, controles y acciones distintos (entidades, sistemas, inputs).
- Tipos: título, menú, juego principal, game over, video o animación.
- Diseño OOP simple: `GameEngine` maneja lo común; `Scene` es una clase base "abstracta" que siempre se hereda (en el video se llama `BaseScene`; en el demo es `Scene`).
- Cambios en el motor: diccionario de escenas, escena actual, nombre de escena a cambiar y `_handle_switch_scene()` al final del loop.
- El video dice que `simulate` limpia muertos y luego actualiza. En el código es al revés: `do_update` primero y `_clear_dead_entities()` después.
- Defensa del profesor: OOP no es "el demonio". Las escenas usan OOP por fuera y ECS por dentro, y siguen leyendo JSON.
- Mundo real: Unity `.unity` (YAML), Unreal `level.umap`, Godot `.tscn` (los subtítulos dicen "tscene"; en Godot todo nodo puede ser una escena). Subescenas para mundos abiertos y MMO. Frameworks como XNA y HaxeFlixel también tienen escenas con un `switch`.

**S5.3 Gameloop avanzado**
- Tiempo variable: `pos += vel * delta_time`. Problemas: túnel, falta de determinismo, flotantes distintos entre procesadores (ARM, Intel, AMD) y no aprovecha varios núcleos.
- Tiempo fijo con acumulador. Pseudocódigo según el video (no está en el demo):
  - `acumulador += delta_time` en cada vuelta.
  - `mientras acumulador >= tiempo_por_ciclo: simular(tiempo_por_ciclo); acumulador -= tiempo_por_ciclo`.
  - `tiempo_por_ciclo = 1/60` (o `1/30`). Luego se dibuja siempre, una vez.
- Ventaja: cada simulación usa el mismo delta, así que es determinista.
- Riesgo: si simular tarda más que `tiempo_por_ciclo`, el acumulador crece en vez de bajar.
- Motores grandes: `Update` (variable, para lo visual y suave) y `FixedUpdate` (fijo, para física y fuerzas). Unity recomienda `FixedUpdate` solo para física.
- Dibujar y actualizar están desacoplados. Eso permite hilos, interpolar el dibujo entre pasos de física y usar la GPU.
- Multijugador: evitar decimales. Por eso `clock.tick` devuelve milisegundos enteros, y Unreal usa enteros para rotaciones (según el video).
- Unity: un solo hilo; hilo principal más hilo de render; *worker threads* con jobs; y jobs hablando directo con la GPU (consolas). El video asocia uno a WebGL y otro a móviles, pero el profesor dice "si no estoy mal": tómalo como aproximado.

**Mapa del demo (`ECS_05_DEMO/`)**
- `main.py`: `GameEngine().run("MENU_SCENE")`.
- `src/engine/game_engine.py`: ventana, reloj, diccionario `_scenes`, `switch_scene`, `_handle_switch_scene`.
- `src/engine/scenes/scene.py`: clase base `Scene`.
- `src/game/menu_scene.py`, `play_scene.py`, `win_scene.py`, `game_over_scene.py`.
- `src/create/prefab_creator.py` (`create_square`, `create_sprite`), `prefab_creator_game.py` (`create_paddle`, `create_ball`, `create_play_field`, `create_block`, `create_game_input`), `prefab_creator_interface.py` (`TextAlignment`, `create_text`).
- Componentes: `CChangingText` (nuevo), `CSurface` con `visible`, `from_surface`, `from_text` y `get_area_relative`; `CInputCommand` con `CommandPhase`; tags `CTagBall`, `CTagBlock`, `CTagPaddle` y `CTagExplosion` (esta no se usa).
- Sistemas nuevos: `system_block_count`, `system_screen_ball`, `system_screen_paddle`, `system_collision_ball_block`, `system_collision_paddle_ball`.
- `assets/cfg/`: `window.json` (640x360, 60 fps), `level_01.json` (`paddle_start`, `ball_start`, `blocks_field`), `blocks.json` (tipos B1 a B6 con `image` y `score`), `ball.json` (`velocity` 200), `paddle.json` (`input_velocity` 200), `editor_level.json` (nivel para el editor de semanas siguientes).
- `ServiceLocator` con `images_service`, `sounds_service` y `fonts_service`. No tiene `configs_service` como el tuyo: cada escena abre sus JSON con `open`.

**API de escena, de un vistazo**

| Quién | Método | Qué hace |
|---|---|---|
| `GameEngine` | `run(start_scene_name)` | Elige escena inicial y arranca el loop |
| `GameEngine` | `switch_scene(new_scene_name)` | Anota el cambio en `_scene_name_to_switch` |
| `GameEngine` | `_handle_switch_scene()` | Al final del frame: `clean()`, cambio y `do_create()` |
| `Scene` | `switch_scene(name)` | Le pide el cambio al motor |
| `Scene` | `simulate(delta_time)` | `do_update` y borra entidades muertas |
| `Scene` | `clean()` | `clear_database()` y `do_clean()` |
| Hija | `do_create`, `do_update`, `do_action`, `do_clean` | Se sobrescriben |
| Hija | `do_draw`, `do_process_events` | Opcionales; ya traen comportamiento |

**Detalles del demo que conviene saber**
- `GameEngine._do_action` existe pero nadie lo llama. El input va por `Scene.do_process_events` → `system_input` → `self.do_action`.
- `FontsService.get` revisa `if path not in self._fonts`, pero guarda con la llave `(path, size)`. Por eso nunca encuentra la fuente y la vuelve a crear en cada llamada. Si lo copias, revisa `(path, size)`.
- En `create_ball`, el ángulo aleatorio se sobrescribe con `random_angle = math.pi/2`: la bola siempre sale recto hacia abajo. Parece una prueba que quedó.
- `system_block_count` corre aunque el juego esté en pausa. No afecta, porque el cambio solo se aplica al final del frame.
- El `esper` incluido en el demo dice `version = '2.4'`, aunque el curso habla de esper 2.5. La API que se usa (`World`, `get_components`, `clear_database`, `_clear_dead_entities`) es la misma.

**Sesión sincrónica (4 nov 2026)**
- El patrón de escena **se evalúa** en el proyecto. El gameloop avanzado y los hilos son solo de referencia.
- El motor queda como "administrador de ventana, rendering y escenas". Si metes en el motor algo que es de una escena, piénsalo dos veces.
- Estado global entre escenas: o una "escena global" que siempre corre, o un servicio en el Service Locator. Sugerencia directa: un servicio de estado del juego con vidas, puntaje y high score (guardar y cargar). Si hacen editor, un servicio de editor.
- Un mundo ECS por escena. Al cambiar puedes limpiar todo (como el demo) o dejar la escena quieta y volver después, como una "foto" que sirve para *save states*. Otra opción es un componente con el id de escena, pero al profesor no le gusta.
- Transiciones (fade): no le pongas transparencia a todos los sprites. Crea una entidad dedicada, un rectángulo del tamaño de la pantalla que se dibuja de último, con un componente tipo "fadeable" (alfa objetivo, velocidad con `delta_time`) y un sistema de fade. Al llegar al objetivo puede ejecutar un *callable* que haga `switch_scene`. La referencia se guarda en un servicio de estado del juego. Las transiciones de Bosconian parecen hechas con tiles animados.
- Pantalla de Bosconian: 256x256 con barras negras de 24 px arriba y abajo, así que el alto real es 208. A la derecha va la interfaz (minimapa, ronda): el área jugable es aún menor (los subtítulos dicen "208 por 192"; conviene revisarlo en el documento del proyecto). La nave no queda en el centro real de la pantalla. Las estrellas no deben verse bajo la interfaz.
- Ideas para eso: varios sistemas de dibujo o capas; un offset de dibujo como propiedad del sprite (ahí sí, porque todos lo necesitan); o dibujar el área de juego en otra `Surface` y luego hacer `blit` a la pantalla. `pygame.SCALED` escala la ventana sin deformar los píxeles.
- Hitboxes: cada entidad que choca debe tener su hitbox, no solo el rectángulo de la imagen.
- Error común en entregas: el juego funciona, pero la arquitectura no. Mucha lógica en la escena que debería estar en sistemas o componentes.
- Recomiendan el demo de *steering* de la semana 7: casi todos los enemigos de Bosconian, salvo bases, asteroides y minas, se mueven así. El editor es un bono que vale doble.
- Recursos actualizados con un logo "Kosmonian", todos con licencia libre. Los configs de ejemplo son opcionales.
- Logística: registrar el grupo en la hoja de Excel (sin eso no se pueden asignar envíos en Coursera). Las entregas de las semanas 5, 6 y 7 son opcionales y solo cuenta la final. Dudas por Slack.
- Pidieron compilar para Windows (o web) aunque se desarrolle en Mac.
- Dibujo top-down con profundidad: ordenar por Y (z-index). esper no trae ordenamiento de entidades.

**Lecturas opcionales (S5.6)**
- *The Art of Game Design* y la app de lentes: schellgames.com/art-of-game-design
- "Personality and play styles: a unified model" (Game Developer): une las teorías de tipos de jugador.
- "Five ways games appeal to players" (Game Developer): clasifica por el deseo del momento, no por personalidad.
- "Object Oriented Game Programming: The Scene System" (Riverman Media): muy parecido a la implementación del curso.
- "How to write a game engine in pure C: State Manager": escenas como máquina de estados, con SDL.
- "Fix Your Timestep!" (Gaffer On Games): el artículo clásico del delta fijo.
- "Game Loop", de *Game Programming Patterns* (Robert Nystrom).
- "Fix your (Unity) timestep" (John Austin): consecuencias de tener dos loops.

---

## Semana 6: Herramientas propias y la razón real de ECS

### En palabras simples

Esta semana tiene dos mitades. La primera es práctica: cómo construir herramientas dentro de tu propio juego. La segunda es de fondo: por qué ECS es rápido de verdad, y no solo cómodo.

**Qué es una herramienta de desarrollo.**
Un motor de juego (game engine) es el programa que junta el trabajo de todo el equipo: arte, sonido, animación y código. El primer video dice algo clave. Un motor exitoso deja que el equipo agregue herramientas hechas a su medida. En Unity se hacen en C#, como una ventana más del editor. En Unreal se hacen con plugins. Por eso algunas empresas grandes siguen teniendo motores propios: conocen tan bien sus necesidades que les vale la pena.

**Motor vs. API.**
El profesor del segundo video lanza una pregunta: ¿qué diferencia a pygame, MonoGame o Raylib de Unity, Unreal o Godot? Su respuesta (él la presenta como opinión propia) son tres cosas:
1. Vistas de depurado.
2. Herramientas de edición.
3. Serialización.

Con pygame abres el editor de código y programas. Con Unity abres un editor de escenas. Esa es la diferencia. Quien arma su motor desde cero gana control total: crea las herramientas que necesita, sin adaptarse a la filosofía de otro.

**Vistas de depurado.**
El depurado clásico (breakpoints, asserts, el famoso `print`) resuelve errores de lógica. Pero no te deja *ver* el juego. A veces el problema es de jugabilidad: "no detecto la colisión, quisiera ver los rectángulos". Una vista de depurado es una capa especial que dibuja eso encima del juego. Ejemplos del video: cajas de colisión y movimiento, estadísticas de rendimiento (frames, milisegundos) y una consola interactiva en pantalla, que es como "un print avanzado".

**Herramientas de edición.**
Van desde lo más simple hasta lo muy elaborado:
- Un menú de debug o de trucos con una tecla: reiniciar nivel, cargar otro nivel, vida infinita, todo el dinero. Sirve para llegar rápido al punto que quieres probar.
- Editores visuales: Blueprints en Unreal (código en cajitas), Shader Graph para efectos, máquinas de estados para animación, editores de diálogo, de audio, de IA.
- Editores de mapas. Según el profesor, Unity, Unreal y Godot son, en esencia, editores de mapas: pones objetos y los modificas.

La idea de fondo es de servicio: "uno no pone a un artista a programar, uno le crea una herramienta".

**Serialización.**
Es convertir objetos en bytes para guardarlos en memoria, en una base de datos o en un archivo. Sin eso, todo lo que editas se pierde. Hay formatos de texto (XML, JSON, YAML; el profesor menciona que las escenas de Unity son YAML) y binarios. En el curso usamos JSON.

**Lo mínimo para un editor en ECS.**
El profesor propone un editor peculiar: no es "editar y luego darle play", sino uno que vive dentro del juego en ejecución. Los ingredientes:
- Un modo edición que se prende y se apaga con una tecla (él sugiere Tab).
- Acciones propias de ese modo: cambiar objeto, colocar entidad, mover, borrar.
- Apagar sistemas mientras editas. Si no llamas al sistema de movimiento, nada se mueve. Si no llamas a colisiones, no chocan.
- Una entidad cursor que sigue al mouse y sirve para "tocar" otras entidades.
- Una etiqueta que marca qué se puede editar, por ejemplo "arrastrable".
- Serializar y deserializar el resultado.

Su conclusión: ECS permite tener herramientas de edición "con poco esfuerzo y alto impacto". Un editor es, al final, unos componentes y unos sistemas más.

**La razón real de ECS: data locality y coherencia de caché.**
Hasta ahora usamos ECS por arquitectura: pensar en datos y en cómo se transforman. El tercer video dice que eso es válido, pero que la razón de rendimiento es otra: la memoria caché.

- La caché es una memoria muy pequeña y muy rápida, pegada al CPU. Hay niveles: L1 (la más pequeña y rápida), L2, L3 y después la RAM. La caché es cara de fabricar; la RAM es barata.
- Cuando el CPU pide un dato a la RAM, no trae solo ese dato. Trae un bloque de memoria de alrededor, porque supone que lo siguiente que vas a pedir está al lado.
- Si lo que pides ya está en caché, es un *hit*. Si no está, es un *cache miss* y toca ir de nuevo a la RAM.
- En el equipo del profesor (Ryzen 3600), la RAM fue unas 70 veces más lenta que la L1.

Los dos experimentos en Python del video:
1. Una matriz de 10.000 x 10.000. Buscar el mínimo recorriendo fila por fila tomó unos 25 s. Recorriendo columna por columna, unos 42 s. Mismo algoritmo. La diferencia es que la fila completa sube a la caché, así que avanzar por ella da hit tras hit. Bajar por columnas da miss tras miss. Lección: iterar primero por filas.
2. Una lista de objetos (cada uno con posición, velocidad, métodos, etc.) contra una lista que solo guarda posiciones. Calcular la distancia mínima tomó 2,5 s con objetos y 1,87 s con la lista de posiciones. Los objetos quedan regados en la RAM; el método está en un lado y el atributo en otro. Una lista de posiciones es lineal: xyz, xyz, xyz.

Ahí está el puente con ECS. Un componente pequeño, guardado junto a los demás del mismo tipo, es amigo de la caché. Un sistema es una sola función que procesa muchas instancias, así que la caché de instrucciones casi no cambia. Un objeto con herencia y métodos salta por toda la memoria.

Las recomendaciones del profesor:
- Estructuras muy pequeñas que quepan en caché. Por eso partimos los componentes.
- Evitar jerarquías de clases y herencia: más indirección, más misses.
- Idealmente, una sola función que procesa muchas instancias.
- Sí, es un poco anti-OOP, y él lo admite.

Una advertencia honesta del video: Python no es bueno para esto. Sus listas y diccionarios son dispersos y uno no controla la alineación. esper usa listas y mapas y "espera lo mejor de Python". En el curso el objetivo era aprender a usar ECS, no optimizar. Los lenguajes que sí controlan la memoria son C, C++, Rust y Zig. NumPy existe justo por eso: arreglos compactos escritos en C. JavaScript creó arreglos nativos para WebGL y WebGPU. C# tiene `struct`.

Los términos "array of structs vs. struct of arrays" y "arquetipos" no aparecen en los subtítulos. El segundo experimento es, en la práctica, la idea de "lista de objetos vs. lista de un solo campo", pero el profesor no le pone ese nombre. Si quieres esos términos, la lectura de Game Programming Patterns sobre data locality es el lugar natural (no la verifiqué).

### Ejemplo en tu juego

Piensa en tu shooter de pygame: jugador, balas, enemigos, el Hunter, explosiones, escudo y pausa.

**Vista de rectángulos.**
¿Te ha pasado que una bala "atraviesa" a un enemigo y no sabes por qué? Con una vista de depurado de rectángulos verías la caja de cada entidad y su posición escrita encima. Si la caja del Hunter es más pequeña que su sprite, lo notas en un segundo. Es exactamente lo que hace `system_rendering_debug_rects` en la demo: recorre todo lo que tiene `CTransform` y `CSurface` y dibuja un borde verde.

**Vista de velocidades.**
Las balas salen torcidas o el Hunter persigue raro. Una vista que escriba el vector de velocidad junto a cada entidad te dice qué pasa sin un solo `print`. En la demo es `system_rendering_debug_velocity`.

**Cómo prenderlas.**
Igual que tu pausa: una entidad con `CInputCommand` y una tecla. La demo usa Ctrl izquierdo para rotar entre "sin depurado", "rectángulos" y "velocidades". Tu pausa ya funciona con el patrón Command, así que esto es casi copiar ese camino.

**Un editor de niveles para el proyecto Bosconian.**
En Bosconian hay bases espaciales, asteroides y minas repartidos por el mapa. Ubicarlos a mano en un JSON, adivinando coordenadas, es lento. Con la receta de la demo:
- Le pones un componente tipo `CEditorDraggable` a las bases y asteroides.
- Un cursor con `CEditorFollowMouse` y un `CEditorPlacer` con la lista de tipos que se pueden poner.
- Tab entra al modo edición y pausa el mundo.
- Clic izquierdo coloca o arrastra; clic derecho cambia el tipo; clic del medio borra.
- Enter recorre las entidades y escribe un JSON con tipo y posición.

Así cualquiera del grupo puede diseñar un nivel sin tocar código. Eso es justo lo que el profesor llama "crear una herramienta para el otro".

**Code smells y tu proyecto.**
La lista de code smells de esta semana es la vara con la que se va a mirar el proyecto final. Si el `update()` de tu escena de juego tiene muchos `if`, sumas y preguntas, es señal de que falta un sistema. Ojo: la propia demo concentra la lógica del editor en `_do_editor_action` dentro de la escena (más abajo lo comento). Para el proyecto conviene llevar esa lógica a sistemas.

### Cómo se ve en el código

**Los tres componentes del editor (`src/ecs/components/editor/`)**

```python
class CEditorDraggable:
    def __init__(self) -> None:
        self.is_dragging = False
```

```python
class CEditorFollowMouse:
    def __init__(self) -> None:
        pass
```

```python
class CEditorPlacer:
    def __init__(self, types:list[str]) -> None:
        self.types = types
        self.curr_type_idx = 0
```

- `CEditorDraggable` es la "etiqueta arrastrable" del video. `is_dragging` dice si el mouse la está llevando ahora.
- `CEditorFollowMouse` es una etiqueta pura: no tiene datos.
- `CEditorPlacer` guarda la lista de tipos que el cursor puede colocar (`types`) y cuál está activo (`curr_type_idx`).

**Los bloques nacen arrastrables (`prefab_creator_game.py`)**

```python
def create_block(world:esper.World, type:str, block_info:dict, pos:pygame.Vector2):
    surf = ServiceLocator.images_service.get(block_info["image"])
    block_ent = create_sprite(world, pos, None, surf)
    world.add_component(block_ent, CTagBlock(type))
    world.add_component(block_ent, CEditorDraggable())
```

- Es el único cambio en este archivo frente a la semana 5: la línea de `CEditorDraggable()`.
- `CTagBlock(type)` guarda `b_type` ("B1"..."B6"). Eso es lo que luego se serializa.

**Las acciones del editor (`src/create/prefab_creator_debug.py`)**

```python
def create_debug_input(world:esper.World):
    switch_debug_view = world.create_entity()
    world.add_component(switch_debug_view,
                        CInputCommand("TOGGLE_DEBUG_VIEW", 
                                      pygame.K_LCTRL))
    switch_editor_mode = world.create_entity()
    world.add_component(switch_editor_mode,
                        CInputCommand("TOGGLE_EDITOR", 
                                      pygame.K_TAB))
```

- Cada acción es una entidad con `CInputCommand`, igual que LEFT o PAUSE.
- Más abajo en la misma función: `MOUSE_MOVE` (`pygame.MOUSEMOTION`), `DRAG_BLOCK` y `PLACE_ENTITY` (ambos `pygame.BUTTON_LEFT`), `CHANGE_ENTITY` (`pygame.BUTTON_RIGHT`), `DELETE_ENTITY` (`pygame.BUTTON_MIDDLE`) y `SAVE_LEVEL` (`pygame.K_RETURN`).
- `system_input` (sin cambios frente a la semana 5) ya llenaba `c_input.mouse_pos` en los eventos del mouse.

```python
def create_editor_placer(world:esper.World):
    placer_entity = create_square(world,
                                  pygame.Vector2(10, 10),
                                  pygame.Color(0, 255, 0),
                                  pygame.Vector2(0,0),
                                  pygame.Vector2(0,0))
    placer_s = world.component_for_entity(placer_entity, CSurface)
    placer_s.visible = False
    world.add_component(placer_entity,
                        CEditorFollowMouse())
    world.add_component(placer_entity,
                        CEditorPlacer([None, "B1", "B2", "B3", "B4", "B5", "B6"]))
    return placer_entity
```

- El cursor es un cuadrado verde de 10x10, invisible hasta entrar al modo edición.
- `None` en la lista significa "modo mano": el cursor no coloca, solo arrastra.

**Los sistemas del editor**

```python
def system_follow_mouse(world:esper.World, mouse_pos:pygame.Vector2):
    components = world.get_components(CTransform, CEditorFollowMouse)
    for _, (c_t, _) in components:
        c_t.pos.x = mouse_pos.x
        c_t.pos.y = mouse_pos.y
```

```python
def system_editor_draggable(world:esper.World, mouse_pos:pygame.Vector2):
    components = world.get_components(CTransform, CEditorDraggable)
    for _, (c_t, c_d) in components:
        if c_d.is_dragging:
            c_t.pos.x = mouse_pos.x
            c_t.pos.y = mouse_pos.y
```

- Son casi idénticos. La diferencia: el cursor sigue siempre; un bloque solo cuando `is_dragging` es verdadero.
- Nota: `s_follow_mouse.py` quedó en `src/ecs/systems/`, no en `systems/editor/`, aunque su componente sí está en `components/editor/`.

**Cuándo corren (`play_scene.py`)**

```python
    def do_update(self, delta_time: float):
        system_screen_paddle(self.ecs_world, self.screen_rect)
        system_screen_ball(self.ecs_world, self.screen_rect, self)
        system_block_count(self.ecs_world, self)
        
        if not self._paused:
            system_movement(self.ecs_world, delta_time)
            system_collision_ball_block(self.ecs_world, delta_time)
            system_collision_paddle_ball(self.ecs_world, self.ball_cfg["velocity"])
        
        if self._editor_mode:
            system_follow_mouse(self.ecs_world, self._mouse_pos)
            system_editor_draggable(self.ecs_world, self._mouse_pos)
```

- Así se "apagan sistemas", como pide el video: con un `if`. Al entrar al editor se pone `self._paused = True`, y movimiento y colisiones dejan de correr.
- `self._mouse_pos` se actualiza en la acción `MOUSE_MOVE`.

**Entrar al modo edición**

```python
        if action.name == "TOGGLE_EDITOR" and action.phase == CommandPhase.START:
            self._editor_mode = not self._editor_mode
            self.placer_s.visible = self._editor_mode
            self.editor_text_s.visible = self._editor_mode
            if self._editor_mode:
                self._b_t.pos.x = self.level_cfg["ball_start"]["pos"]["x"]
                self._b_t.pos.y = self.level_cfg["ball_start"]["pos"]["y"]
                self._p_t.pos.x = self.level_cfg["paddle_start"]["pos"]["x"]
                self._p_t.pos.y = self.level_cfg["paddle_start"]["pos"]["y"]
                self._paused = True
                self.p_txt_s.visible = self._paused
```

- Al entrar, la bola y la paleta vuelven a su posición inicial del nivel. Es el "reiniciar a modo inicial" del video.
- Al salir no se despausa: hay que oprimir P. Lo deduzco del código; no lo vi en el video.

**Arrastrar con el cursor**

```python
        if action.name == "DRAG_BLOCK":
            b_type = self.placer_ed.types[self.placer_ed.curr_type_idx]
            if b_type is None:
                if action.phase == CommandPhase.START:
                    components = self.ecs_world.get_components(CTransform, CSurface, CEditorDraggable)
                    for _, (c_t, c_s, c_d) in components:
                        surf_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
                        placer_rect = CSurface.get_area_relative(self.placer_s.area, self.placer_t.pos)
                        if surf_rect.colliderect(placer_rect):
                            c_d.is_dragging = True
                else:
                    components = self.ecs_world.get_component(CEditorDraggable)
                    for _, c_d in components:
                        c_d.is_dragging = False
                self.editor_text_saved_s.visible = False
```

- Solo arrastra si el tipo activo es `None` (modo mano).
- Al oprimir: todo lo arrastrable que choque con el rect del cursor queda con `is_dragging = True`. Al soltar, todos vuelven a `False`.
- `get_area_relative` (de `CSurface`) copia el rect y le pone `topleft` en la posición dada.

**Cambiar, colocar y borrar**

```python
        if action.name == "PLACE_ENTITY" and action.phase == CommandPhase.START:
            b_type = self.placer_ed.types[self.placer_ed.curr_type_idx]
            if b_type is not None:
                create_block(self.ecs_world, 
                             b_type,
                             self.blocks_cfg[b_type], 
                             self._mouse_pos - pygame.Vector2(1,1))
            self.editor_text_saved_s.visible = False
```

- Colocar reutiliza el mismo prefab del juego, `create_block`. No hay un "bloque de editor" aparte.
- `CHANGE_ENTITY` hace `curr_type_idx += 1` y luego `%= len(self.placer_ed.types)` para dar la vuelta. Cambia la imagen del cursor por la del bloque, o por el cuadrado de `editor_cursor.json` si el tipo es `None`.
- `DELETE_ENTITY` usa el mismo `colliderect` y llama `self.ecs_world.delete_entity(ent)`.

**Serializar el nivel**

```python
            level["blocks_field"] = []
            components = self.ecs_world.get_components(CTransform, CTagBlock)
            for ent, (c_t, c_b) in components:
                block = {}
                block["type"] = c_b.b_type
                block["pos"] = {}
                block["pos"]["x"] = c_t.pos.x
                block["pos"]["y"] = c_t.pos.y
                level["blocks_field"].append(block)
            
            with open("assets/cfg/editor_level.json", "w") as write_file:
                json.dump(level, write_file, indent=4)
```

- Antes de esto arma `level["ball_start"]` y `level["paddle_start"]` con la misma forma, buscando `CTagBall` y `CTagPaddle`.
- El diccionario tiene la misma forma que `level_01.json`. Por eso el archivo guardado se puede cargar con el mismo código. Esa simetría es la clave de serializar y deserializar.
- Se guarda en `editor_level.json`, no encima de `level_01.json`. El juego sigue cargando `level_01.json` (ver `game_engine.py`). Para usar el nivel editado hay que copiarlo o renombrarlo a mano. Esto lo deduzco del código.

**Deserializar: recargar al crear la escena**

```python
    def do_create(self):
        # Recargar nivel, por si acaso estoy entrando 
        # y saliendo después de grabar
        with open(self.level_path) as level_file:
            self.level_cfg = json.load(level_file)
```

- `self.level_path` es nuevo en el constructor. Así, cada vez que entras a la escena se relee el JSON del disco.

**Las vistas de depurado**

```python
class DebugView(Enum):
    NONE = 0
    RECTS = 1
    VELOCITY = 2
```

```python
    def do_draw(self, screen):
        # Evaluar vistas de depurado y vistas normales
        if not self._debug_view == DebugView.RECTS:
            system_rendering(self.ecs_world, screen)
        else:
            system_rendering_debug_rects(self.ecs_world, screen)

        if self._debug_view == DebugView.VELOCITY:
            system_rendering_debug_velocity(self.ecs_world, screen)        
```

- RECTS reemplaza el render normal: solo se ven cajas. VELOCITY se dibuja encima del render normal.
- `TOGGLE_DEBUG_VIEW` rota NONE → RECTS → VELOCITY → NONE.

```python
    components = world.get_components(CTransform, CSurface)
    for _, (c_t, c_s) in components:
        if not c_s.visible:
            continue
        
        final_rect = pygame.Rect(c_t.pos, c_s.area.size)
        pygame.draw.rect(screen, pygame.Color(10, 255, 10), final_rect, 1, 2)
        pygame.draw.circle(screen, pygame.Color(255, 255, 255), final_rect.topleft, 2, 2)
```

- Borde verde de 1 px con esquinas redondeadas de 2 px y un punto blanco en la esquina superior izquierda (el origen).
- Después escribe `str(c_t.pos)` en blanco y `str(c_s.area.size)` en amarillo. La fuente sale de `ServiceLocator.fonts_service`.

### Notas técnicas

**S6.1 Herramientas de desarrollo**
- Motor = herramienta que integra el trabajo de artistas, músicos y programadores, y produce el juego final.
- Un motor maduro trae tienda de assets, soporta muchos formatos, facilita animaciones, estados y sprites, y deja programar en lenguajes visuales o tradicionales.
- Dos públicos: quien quiere hacer un juego o demo solo con el motor, y los equipos profesionales. Para el segundo, lo decisivo es poder agregar herramientas a la medida (Unity en C#, Unreal con plugins).

**S6.2 Herramientas en ECS**
- Tesis del profesor (opinión suya): motor vs. API = vistas de depurado + herramientas + serialización.
- Vistas de depurado: colisiones y movimiento, estadísticas y rendimiento, consola interactiva.
- Edición: menú de debug y trucos, scripting visual (Blueprints), Shader Graph, animación por estados, editores de mapas y tiles.
- Serialización: texto (XML, JSON, YAML) o binario. Escenas, modelos, animaciones.
- Mínimo en ECS: modo edición con Tab, acciones propias, apagar sistemas, cursor, etiqueta editable o arrastrable, guardar y cargar.
- Extensibilidad: tiendas de Unity, Unreal, Construct y GameMaker; el ejemplo de Doom, que dura décadas por sus herramientas de modificación.
- Conclusión: "ECS permite tener herramientas de edición con poco esfuerzo y alto impacto".

**S6.3 Data locality y coherencia de caché**
- Razón arquitectónica (pensar en datos) vs. razón de rendimiento (caché). Hay que conservar las dos.
- No hace falta ECS puro: Unity y Unreal usan "EC" (lógica dentro del componente), y Godot usa nodos en jerarquía. ECS se vende sobre todo para proyectos muy demandantes.
- Caché L1 < L2 < L3 < RAM. Hay caché de datos y de instrucciones. El CPU sube bloques vecinos a la caché.
- Latencias citadas (Ryzen 3600): L1 "unos 9 ns" según el subtítulo, L2 2,8 ns, L3 10,3 ns, RAM 67 ns. El "9" casi seguro es 0,9 ns, porque L1 no puede ser más lenta que L2 y el profesor dice que la RAM es "casi 70 veces más lenta". Por confirmar en el video.
- Tamaños de caché citados: 32 KB, "502 KB" y 16 MB. El 502 puede ser un error del subtítulo (quizás 512 KB).
- Experimento 1: matriz 10.000 x 10.000, ~25 s por filas vs. ~42 s por columnas.
- Experimento 2: lista de objetos ~2,5 s vs. lista de posiciones ~1,87 s.
- Un cache miss suele costar más que lo que ganas optimizando el algoritmo.
- Recomendaciones: componentes pequeños, evitar herencia, una función para muchas instancias.
- Python no controla la alineación. NumPy, los arreglos nativos de JS y `struct` en C# sí. esper usa listas y mapas.
- Las GPU son máquinas que procesan matrices y vectores alineados, con caché propia. Por eso "ECS es de los pocos patrones con aplicación directa en hardware".
- Quién lo usa, según el video: Rocket League, Overwatch, Unity DOTS, Unreal (para IA y Nanite), Phaser, Sony, Intel, Apple, Insomniac, Ubisoft, DICE y Riot.
- No se mencionan los términos AoS/SoA ni arquetipos.

**Mapa de archivos nuevos (ECS_06_DEMO frente a ECS_05_DEMO)**
- `src/ecs/components/editor/`: `c_editor_draggable.py`, `c_editor_follow_mouse.py`, `c_editor_placer.py`.
- `src/ecs/systems/editor/s_editor_draggable.py` y `src/ecs/systems/s_follow_mouse.py`.
- `src/ecs/systems/debug/`: `s_rendering_debug_rects.py`, `s_rendering_debug_velocity.py`.
- `src/create/prefab_creator_debug.py`: `create_debug_input`, `create_editor_placer`.
- `assets/cfg/editor_cursor.json`: tamaño 10x10 y color verde del cursor en modo mano.

**Archivos modificados**
- `play_scene.py`: casi todo el cambio. `DebugView`, `level_path`, `editor_cursor_cfg`, `_debug_view`, `_mouse_pos`, `_editor_mode`, recarga en `do_create`, `do_draw` propio, `do_clean` reinicia los modos, y `_do_editor_action` con MOUSE_MOVE, DRAG_BLOCK, CHANGE_ENTITY, PLACE_ENTITY, DELETE_ENTITY y SAVE_LEVEL.
- `prefab_creator_game.py`: `CEditorDraggable()` en `create_block`.
- `scene.py`: el parámetro pasa a `engine` y el atributo `_game_engine` pasa a público `game_engine`. Las escenas menú, victoria y game over ahora llaman `self.game_engine.switch_scene(...)`.
- `game_engine.py`: `_window_cfg` pasa a `window_cfg` (público).
- `level_01.json`: mismo contenido, pero con floats (`314.0`) y otro orden de claves. Parece regrabado por el editor.
- `window.json`: título "Arkanoid con editor".
- Cambios menores: `c_animation.py` usa `list[...]` en vez de `typing.List`, y hay comentarios corregidos.
- Curiosidad: el zip de la semana 5 ya traía un `editor_level.json`, que no está en la semana 6. Parece un archivo de salida que se coló.

**Controles de la demo**
- Ctrl izquierdo: rotar vista de depurado. Tab: modo edición. P: pausa. Esc: menú.
- En el editor: clic izquierdo arrastra (tipo `None`) o coloca; clic derecho cambia el tipo; clic del medio borra; Enter guarda.
- Detalle: `DRAG_BLOCK` y `PLACE_ENTITY` comparten `BUTTON_LEFT`. Lo que decide qué pasa es el tipo activo en `CEditorPlacer`.
- El texto en pantalla dice "PRESS ENTER SO SAVE" (errata del original).

**Code smells en ECS (lista completa, para el proyecto final)**
ECS:
- Si algo puede ser sistema + componente, no lo dejes en Engine ni en Scene.
- Lo que no use ECS no cuenta para la nota. Lo mismo vale para los demás patrones del curso (eventos, Service Locator, escenas, etc.).
- Muchas preguntas, asignaciones, `if` y cálculos en `update()` o `draw()`: falta un sistema.
- Puede haber sistemas dentro de sistemas. No es ortodoxo (los puristas lo ven como mucha indirección), pero según el autor puede tener sentido si la complejidad lo pide.
- Cada clase en su rol. Engine solo administra escenas. Scene solo administra mundos ECS, crea entidades y administra sistemas, "nada más".
- Muchos sistemas hechos con copy/paste que cambian poco: deberían ser un solo sistema donde los componentes marquen la diferencia.
- Si para arreglar un error propio de tu juego (no algo general como la pausa) tienes que mirar fuera de componentes y sistemas, tienes todo muy disperso fuera de ECS.
- Si "desactivar" un sistema exige más que comentar la llamada o cambiar una propiedad de un componente, no estás aplicando ECS bien.
- Tener un solo componente para un solo sistema está bien. Se recomienda guardar ese componente (o la entidad) en la escena o en un servicio, para acceder fácil desde otros sistemas.

Service Locator:
- Muchas cosas pueden ser un servicio. Ejemplos: el manejo de configuraciones JSON y las constantes o variables que trascienden escenas.

Comando simplificado (eventos):
- No invocar eventos ad hoc dentro de `update` o `draw`. Usar el sistema de eventos. A algunos no les gusta la comunicación indirecta, pero motores como Defold se comunican solo con eventos.

Ojo con la propia demo: `_do_editor_action` y el guardado viven en `PlayScene`, lo que choca con "Scene solo administra mundos y sistemas". Para el proyecto conviene pasar el guardado a un sistema o a un servicio.

**Lecturas opcionales (S6.6)**
- Herramientas: "What I Learned About Tools Development From Games Industry Legends" (UX de herramientas para el equipo), "Creating a Tools Pipeline for Horizon: Zero Dawn" (herramientas AAA) y "The 2019 Tech Toolbox" (herramientas indie).
- Data locality: "Pitfalls of Object Oriented Programming" (GCAP 09, de las primeras presentaciones sobre DOD), "Data Oriented Design in C++" (marca la generación moderna de DOD; "controversial pero muy conocido") y "Data locality" de Game Programming Patterns (la explicación completa y rápida).
- La página S6.4 apunta al sitio de la cohorte con la demo completa y aclara que el proyecto se puede estudiar y adaptar.

**Por confirmar**
- Las cifras de latencia y tamaño de caché (posibles errores del subtítulo).
- Si el video de la demo explica cómo pasar `editor_level.json` a `level_01.json`. No usé el .mp4.

---

## Semana 7: reglas simples, comportamientos que parecen listos

### En palabras simples

Esta semana tiene tres ideas. Las tres hablan de lo mismo desde lados distintos: cómo algo sencillo puede verse complejo, y cómo saber qué tan caro le sale eso a la máquina.

**Juego emergente.** Pones pocas reglas sencillas y, al combinarlas, aparece un comportamiento que nadie programó de forma directa. El ejemplo clásico es el Juego de la Vida de Conway: cada celda solo mira a sus vecinas, y aun así salen figuras que "caminan" por el tablero. En un juego pasa lo mismo cuando varios enemigos con reglas simples terminan pareciendo un escuadrón organizado. Lo bonito es que sorprende. Lo difícil es que, por lo mismo, cuesta diseñarlo y ajustarlo.

**Perfilado.** Un perfilador es una herramienta que te dice en qué se va el tiempo (o la memoria) de tu juego. La regla de oro del profesor: no optimices "por si acaso". Primero mide. Luego busca el cuello de botella: ¿lo lento es el `update` (CPU) o el `draw` (GPU)? Si lo lento es dibujar, mejorar la lógica no sirve de nada, y al revés.

**Steering behaviours (comportamientos de dirección).** Es una forma de darle "voluntad" a un enemigo sin una IA complicada. Cada comportamiento es una flecha (un vector) que empuja: "quiero ir hacia allá", "quiero alejarme de esto". Sumas las flechas y obtienes una sola. Pero el enemigo no gira de golpe hacia ella: su velocidad se va acercando poco a poco. Por eso el movimiento se ve suave, como de algo vivo, y no de robot.

Piensa en manejar un carro. No cambias de dirección teletransportándote; giras el timón un poco cada instante. Eso es *steering*: corregir un poco la velocidad en cada cuadro.

### Ejemplo en tu juego

Tu Hunter de la semana 3 ya persigue al jugador. En `CHASE` calcula `direction = pl_center - hunter_center`, la normaliza y la multiplica por `velocity_chase`. Funciona, pero tiene un detalle: **gira en seco**. Cada cuadro su velocidad salta directo a la nueva dirección. Se ve correcto, pero mecánico.

Con steering el Hunter se sentiría distinto:

1. **Buscar (seek) en vez de apuntar.** En `CHASE` no asignas la velocidad: la *mezclas* con la deseada. Así el Hunter traza curvas y, si el jugador lo esquiva rápido, se pasa de largo y tiene que corregir. Eso da sensación de inercia y le deja al jugador un momento para escapar.
2. **Perseguir (pursue).** En vez de apuntar a donde *está* el jugador, apunta a donde *va a estar*: su posición más su velocidad. Un Hunter así te corta el paso.
3. **Llegar (arrive) en `RETURN`.** Al volver a su `origin`, hoy puede temblar si se pasa del punto. Con "arrive" frena a medida que se acerca y se detiene al llegar a una distancia mínima. Luego pasa a `IDLE` sin vibrar.
4. **Huir (flee).** Si el jugador tiene el escudo activo, el Hunter podría sumar una flecha que lo aleja. Es la misma cuenta que "buscar", pero con el vector al revés.

La máquina de estados no desaparece. Sigue decidiendo **qué** quiere el Hunter (esperar, perseguir, volver). El steering decide **cómo** se mueve para lograrlo. Son dos capas que se llevan bien.

En el proyecto final (estilo Bosconian) esto pesa todavía más. Allí muchas naves enemigas persiguen al jugador al mismo tiempo. Si todas usan "buscar" puro, terminan encimadas en una sola bola. Si a cada una le sumas una flecha de **separación** (alejarse de las naves cercanas), aparece una formación que parece coordinada sin que la hayas programado. Eso es juego emergente en tu propio código. Ojo: el demo del curso **no** implementa separación; la idea sale de la clase (los "boids") y tocaría escribirla.

El demo de esta semana es un buen modelo a escala: una bola que va hacia los bloques azules (comida) y esquiva los rojos (peligro). Cambia "bola" por "nave enemiga", "bloque azul" por "jugador" y "bloque rojo" por "otra nave o asteroide", y tienes el esqueleto de un enemigo de Bosconian.

### Cómo se ve en el código

El demo `ECS_07_DEMO` no es el space shooter. Es una escena con una bola gris y 25 bloques al azar: cerca de la mitad azules (`"B1"`) y la otra mitad rojos (`"B5"`). La bola va al azul más cercano y se aleja del rojo más cercano. Al tocar cualquier bloque, ese bloque desaparece y nace otro del mismo tipo en un lugar al azar.

**El componente: dos flechas guardadas** (`src/ecs/components/c_steering.py`)

```python
class CSteering:
    def __init__(self) -> None:
        self.follow_vector:pygame.Vector2 = pygame.Vector2(0, 0)
        self.avoid_vector:pygame.Vector2 = pygame.Vector2(0, 0)
```

- **`follow_vector`:** la flecha de "quiero ir hacia allá" (hacia el bloque bueno).
- **`avoid_vector`:** la flecha de "quiero alejarme de esto" (del bloque malo).
- Es un componente puro de datos, como manda ECS. Se guardan en el componente (y no en variables locales) para que otro sistema, el de depuración, las pueda dibujar.

**Las fuerzas vienen del JSON** (`assets/cfg/ball.json`)

```json
{
    "image": "assets/img/ball_grey.png",
    "follow_force": 125,
    "avoid_force": 100
}
```

- **`follow_force`** (125): el largo de la flecha que atrae. En la práctica es la rapidez deseada en píxeles por segundo.
- **`avoid_force`** (100): el largo máximo de la flecha que repele. Es menor que la de atracción, así que la bola prefiere comer antes que huir, salvo que el rojo esté muy cerca.

**La bola nace quieta y con su `CSteering`** (`src/create/prefab_creator_game.py`)

```python
def create_ai_ball(world:esper.World, ball_cfg:dict) -> int:
    surf = ServiceLocator.images_service.get(ball_cfg["image"])
    pos = pygame.Vector2(320, 180)
    vel = pygame.Vector2(0,0)
    ball_ent = create_sprite(world, pos, vel, surf)
    world.add_component(ball_ent, CTagBall())
    world.add_component(ball_ent, CSteering())
    return ball_ent
```

- Nace en el centro de la ventana de 640x360 con velocidad cero. Toda su velocidad la va a construir el sistema de steering.
- **`CTagBall`** es la etiqueta que usa el sistema para encontrarla. Los bloques llevan **`CTagBlock(b_type)`**, que guarda el tipo `"B1"` o `"B5"`.

**El sistema: buscar + huir + suavizar** (`src/ecs/systems/s_ball_steering.py`)

```python
def system_ball_steering(world:esper.World, ball_cfg:dict, delta_time:float):
    components = world.get_components(CTransform, CVelocity, CSteering, CTagBall)
    for _, (c_t, c_v, c_bs, _) in components:
        closest_good, good_block_dist = _get_closest_good_block_pos(world, c_t.pos)
        closest_bad, bad_block_dist = _get_closest_bad_block_pos(world, c_t.pos)

        # Follow Vector
        c_bs.follow_vector = closest_good - c_t.pos
        desired_good_length = ball_cfg["follow_force"]
        c_bs.follow_vector.scale_to_length(desired_good_length)

        # Avoid Vector
        avoid_dampening = bad_block_dist / 50
        c_bs.avoid_vector = closest_bad - c_t.pos
        desired_bad_length = min(ball_cfg["avoid_force"], ball_cfg["avoid_force"] / avoid_dampening)
        c_bs.avoid_vector.scale_to_length(-desired_bad_length)

        final_vector = c_bs.follow_vector + c_bs.avoid_vector
        c_v.vel = c_v.vel.lerp(final_vector, delta_time * 5)
```

Vamos por partes.

- **`c_bs`:** "componente ball steering". **`c_t`** y **`c_v`** son, como siempre, transform y velocidad.
- **Buscar (follow):** `closest_good - c_t.pos` es la flecha que va de la bola al bloque azul. Restar "destino menos origen" siempre da la flecha que apunta al destino.
- **`scale_to_length(desired_good_length)`:** deja la dirección igual pero cambia el largo a 125. Equivale a `normalize() * 125`. No importa si el bloque está a 10 o a 500 píxeles: la flecha siempre mide lo mismo.
- **Huir (avoid):** `closest_bad - c_t.pos` apunta **hacia** el rojo. El truco está en `scale_to_length(-desired_bad_length)`: un largo **negativo** voltea la flecha. Ahora apunta lejos del rojo.
- **`avoid_dampening = bad_block_dist / 50`:** un "amortiguador" que crece con la distancia. Con eso, el largo de huida queda así:
  - `desired_bad_length = min(100, 100 / (dist / 50))`, o sea `min(100, 5000 / dist)`.
  - A 50 píxeles o menos: 100 (huye con toda la fuerza).
  - A 100 píxeles: 50. A 200 píxeles: 25. A 500 píxeles: 10.
  - Es decir, el miedo baja como 1/distancia. Un rojo lejano casi no molesta; uno cercano empuja fuerte. El `min` pone un techo para que no se dispare cuando está muy cerca.
- **`final_vector = follow_vector + avoid_vector`:** la suma de fuerzas que explica la clase. Es la velocidad que la bola *quisiera* tener. Su largo nunca pasa de 125 + 100 = 225.
- **`c_v.vel.lerp(final_vector, delta_time * 5)`:** aquí está el movimiento suave. `lerp` (interpolación lineal) avanza una fracción del camino entre la velocidad actual y la deseada:
  - `vel_nueva = vel + (final_vector - vel) * (delta_time * 5)`.
  - A 60 FPS, `delta_time` ≈ 0.0167, así que avanza cerca del 8 % del camino en cada cuadro.
  - Fíjate en la parte `(final_vector - vel)`: es "deseada menos actual". Es exactamente la fuerza de dirección (*steering force*) de la clase. El `delta_time * 5` hace de "fuerza de deseo" que la matiza. El `5` es un número fijo en el código, no viene del JSON.
- Luego `system_movement` mueve la bola con `c_t.pos += c_v.vel * delta_time`, como desde la semana 1. El steering **solo toca la velocidad**, nunca la posición.

**Buscar el bloque más cercano** (`s_ball_steering.py`)

```python
def _get_closest_good_block_pos(world:esper.World, ball_pos:pygame.Vector2) -> pygame.Vector2:
    min_pos:pygame.Vector2 = None
    min_dist = None
    components = world.get_components(CTransform, CSurface, CTagBlock)
    for _, (c_t, c_s, c_bl) in components:
        if c_bl.b_type == "B1":
            dist = c_t.pos.distance_to(ball_pos)
            if min_pos is None or dist < min_dist:
                min_pos = c_t.pos + c_s.area.center
                min_dist = dist
    return min_pos, min_dist
```

- Recorre todos los bloques y se queda con el `"B1"` más cercano. `_get_closest_bad_block_pos` es igual pero con `"B5"`.
- **`c_t.pos + c_s.area.center`:** `pos` es la esquina superior izquierda; sumarle el centro del `area` da el **centro** del bloque. Así la bola apunta al medio y no a la esquina.
- **`distance_to`:** distancia en línea recta entre dos puntos.
- Esto es una "percepción" muy simple: el agente mira su entorno y elige un objetivo. Es lo que la clase llama agentes que se basan en su entorno.

**Ver las flechas: sistema de depuración** (`src/ecs/systems/debug/s_steering_draw_debug.py`)

```python
def system_steering_draw_debug(world:esper.World, screen:pygame.Surface):
    components = world.get_components(CTransform, CSteering)
    for _, (c_t, c_bs) in components:
        # Draw vectors for debugging
        final_vector = c_bs.follow_vector + c_bs.avoid_vector        
        pygame.draw.line(screen, pygame.Color(0, 255, 0), c_t.pos, c_t.pos + c_bs.follow_vector)
        pygame.draw.line(screen, pygame.Color(255, 0, 0), c_t.pos, c_t.pos + c_bs.avoid_vector)
        pygame.draw.line(screen, pygame.Color(255, 255, 255), c_t.pos, c_t.pos + final_vector)
```

- Dibuja tres líneas desde la bola: **verde** = atracción, **roja** = huida, **blanca** = suma (velocidad deseada).
- La línea blanca es la deseada, no la velocidad real. La real va "detrás", alcanzándola con el `lerp`.
- Es la mejor herramienta para afinar `follow_force` y `avoid_force`: ves en vivo por qué la bola toma cada decisión.

**Cómo se conecta a la escena** (`src/game/play_scene.py`)

```python
    def do_update(self, delta_time: float):
        if not self._paused:
            system_movement(self.ecs_world, delta_time)
            system_ball_steering(self.ecs_world, self.ball_cfg, delta_time)
            system_collision_ball_block(self.ecs_world, self.blocks_cfg)        

    def do_draw(self, screen):
        super().do_draw(screen)
        if self._steering_debug:
            system_steering_draw_debug(self.ecs_world, screen)
```

```python
        if action.name == "TOGGLE_STEERING_DEBUG" and action.phase == CommandPhase.START:
            self._steering_debug = not self._steering_debug
            self.steering_debug_txt_s.visible = self._steering_debug
```

- El steering va en `do_update` (lógica). La depuración va en `do_draw`, **después** de `super().do_draw(screen)`, para que las líneas queden encima de los sprites.
- El sistema de depuración solo corre si `_steering_debug` es `True`. Se prende y apaga con **Ctrl izquierdo** (`CInputCommand("TOGGLE_STEERING_DEBUG", pygame.K_LCTRL)`). La **P** pausa.
- Todo es el patrón Command de la semana 2 y las escenas de las semanas 5-6: nada nuevo en el motor, solo un componente y dos sistemas más.

### Notas técnicas

Módulo 7: juego emergente, perfilado y steering behaviours. Fuentes: subtítulos `S7.1`–`S7.3`, demo `S7/ECS_07_DEMO/ECS_07_DEMO/`, lecturas `S7.6_lecturas_opcionales.json`. La página `S7.4` solo describe el demo y enlaza al sitio del curso (`misw-4407-desarrollo-de-videojuegos.github.io/web-cohorte-2026-12/`).

**S7.1 Juego emergente (Pablo Figueroa):**
- Definición (Rollings y Adams): comportamiento emergente = combinar reglas sencillas para producir un resultado complejo. Se nota solo tras bastante tiempo de juego.
- Juego de la Vida (John Conway, década de 1960). Reglas dichas en clase: nacimiento (celda apagada con exactamente 3 vecinas prendidas se prende), muerte por soledad (prendida con menos de 2 vecinas se apaga), muerte por sobrepoblación (prendida con 4 o más se apaga). La regla de supervivencia (2 o 3 vecinas sigue viva) no se dice explícita; queda implícita. Figuras: Glider, R-pentomino. Sitio sugerido: playgameoflife.com.
- Categorías de Jochen Fromm (el subtítulo dice "Times and Forms of Emergence"; la lectura confirma "Types and Forms of Emergence"):
  - **Nominal o intencional:** parte del diseño, sin sorpresas (la lavadora).
  - **Débil:** retroalimentación del todo a las partes (bandada de pájaros que rota al líder cansado).
  - **Múltiple:** varias leyes a la vez (mercado de valores).
  - **Fuerte:** comportamientos que salen de muchas acciones básicas de subcomponentes (genes, cultura).
- En videojuegos: niveles procedimentales en Tiny Wings, reglas simples de enemigos con comportamiento grupal en Halo, arco narrativo emergente en Façade. Clave de diseño: balance entre reglas libres y predecibles.

**S7.2 Perfilado:**
- Factores de rendimiento: CPU (`update`, física, IA), GPU (`draw`), memoria (latencia y espacio; sin RAM se usa disco y sube la latencia). Casi siempre el límite es CPU o GPU.
- Herramientas en Python (el profesor aclara que son básicas):
  - **cProfile:** perfilador de CPU nativo. Se ejecuta el juego con el perfil activado y se guarda en un archivo `.prof` (en clase, `perfil.prof`).
  - **SnakeViz:** `snakeviz perfil.prof` abre una página web con la vista *sunburst* (anillos; el tamaño del anillo es el tiempo, la profundidad es la pila de llamadas) y la vista *icicle* (estalactita, la más común en perfiladores). Abajo hay una tabla con tiempo y número de llamadas por función. Ejemplos que muestra: `draw sprite` en el sistema de rendering y `pygame.display.flip`.
  - **memory-profiler** (necesita **matplotlib**): se corre el juego y luego `mprof plot` muestra la memoria en el tiempo. Una curva en escalera que no baja indica una fuga (*leak*). Su juego arranca en unos 80 MB, casi todo del runtime de Python.
  - **GPU:** no hay perfilador en Python. Menciona herramientas externas.
  - Inseguro: los subtítulos no dictan los comandos completos. La forma estándar sería `python -m cProfile -o perfil.prof main.py`, `pip install snakeviz memory-profiler matplotlib` y `mprof run main.py`; esto es uso habitual de las herramientas, no una cita de la clase.
- **Trampa de `clock.tick`:** con un framerate, `tick` espera a propósito para no pasar de ese límite, y en el perfil aparece ocupando casi todo. El profesor dice que incluso `tick(0)` sigue esperando (él lo llama posible error de pygame). Para perfilar: llamar `tick()` **sin argumento**. En el motor del demo eso sería `_calculate_time` → `self._clock.tick(self._framerate)`. Solo para perfilar; al publicar conviene volver a limitar el framerate para evitar `delta_time` grandes.
- **Flujo de trabajo:** (1) perfila solo si hay un problema; evita la optimización prematura. (2) Identifica el cuello de botella: ¿CPU o GPU *bound*? En el demo, ¿`update` o `draw`? (3) Optimiza solo esa parte. Su ejemplo de clase quedó GPU *bound*: el sistema de rendering era lo más pesado.
- **Optimizaciones básicas:** algoritmos eficientes (solo tras encontrar el cuello); sistemas reutilizables (optimizar `system_movement` o el rendering mejora a todas las entidades); usar `get_components` en vez de pedir componentes uno a uno dentro del bucle; evitar asignaciones de memoria y estructuras grandes; ser amigo de la caché (por eso ECS y DOD ayudan).
- **Cómo guarda esper los componentes:** dos esquemas teóricos (arreglo por entidad o arreglo por componente). esper es "relajado": usa diccionarios, suficiente para el curso. Agregar y quitar componentes es lo más costoso en un ECS; muchos motores prefieren desactivar o marcar inválida una entidad antes que borrarla. Nota: el demo borra y crea un bloque en cada choque (`system_collision_ball_block`), justo lo que la clase dice que es caro, aunque a esta escala no importa.
- **Mundo real:** Unity Profiler (CPU con hilos principal, render y *workers*; Memory Profiler con *snapshots* comparables, por tipo de recurso, memoria C# y C++), Unreal (perfilador de rendimiento), RenderDoc (GPU, libre, captura un frame), Razor CPU/GPU de PlayStation, Microsoft PIX (CPU, GPU y memoria, también en Windows).
- Conclusión: el rendimiento es un requisito de calidad clave. Perfila si es necesario.

**S7.3 Steering behaviours:**
- Control autónomo de agentes que perciben su entorno. Tienen una velocidad y lo que cambia es su dirección. Cada comportamiento produce un vector-fuerza; se suman y el cambio es progresivo, no brusco. Advertencia del profesor: no es un curso de IA.
- **Boids / cardumen** (subtítulo: "Voids"): vector A = cohesión (ir al promedio de posición del grupo), vector B = separación (no pegarse a los otros), vector C = dirección hacia un objetivo. Su suma da la dirección.
- **Buscar (seek):** `deseada = (objetivo - pos).normalize() * |vel|`; `steering = (deseada - vel)` escalado a una fuerza (la "fuerza de deseo"); `vel = vel + steering`. También se puede suavizar con interpolación. Con fuerza pequeña gira despacio y puede pasarse y corregir.
- **Perseguir (pursue):** apuntar a `pos_objetivo + vel_objetivo` (donde *va a estar*) y repetir la misma cuenta.
- **Huir (flee):** igual que buscar con la dirección deseada negada.
- **Llegar (arrive):** reducir la fuerza a medida que se acerca y definir una distancia mínima; al llegar, detener. Sin esto, "buscar" tiembla alrededor del objetivo.
- Otros nombrados (plugin gratis de Unreal 5): wander (vagar), evade (evadir), collision avoidance (no es lo mismo que huir), leader following, path following, flocking. Plugins citados: Polarith (Unity) y comportamientos "mover a" en Construct.

**Qué implementa realmente el demo** (para no confundir):
- **Sí:** buscar (`follow_vector`) y huir con atenuación por distancia (`avoid_vector`), sumados y suavizados con `lerp`.
- **No:** perseguir, llegar, vagar, separación ni cohesión. No hay *arrive* porque la bola nunca necesita frenar: al tocar el bloque, este desaparece.
- **Diferencia con la fórmula de clase:** el demo no escala la dirección deseada a `|vel|` sino a `follow_force` fijo. Y en vez de `vel + steering * fuerza` usa `vel.lerp(final, delta_time * 5)`, que es matemáticamente `vel + (final - vel) * delta_time * 5`. Es la misma idea, con el factor ligado al tiempo.

**Mapa de archivos del demo:**
| Archivo | Qué aporta |
|---|---|
| `src/ecs/components/c_steering.py` | `CSteering(follow_vector, avoid_vector)` |
| `src/ecs/systems/s_ball_steering.py` | `system_ball_steering`, `_get_closest_good_block_pos`, `_get_closest_bad_block_pos` |
| `src/ecs/systems/debug/s_steering_draw_debug.py` | `system_steering_draw_debug` (líneas verde/roja/blanca) |
| `src/ecs/systems/s_collision_ball_block.py` | al chocar: `delete_entity(block_ent)` + `create_random_block` del mismo tipo |
| `src/create/prefab_creator_game.py` | `create_ai_ball`, `create_random_playfield` (25 bloques, `B5` si `random() > 0.5`), `create_game_input` (P y LCTRL) |
| `src/game/play_scene.py` | `PlayScene`: carga `ball.json` y `blocks.json`, `_paused`, `_steering_debug` |
| `src/engine/game_engine.py` | solo registra `"PLAY_SCENE"`; `_calculate_time` con `clock.tick(self._framerate)` |
| `assets/cfg/ball.json` | `follow_force` 125, `avoid_force` 100 |
| `assets/cfg/blocks.json` | `B1`–`B6` con `image` y `score`; el demo solo usa `B1` y `B5` (`score` no se usa) |
| `assets/cfg/window.json` | 640x360, 60 FPS; el título dice "Arkanoid con editor" (resto de un demo anterior) |
| `src/ecs/systems/s_block_count.py` | `system_block_spawner` cambia a `"WIN_SCENE"`; no se llama en esta escena |

**Fórmulas clave:**
- Dirección hacia algo: `objetivo - pos`. Alejarse: `-(objetivo - pos)` o `scale_to_length` con largo negativo.
- Largo de huida del demo: `min(avoid_force, avoid_force * 50 / dist)`.
- Suavizado: `vel = vel + (deseada - vel) * t`, con `t = delta_time * 5`.
- Velocidad deseada máxima del demo: `follow_force + avoid_force = 225` px/s.

**Detalles frágiles del demo** (útiles si copias el código al proyecto):
- `Vector2.lerp` exige `t` entre 0 y 1. Si `delta_time` pasa de 0.2 s (por ejemplo, al arrastrar la ventana), `delta_time * 5 > 1` y pygame lanza `ValueError`. Conviene `min(delta_time * 5, 1)`.
- `scale_to_length` falla con un vector de largo cero. Pasaría si la bola quedara justo sobre el objetivo; en el demo es raro porque el choque borra el bloque antes.
- Si `bad_block_dist` fuera 0, `avoid_dampening` sería 0 y habría división entre cero.
- Si no queda ningún `B1` (o ningún `B5`), la función devuelve `None` y la resta revienta. Con 25 bloques al azar es poco probable, pero posible.
- La distancia se mide desde la esquina (`c_t.pos`), pero el punto devuelto es el centro. Puede elegir un bloque que no es el más cercano por su centro. Diferencia pequeña.
- En `_get_closest_bad_block_pos` falta `min_dist = None`. No falla porque `min_pos is None` corta la condición en la primera vuelta, pero es un descuido. Las anotaciones dicen que devuelven `pygame.Vector2`, aunque devuelven una tupla.

**Lecturas opcionales (S7.6):**
- *Juego emergente:* "Types and Forms of Emergence" (Fromm, arXiv nlin/0506028); "Exploring the Tech and Design of Noita" (emergencia con píxeles simples); "Contando historias con sistemas"; "How Game Designers Create Systemic Games" y "The rise of the systemic games" (juego sistémico: la interacción de sistemas supera la suma de partes).
- *Steering:* serie "Understanding Steering Behaviors" (Tuts+ gamedevelopment, más comportamientos que los de clase); charla GDC "The Next Vector: Improvements in AI Steering Behaviors" (casos especiales y problemas).
- *Perfilado:* GDC "Automated Testing and Profiling for Call of Duty"; GDC "Borderlands: The Pre-Sequel on Android – AAA Porting".

**Conexión:** reutiliza `CTransform`/`CVelocity`/`system_movement` (semana 1), etiquetas y patrón Command (semana 2), `CSurface.area` (semana 3), Service Locator (semana 4) y escenas (semanas 5-6). Para el Hunter y Bosconian: la FSM decide el objetivo y un sistema de steering calcula la velocidad. Agregar separación entre enemigos sería trabajo propio, no está en el demo.

---

## Semana 8: cierre y entregas finales

### En palabras simples

La última semana no trae clases ni demostración. Es el cierre: se entrega el proyecto en grupo y se publican las notas con las bonificaciones. Además deja dos lecturas para después del curso, una sobre software liviano y otra con otros frameworks para hacer juegos.

### Ejemplo en tu juego

Cada bono vale un punto porcentual sobre la nota, y todo el grupo recibe el mismo. Varios bonos se apoyan en lo que vimos en las semanas 5 a 7: el menú separado y la pantalla de instrucciones son escenas, las vistas de depurado y el editor de niveles vienen de la semana 6, y el ataque dinámico de los enemigos puede salir de los steering behaviours de la semana 7.

### Notas técnicas

**Entregas finales (todas las califica el equipo docente):** juego publicado, enlace al código fuente, documento de análisis de arquitectura y post-mortem en grupo, documento post-mortem individual y presentación del proyecto.

**Bonificaciones** (lectura "Notas finales + bonificaciones"; está escrita en pasado, así que parece la de una cohorte anterior, pero muestra qué se premia):
- Ataque de enemigos dinámico, acercándose al jugador, como en el original.
- Varios niveles con avance marcado por íconos de banderas (cinco banderas al principio y luego el juego).
- Sistema de vidas: cuatro vidas y game over.
- Puntaje máximo (HIGH-SCORE) que se conserva durante la sesión de juego.
- Menú principal separado del nivel.
- Escena de instrucciones en el menú, además de la pantalla de título.
- Niveles con distribuciones de enemigos distintas a las del original.
- Vistas de depurado de los elementos pertinentes del juego.
- Editor de niveles: crear enemigos, moverlos, eliminarlos y guardar el nivel. En la sesión síncrona del 4 nov dijeron que este bono cuenta doble.
- Arma adicional del jugador con un comportamiento especial.
- Un efecto visual extra sobre el juego.
- Intro personalizado si la versión es web.

Reglas: cada ítem suma un punto porcentual directamente a la nota acumulada. El bono es igual para todos los miembros del grupo. Si la nota final pasa de 100 % se aproxima a 100; si no, queda sin redondeo.

**Lecturas finales:** Niklaus Wirth, *A Plea for Lean Software* (descargado en `curso_semanas_5_7/S8/`). Otros PDF de lecturas opcionales descargados: *Pitfalls of Object Oriented Programming* en `S6/` y *Types and forms of emergence* en `S7/`. "Otros frameworks para juegos": SDL, Allegro, SFML, Raylib, Kha/Kore, ORX, PixiJS, Pygame-ce, Pyglet, MonoGame, FNA, Ebitengine, Bevy, LÖVE 2D, HaxeFlixel, Kaplay.js, Excalibur.js y Phaser. Algunos traen ECS incluido; otros solo dibujan y el patrón lo pone uno.

---

## El hilo que une todo

Cada semana se construyó sobre la anterior con la misma receta. Cuando quieres algo nuevo:
1. **Ficha nueva:** creas un componente con los datos que necesitas.
2. **Trabajador nuevo:** creas un sistema que actúa sobre esos datos.
3. **Ensamblaje:** en el prefab, juntas las fichas para armar la entidad.
4. **Valores afuera:** pones los números en un JSON y no en el código.

Tu escudo de energía es la prueba de que ya dominas esa receta. Es una ficha (`CShield`), dos trabajadores (uno que lo controla y otro que dibuja la barra) y un archivo de configuración. No tuviste que tocar el resto del juego para que funcionara.

La velocidad es casi siempre lo mismo: **dirección normalizada × rapidez del JSON**, y luego **posición += velocidad × delta_time**. Si entiendes esas dos líneas, entiendes cómo se mueve todo en tu juego.

## Tabla de nombres

| Nombre | Qué es |
|---|---|
| `ecs_world` / `world` | El mundo de esper: la bodega de todas las entidades y sus fichas |
| `delta_time` | Segundos que duró la última vuelta del ciclo (~0,016) |
| `pos` | Posición de la esquina superior izquierda, en píxeles |
| `vel` | Velocidad en píxeles por segundo (x, y) |
| `c_t`, `c_v`, `c_s`, `c_a` | Fichas de transform, velocity, surface y animation |
| `c_pst`, `c_hst`, `c_sh` | Fichas de estado del jugador, estado del Hunter y escudo |
| `vel_mag` | Rapidez sin dirección |
| `direction` | Flecha hacia donde se quiere ir |
| `normalize()` | Deja la flecha de largo 1 (solo dirección) |
| `input_velocity` | Cuánto suma o resta cada tecla a la velocidad del jugador (100) |
| `surf` / `area` | Imagen completa / pedazo que se dibuja |
| `curr_frame`, `curr_anim`, `curr_anim_time` | Dibujo actual, animación actual, cronómetro del cuadro |
| `_player_entity`, `_player_c_v`, `_player_c_t`, `_player_c_s` | El jugador y sus fichas, guardados en el motor |
| `*_cfg` / `*_info` | Diccionarios leídos de los JSON (`player_cfg`, `enemy_info`, etc.) |

---

## Proyecto final (resumen)

Proyecto en grupo: reproducción **exacta** de *Bosconian* (Sharp X68000, 1988) con ECS, en el repo privado del grupo. El detalle completo (requisitos, medidas del original, plan por fases) está en `VideoJuegos/proyecto_final/` (`lineamientos_bosconian.md` y `PLAN_FASES.md`).
