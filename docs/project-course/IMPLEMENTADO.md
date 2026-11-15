# COSMONIAN: lo implementado

Estado del repositorio `dso-uniandes/bosconian` al 14 de noviembre de 2026, después de mezclar los PR 10 (bases de cada ronda), 11 (ajustes de la auditoría de ECS y configuración) y 12 (escenas del curso, `session_service` y pausa por comando). Cada punto dice dónde está el código:

- **main**: ya mezclado en la rama principal.
- **Pila del frente B**: los PR 14, 15, 17, 18, 19, 20, 21 y 23, cada uno sobre el anterior, con la etapa 2 del frente B. El PR 23 trae la rama de Jerson y los ajustes de ECS de la revisión del proyecto. Se mezclan en orden.
- **Rama de Jerson**: `jflorez` (PR 22), con escenas y sonidos; ya está dentro del PR 23.

El plan completo está en [PLAN_DE_TRABAJO.md](PLAN_DE_TRABAJO.md).

## Requisitos de la rúbrica

| Requisito | Lo implementado | Dónde | Lo que sigue |
|---|---|---|---|
| Intro, 10 niveles con ronda en el panel, instrucciones y créditos | Los diez niveles en `levels/level_01.json` a `level_10.json`, generados con `tools/gen_levels.py`. Escenas de instrucciones y créditos | Niveles en main; escenas en la rama de Jerson | Número de ronda en el panel e intro animada |
| Estrellas con color, parpadeo y movimiento | Estrellas de colores que parpadean de 0 a 255 y se mueven con parallax de 0,5 en el juego. Estrellas que caen en el título | Juego en main; título en la rama de Jerson | Integrar la rama de Jerson |
| Escenas de juego, victoria y derrota | Una sola escena de juego para las diez rondas. Al perder la última vida pasa a game over con continuar, y al terminar la ronda 10 pasa a la victoria, que muestra continuaciones y naves perdidas | Juego en main; victoria, game over y los cambios de escena en PR 23 | |
| Cámara del jugador y parallax | La cámara sigue a la nave a través de los bordes del mundo y las estrellas se mueven a la mitad | main | |
| Minimapa | Minimapa de 64 x 96 a escala 1:16, con el jugador blanco que parpadea y cada base como un punto verde de 2 x 2 | main | |
| Wraparound | Mundo de 1024 x 1536 que da la vuelta en ambos ejes, con `wrapped_delta` para la distancia más corta | main | |
| Jugador | Aceleración en 8 direcciones con giro instantáneo, disparo en pares, muerte con varias explosiones, congelamiento de 2,5 s y reaparición | main | Vidas |
| Habilidad especial por nivel | EXTRA CANNON en las rondas 3, 6, 9 y 10, con cuatro balas por disparo, y la trampa 4 para activarlo | main | Anuncio "EXTRA CANNON" al inicio de la ronda |
| Bases | Bases H y V, cada una con cuerpo, seis cañones y núcleo como entidades separadas, con hitbox y etiqueta. Cada cañón destruido vale 200 y queda con su sprite de destruido; el núcleo se acierta solo por su eje y la base completa vale 1500 (1700 con el sexto cañón), con `CEventBaseDestroyed` y `system_base_destroyed`. Los cañones de una base a 144 px o menos disparan hacia el jugador dentro de su abanico, con la espera y la recarga de la ronda y sus cuadros de apertura. Desde la ronda 5 el núcleo se cierra y se abre con `CCoreState`, resiste cerrado (la bala desaparece), cae con una bala por cualquier lado libre estando abierto y, con el núcleo en pantalla, lanza el misil E por su abertura hacia el lado del jugador | main; choques en PR 17, disparo en PR 18, núcleo y misil en PR 19 y 21 | Cambio de alerta al destruir una base y cambio de ronda |
| Enemigos I, P y E | Aparición por los bordes con dos relojes. Cada tipo trae en `enemies.json` su velocidad, cuánto persigue y a qué estado pasa: I persigue y se aleja, P persigue y vaga, E espera 0,4 s y va recto por el eje del núcleo. Explosión que conserva la velocidad al morir. Mueren con la bala del jugador, con el jugador, con rocas, minas y balas de cañón; I y P rebotan entre sí y contra las bases (`CTagBounces`); el misil E atraviesa bases y enemigos | main; choques en PR 15, misil E en PR 19 y 21 | |
| Obstáculos | Rocas de tres formas y minas con luces animadas, con sus puntos en `CPoints`. Las destruyen la bala del jugador, el jugador al chocar y la bala de cañón, con `destroy_obstacle` | main; choques en PR 14 y 18 | Explosión letal de la mina y rocas indestructibles |
| Colisiones con hitbox | Componente `CHitbox` en todas las entidades que chocan. Una consulta común, `colliding_pairs` en `src/ecs/queries`, arma los rectángulos con `wrapped_delta` y cada par tiene su sistema: bala y jugador contra obstáculo, enemigo y base; enemigo contra enemigo, peligro y base; bala de cañón contra obstáculo. Los choques crean eventos (enemigo muerto, obstáculo destruido, rebote) que atiende un sistema para cada uno | main; sistemas en PR 14 a 19; eventos en PR 23 | Rocas indestructibles, explosión de mina e ítem |
| Puntaje, récord y vidas | `system_score` suma los puntos a la sesión y sube el récord, que arranca en 20.000. `system_lives` resta una vida en cada muerte y cuenta las naves perdidas. `scoring.json` con las vidas extra | main; vidas en PR 23 | Panel con puntaje y vidas extra |
| Alertas | Componente `CAlert`, alerta inicial desde `alerts.json` y cambio de alerta con el modo trampa | main | Cambio por tiempo y por eventos |
| Sonidos y música | Servicio de sonidos, `sounds.json`, 22 efectos en OGG y música por ronda, que arranca al terminar el BLAST OFF | PR 23 | Conectar los efectos a cada evento del juego |

