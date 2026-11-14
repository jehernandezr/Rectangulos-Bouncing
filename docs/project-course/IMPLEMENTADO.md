# COSMONIAN: lo implementado

Estado del repositorio `dso-uniandes/bosconian` al 14 de noviembre de 2026, después de mezclar los PR 10 (bases de cada ronda), 11 (ajustes de la auditoría de ECS y configuración) y 12 (escenas del curso, `session_service` y pausa por comando). Cada punto dice dónde está el código:

- **main**: ya mezclado en la rama principal.
- **Pila del frente B**: los PR 14, 15, 17, 18, 19, 20 y 21, cada uno sobre el anterior, con la etapa 2 del frente B. Se mezclan en orden.
- **Rama de Jerson**: `jflorez` y `backup/main-con-jerson`, con escenas y sonidos que vuelven a `main` en la integración.

El plan completo está en [PLAN_DE_TRABAJO.md](PLAN_DE_TRABAJO.md).

## Requisitos de la rúbrica

| Requisito | Lo implementado | Dónde | Lo que sigue |
|---|---|---|---|
| Intro, 10 niveles con ronda en el panel, instrucciones y créditos | Los diez niveles en `levels/level_01.json` a `level_10.json`, generados con `tools/gen_levels.py`. Escenas de instrucciones y créditos | Niveles en main; escenas en la rama de Jerson | Número de ronda en el panel e intro animada |
| Estrellas con color, parpadeo y movimiento | Estrellas de colores que parpadean de 0 a 255 y se mueven con parallax de 0,5 en el juego. Estrellas que caen en el título | Juego en main; título en la rama de Jerson | Integrar la rama de Jerson |
| Escenas de juego, victoria y derrota | Escena de juego con su mundo de Esper. Escenas de victoria y game over | Juego en main; victoria y game over en la rama de Jerson | Integrar la rama de Jerson |
| Cámara del jugador y parallax | La cámara sigue a la nave a través de los bordes del mundo y las estrellas se mueven a la mitad | main | |
| Minimapa | Minimapa de 64 x 96 a escala 1:16, con el jugador blanco que parpadea y cada base como un punto verde de 2 x 2 | main | |
| Wraparound | Mundo de 1024 x 1536 que da la vuelta en ambos ejes, con `wrapped_delta` para la distancia más corta | main | |
| Jugador | Aceleración en 8 direcciones con giro instantáneo, disparo en pares, muerte con varias explosiones, congelamiento de 2,5 s y reaparición | main | Vidas |
| Habilidad especial por nivel | EXTRA CANNON en las rondas 3, 6, 9 y 10, con cuatro balas por disparo, y la trampa 4 para activarlo | main | Anuncio "EXTRA CANNON" al inicio de la ronda |
| Bases | Bases H y V, cada una con cuerpo, seis cañones y núcleo como entidades separadas, con hitbox y etiqueta. Cada cañón destruido vale 200 y queda con su sprite de destruido; el núcleo se acierta solo por su eje y la base completa vale 1500 (1700 con el sexto cañón), con `CEventBaseDestroyed` y `system_base_destroyed`. Los cañones de una base a 144 px o menos disparan hacia el jugador dentro de su abanico, con la espera y la recarga de la ronda y sus cuadros de apertura. Desde la ronda 5 el núcleo se cierra y se abre con `CCoreState`, resiste cerrado (la bala explota) y lanza el misil E si está en pantalla | main; choques en PR 17, disparo en PR 18, núcleo y misil en PR 19 y 21 | Cambio de alerta al destruir una base y cambio de ronda |
| Enemigos I, P y E | Aparición por los bordes con dos relojes. Cada tipo trae en `enemies.json` su velocidad, cuánto persigue y a qué estado pasa: I persigue y se aleja, P persigue y vaga, E espera 0,4 s y va recto. Explosión que conserva la velocidad al morir. Mueren con la bala del jugador, con el jugador, con rocas, minas y balas de cañón; todos rebotan entre sí y contra las bases; el misil E no rebota contra la base que lo lanzó (`CLaunchBase`) | main; choques en PR 15, misil E en PR 19 y 21 | |
| Obstáculos | Rocas de tres formas y minas con luces animadas, con sus puntos en `CPoints`. Las destruyen la bala del jugador, el jugador al chocar y la bala de cañón, con `destroy_obstacle` | main; choques en PR 14 y 18 | Explosión letal de la mina y rocas indestructibles |
| Colisiones con hitbox | Componente `CHitbox` en todas las entidades que chocan. Una función común, `colliding_pairs`, arma los rectángulos con `wrapped_delta` y cada par tiene su sistema: bala y jugador contra obstáculo, enemigo y base; enemigo contra enemigo, peligro y base; bala de cañón contra obstáculo | main; sistemas en PR 14 a 19 | Rocas indestructibles, explosión de mina e ítem |
| Puntaje, récord y vidas | `system_score` suma los puntos a la sesión y sube el récord, que arranca en 20.000. `scoring.json` con las vidas extra | main | Panel con puntaje y vidas extra |
| Alertas | Componente `CAlert`, alerta inicial desde `alerts.json` y cambio de alerta con el modo trampa | main | Cambio por tiempo y por eventos |
| Sonidos y música | Servicio de sonidos, `sounds.json`, 22 efectos en OGG y música por ronda | Rama de Jerson | Integrar la rama de Jerson |

