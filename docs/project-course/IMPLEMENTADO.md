# COSMONIAN: lo implementado

Estado del repositorio `dso-uniandes/bosconian` al 14 de noviembre de 2026, después de mezclar los PR 10 (bases de cada ronda) y 11 (ajustes de la auditoría de ECS y configuración). Cada punto dice dónde está el código:

- **main**: ya mezclado en la rama principal.
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
| Bases | Bases H y V, cada una con cuerpo, seis cañones y núcleo como entidades separadas, con hitbox y etiqueta | main | Disparo de los cañones, núcleo animado y misil E |
| Enemigos I, P y E | Aparición por los bordes con dos relojes. Cada tipo trae en `enemies.json` su velocidad, cuánto persigue y a qué estado pasa: I persigue y se aleja, P persigue y vaga, E va recto. Explosión que conserva la velocidad al morir | main | Misil E desde el núcleo |
| Obstáculos | Rocas de tres formas y minas con luces animadas | main | Explosión letal de la mina y rocas indestructibles |
| Colisiones con hitbox | Componente `CHitbox` en el jugador, las balas, los enemigos, los obstáculos, los cañones y el núcleo | main | Un sistema de colisión por par, con `wrapped_delta` |
| Puntaje, récord y vidas | `system_score` suma los puntos a la sesión y sube el récord, que arranca en 20.000. `scoring.json` con las vidas extra | main | Panel con puntaje y vidas extra |
| Alertas | Componente `CAlert`, alerta inicial desde `alerts.json` y cambio de alerta con el modo trampa | main | Cambio por tiempo y por eventos |
| Sonidos y música | Servicio de sonidos, `sounds.json`, 22 efectos en OGG y música por ronda | Rama de Jerson | Integrar la rama de Jerson |

## Motor y patrones del curso

| Pieza | Lo implementado | Dónde |
|---|---|---|
| Game loop | Loop asíncrono con delta time, con su tope en `window.json` (`min_framerate`), listo para pygbag | main |
| Pantalla | Lienzo de 256 x 208 escalado a mano a 768 x 624, con área de juego de 192 x 208 | main |
| ECS | Componentes con solo datos, etiquetas en `tags/`, prefabs `create_*` y sistemas `system_*` que tratan igual a todas las entidades, sin preguntar el tipo | main |
| Command | Teclas como `CInputCommand` con su comando. Las teclas vienen de `input.json` y `cheats.json`, y cada comando hace su trabajo en `execute` | main |
| State | `CPlayerState` y `CEnemyState` con su sistema | main |
| Service Locator | Servicios de configuraciones, imágenes y fuentes | main |
| Escenas | Título y juego, con cambio de escena al final del cuadro | main |
| Configuración | Un JSON por tipo de entidad y uno por ronda, sin valores del juego en el código, sin comentarios ni docstrings | main |
| Orden de dibujo | Capas del mundo en `window.json`, con el cuerpo de la base debajo de sus cañones y su núcleo | main |
| Modo trampa | La tecla 0 lo activa y el panel muestra "CHEAT". La acción 4 activa el EXTRA CANNON y la 6 cambia la alerta | main |
| Pausa | Escena de pausa | Rama de Jerson |
| Pruebas | 50 pruebas sin ventana de `world_math`, el spawner y la máquina de estados de los enemigos | main |
| Documentación | `README.md` con instrucciones, controles, modo trampa, pruebas y estructura | main |

## Bonos

Los diez bonos de la sección 1.3 del plan se construyen después de los requisitos obligatorios. La rama de Jerson trae la cutscene al empezar y un commit que suma escenas de victoria, game over y bonos.