## Motor y patrones del curso

| Pieza | Lo implementado | Dónde |
|---|---|---|
| Game loop | Loop asíncrono con delta time, con su tope en `window.json` (`min_framerate`), listo para pygbag | main |
| Motor | Administra la ventana, el reloj, el dibujo final y las escenas en un diccionario por nombre. Las configuraciones del juego las pide cada escena a `configs_service` | main |
| Pantalla | Lienzo de 256 x 208 escalado a mano a 768 x 624, con área de juego de 192 x 208 | main |
| ECS | Componentes con solo datos, etiquetas en `tags/`, prefabs `create_*` y sistemas `system_*` que tratan igual a todas las entidades, sin preguntar el tipo | main |
| Command | Teclas como `CInputCommand` con nombre, tecla y fase, creadas siempre con `create_key_command`. Las teclas vienen de `input.json` (siempre como lista `keys`) y `cheats.json`. Los comandos del jugador y del modo trampa hacen su trabajo en `execute`, y la escena atiende START y PAUSE en `do_action` | main |
| State | `CPlayerState` y `CEnemyState` con su sistema | main |
| Service Locator | Servicios de configuraciones, imágenes y fuentes. `session_service` con la ronda, el puntaje, el récord, las vidas y las continuaciones, que guarda y carga el récord en `hi_score.json` o en el almacenamiento local del navegador | main |
| Escenas | Intro, título, opciones, instrucciones, créditos, cutscene, juego, game over y victoria, con la forma de la semana 5: cada escena tiene su mundo y sus ganchos `do_create`, `do_update`, `do_action`, `do_draw` y `do_clean`, pide el cambio con `switch_scene` y el motor lo hace al final del cuadro. Una sola clase `GameScene` sirve para las diez rondas; los sistemas que cambian de escena reciben la escena | main; escenas de Jerson y una sola escena de juego en PR 23 |
| Configuración | Un JSON por tipo de entidad y uno por ronda, sin valores del juego en el código, sin comentarios ni docstrings | main |
| Orden de dibujo | Capas del mundo en `window.json`, con el cuerpo de la base debajo de sus cañones y su núcleo | main |
| Modo trampa | La tecla 0 lo activa y el panel muestra "CHEAT". La acción 4 activa el EXTRA CANNON, la 6 cambia la alerta, la 7 destruye todas las bases, la 8 va a la victoria y la 9 al game over. Cada trampa tiene su nombre en `cheats.json` y el comando lo anota en `CCheatMode` | main; la 7 en PR 20; la 8, la 9 y los nombres en PR 23 |
| Pausa | ESC o P pausan y reanudan la partida con una sola bandera de la escena de juego. En pausa se ocultan el jugador, los enemigos y el minimapa, las estrellas quedan quietas brillando, aparece "JUEGO PAUSADO" con su menú y se pueden abrir las opciones. El texto y el menú se crean una vez y un sistema los muestra u oculta | PR 23 |
| Medición | Ronda 10 en alerta roja durante 30 s con cProfile: 1,58 ms por cuadro con el perfilador encendido, de los 16,7 ms que tiene un cuadro a 60 FPS. Las colisiones son el 58 % de la simulación (0,9 ms). Con eso la cuadrícula de colisiones queda fuera; se vuelve a medir en la versión web | Medición sobre la pila del PR 19 |
| Documentación | `README.md` con instrucciones, controles, modo trampa y estructura | main |
| Sonidos | `sounds_service` y `sounds.json` | PR 23 |

## Bonos

Los diez bonos de la sección 1.3 del plan se construyen después de los requisitos obligatorios. La rama de Jerson trae la cutscene al empezar y un commit que suma escenas de victoria, game over y bonos.