## Motor y patrones del curso

| Pieza | Lo implementado | Dónde |
|---|---|---|
| Game loop | Loop asíncrono con delta time, con su tope en `window.json` (`min_framerate`), listo para pygbag | main |
| Motor | Administra la ventana, el reloj, el dibujo final y las escenas en un diccionario por nombre. Las configuraciones del juego las pide cada escena a `configs_service` | main |
| Pantalla | Lienzo de 256 x 208 escalado a mano a 768 x 624, con área de juego de 192 x 208 | main |
| ECS | Componentes con solo datos, etiquetas en `tags/`, prefabs `create_*` y sistemas `system_*` que tratan igual a todas las entidades, sin preguntar el tipo | main |
| Command | Teclas como `CInputCommand` con nombre, tecla y fase. Las teclas vienen de `input.json` y `cheats.json`. Los comandos del jugador y del modo trampa hacen su trabajo en `execute`, y la escena atiende START y PAUSE en `do_action` | main |
| State | `CPlayerState` y `CEnemyState` con su sistema | main |
| Service Locator | Servicios de configuraciones, imágenes y fuentes. `session_service` con la ronda, el puntaje, el récord, las vidas y las continuaciones, que guarda y carga el récord en `hi_score.json` o en el almacenamiento local del navegador | main |
| Escenas | Título y juego con la forma de la semana 5: cada escena tiene su mundo y sus ganchos `do_create`, `do_update`, `do_action`, `do_draw` y `do_clean`, pide el cambio con `switch_scene` y el motor lo hace al final del cuadro. La escena de juego recibe la ruta de su nivel, y `scenes.json` lista el título y los diez niveles. El título arma sus textos como entidades | main |
| Configuración | Un JSON por tipo de entidad y uno por ronda, sin valores del juego en el código, sin comentarios ni docstrings | main |
| Orden de dibujo | Capas del mundo en `window.json`, con el cuerpo de la base debajo de sus cañones y su núcleo | main |
| Modo trampa | La tecla 0 lo activa y el panel muestra "CHEAT". La acción 4 activa el EXTRA CANNON, la 6 cambia la alerta y la 7 destruye todas las bases | main; la 7 en PR 20 |
| Pausa | ESC o P pausan y reanudan la partida con una bandera de la escena de juego; en pausa solo parpadean las estrellas | main. Ocultar entidades, texto "JUEGO PAUSADO" y menú de opciones: lo que sigue, con la escena de pausa de la rama de Jerson |
| Pruebas | 50 pruebas sin ventana de `world_math`, el spawner y la máquina de estados de los enemigos | main |
| Medición | Ronda 10 en alerta roja durante 30 s con cProfile: 1,58 ms por cuadro con el perfilador encendido, de los 16,7 ms que tiene un cuadro a 60 FPS. Las colisiones son el 58 % de la simulación (0,9 ms). Con eso la cuadrícula de colisiones queda fuera; se vuelve a medir en la versión web | Medición sobre la pila del PR 19 |
| Documentación | `README.md` con instrucciones, controles, modo trampa, pruebas y estructura | main |
| Sonidos | `sounds_service` y `sounds.json` | Rama de Jerson |

## Bonos

Los diez bonos de la sección 1.3 del plan se construyen después de los requisitos obligatorios. La rama de Jerson trae la cutscene al empezar y un commit que suma escenas de victoria, game over y bonos.
