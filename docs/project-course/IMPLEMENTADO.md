# COSMONIAN: lo implementado

Estado del repositorio `dso-uniandes/bosconian` al 17 de noviembre de 2026. Todo lo de esta lista está en `main`, después de mezclar:

- **PR 10 a 13**: bases de cada ronda, ajustes de la auditoría de ECS, escenas del curso con `session_service` y pausa por comando.
- **PR 22**: la rama de Jerson con escenas y sonidos.
- **PR 14 a 21**: la etapa 2 del frente B (choques, cañones, núcleo, misil E y trampa 7), mezclados en orden.
- **PR 23**: los ajustes de ECS sobre las escenas de Jerson y los arreglos de la revisión de cada PR con la skill.
- **PR 24 a 28**: la etapa 3 del frente B (explosión letal de la mina, rocas indestructibles, editor de niveles con guardado y la música de los niveles), mezclados en orden.
- **PR 29**: alertas, puntaje, vidas extra y panel del frente C.
- **PR 30**: el panel con etiquetas y componentes, los textos centrados otra vez al centro, HI-SCORE visible, el panel del título y los sonidos de alerta desde `alerts.json`, con la sirena RED que se repite.
- **PR 31**: el editor arma sus piezas arrastrables en los prefabs y oculta el BLAST OFF, el cañón destruido se resuelve con un evento y los choques que solo cambiaban una etiqueta quedan en un sistema.
- **PR 32**: los sonidos de explosiones, cañones, núcleo, misil E y base destruida, cada uno desde el JSON de su entidad.
- **PR 33**: las vistas de depurado de hitboxes y velocidades con Mayús + 1.

Cada punto dice en qué PR entró.

El plan completo está en [PLAN_DE_TRABAJO.md](PLAN_DE_TRABAJO.md).

## Requisitos de la rúbrica

| Requisito | Lo implementado | Dónde | Lo que sigue |
|---|---|---|---|
| Intro, 10 niveles con ronda en el panel, instrucciones y créditos | Los diez niveles en `levels/level_01.json` a `level_10.json`, generados con `tools/gen_levels.py`. Escenas de instrucciones y créditos | Niveles en main; escenas en PR 22 y PR 23 | Número de ronda en el panel e intro animada |
| Estrellas con color, parpadeo y movimiento | Estrellas de colores que parpadean de 0 a 255 y se mueven con parallax de 0,5 en el juego. Estrellas que caen en el título | Juego en main; título en PR 22 | |
| Escenas de juego, victoria y derrota | Una sola escena de juego para las diez rondas. Al caer la última base, `system_round_clear` espera `round_clear.delay` de `interface.json`, sube la ronda en la sesión y pasa a la siguiente. Al perder la última vida pasa a game over con continuar, y al terminar la ronda 10 pasa a la victoria, que muestra continuaciones y naves perdidas | PR 23 | |
| Cámara del jugador y parallax | La cámara sigue a la nave a través de los bordes del mundo y las estrellas se mueven a la mitad | main | |
| Minimapa | Minimapa de 64 x 96 a escala 1:16, con el jugador blanco que parpadea y cada base como un punto verde de 2 x 2 | main | |
| Wraparound | Mundo de 1024 x 1536 que da la vuelta en ambos ejes, con `wrapped_delta` para la distancia más corta | main | |
| Jugador | Aceleración en 8 direcciones con giro instantáneo, disparo en pares, muerte con varias explosiones, congelamiento de 2,5 s y reaparición | main | |
| Habilidad especial por nivel | EXTRA CANNON en las rondas 3, 6, 9 y 10, con cuatro balas por disparo, y la trampa 4 para activarlo | main | Anuncio "EXTRA CANNON" al inicio de la ronda |
| Bases | Bases H y V, cada una con cuerpo, seis cañones y núcleo como entidades separadas, con hitbox y etiqueta. Cada cañón destruido vale 200 y queda con su sprite de destruido; la base completa vale 1500 (1700 con el sexto cañón), con `CEventBaseDestroyed` y `system_base_destroyed`; ese evento también pone la condición en GREEN. Los cañones de una base a 144 px o menos disparan hacia el jugador dentro de su abanico, con la espera y la recarga de la ronda. `system_cannon_frames` muestra sus cuadros de apertura. Desde la ronda 5 el núcleo se cierra y se abre con `CCoreState`, resiste cerrado (la bala desaparece), cae con una bala por cualquier lado libre estando abierto y, con el núcleo en pantalla, lanza el misil E por su abertura hacia el lado del jugador | Choques en PR 17, disparo en PR 18, núcleo y misil en PR 19 y 21, cuadros del cañón en PR 23, alerta en PR 29 | |
| Enemigos I, P y E | Aparición por los bordes con dos relojes. Cada tipo trae en `enemies.json` su velocidad, cuánto persigue y a qué estado pasa: I persigue y se aleja, P persigue y vaga, E espera 0,4 s y va recto por el eje del núcleo. Explosión que conserva la velocidad al morir. Mueren con la bala del jugador, con el jugador, con rocas, minas y balas de cañón; I y P rebotan entre sí y contra las bases (`CTagBounces`) con `CEventBounce` y `system_bounce`; el misil E atraviesa bases y enemigos | Choques en PR 15, misil E en PR 19 y 21; la explosión con velocidad se arma con `create_moving_explosion` (PR 23) | |
| Obstáculos | Rocas de tres formas y minas con luces animadas, con sus puntos en `CPoints`. Las destruyen la bala del jugador, el jugador al chocar y la bala de cañón; el choque crea un evento de obstáculo destruido y `system_obstacle_destroyed` deja la explosión y los puntos. La mina deja una explosión verde con área letal de 24 x 24 (`CLethalBlast`, datos en `obstacles.json`) que mata al jugador y a los enemigos. Las rocas indestructibles, grises, van a 30 px/s en una dirección al azar, de 2 a 6 por ronda; se tragan las balas, matan al jugador y a los enemigos y rebotan en las bases | Choques en PR 14 y 18; evento en PR 23; mina en PR 24; rocas indestructibles en PR 25 | |
| Colisiones con hitbox | Componente `CHitbox` en todas las entidades que chocan. Una consulta común, `colliding_pairs` en `src/ecs/queries`, arma los rectángulos con `wrapped_delta` y cada par tiene su sistema: bala y jugador contra obstáculo, enemigo y base; enemigo contra enemigo, peligro y base; bala de cañón contra obstáculo. Los choques crean eventos (enemigo muerto, obstáculo destruido, rebote) que atiende un sistema para cada uno | Sistemas en PR 14 a 19; eventos en PR 23; mina y rocas indestructibles en PR 24 y 25 | Ítem |
| Puntaje, récord y vidas | `system_score` suma los puntos a la sesión y sube el récord, que arranca en 20.000. `system_lives` resta una vida en cada muerte y cuenta las naves perdidas. `system_score` también da las vidas extra de `scoring.json`. El panel muestra récord, puntaje, condición, vidas y ronda | main; vidas en PR 23; vidas extra y panel en PR 29 | |
| Alertas | `CAlert` con su máquina de estados en `system_alerts`: GREEN al empezar y al reaparecer, YELLOW por tiempo, RED al acabarse la espera de la ronda, con parpadeo y alarma repetida, y GREEN por 3,2 s al destruir una base. La trampa 6 cambia la alerta | main; máquina de estados en PR 29 | Formación y espía |
| Sonidos y música | Servicio de sonidos, `sounds.json`, 22 efectos en OGG y música por ronda, que arranca al terminar el BLAST OFF. Suenan las alertas, la vida extra, los menús, las explosiones (el prefab toca el sonido de `explosion.json`), la apertura y el disparo de los cañones, el golpe en el núcleo cerrado, el misil E y la base destruida | PR 22 y PR 23; efectos del frente B en PR 32 | Disparo del jugador y del EXTRA CANNON, espía y formación |

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
| Escenas | Intro, título, opciones, instrucciones, créditos, cutscene, juego, game over y victoria, con la forma de la semana 5: cada escena tiene su mundo y sus ganchos `do_create`, `do_update`, `do_action`, `do_draw` y `do_clean`, pide el cambio con `switch_scene` y el motor lo hace al final del cuadro. Una sola clase `GameScene` sirve para las diez rondas; los sistemas que cambian de escena reciben la escena | main; escenas de Jerson en PR 22 y una sola escena de juego en PR 23 |
| Configuración | Un JSON por tipo de entidad y uno por ronda, sin valores del juego en el código, sin comentarios ni docstrings | main |
| Orden de dibujo | Capas del mundo en `window.json`, con el cuerpo de la base debajo de sus cañones y su núcleo | main |
| Modo trampa | La tecla 0 lo activa y el panel muestra "CHEAT". La acción 4 activa el EXTRA CANNON, la 6 cambia la alerta, la 7 destruye todas las bases, la 8 va a la victoria y la 9 al game over. Cada trampa tiene su nombre en `cheats.json` y el comando lo anota en `CCheatMode` | main; la 7 en PR 20; la 8, la 9 y los nombres en PR 23 |
| Pausa | ESC o P pausan y reanudan la partida con una sola bandera de la escena de juego. En pausa se ocultan el jugador, los enemigos y el minimapa, las estrellas quedan quietas brillando, aparece "JUEGO PAUSADO" con su menú y se pueden abrir las opciones. El texto y el menú se crean una vez y `system_pause_visibility`, desde `do_update`, los muestra u oculta con `CVisible`; también oculta el "BLAST OFF!!" (`CTagHiddenInPause`) si se pausa durante la cuenta | PR 23 |
| Vistas de depurado | Con trampa activa, Mayús + 1 rota entre la vista normal, la de hitboxes (`system_rendering_debug_rects`) y la de velocidades (`system_rendering_debug_velocity`), con los colores y la escala en `debug.json` | PR 33 |
| Medición | Ronda 10 en alerta roja durante 30 s con cProfile: 1,58 ms por cuadro con el perfilador encendido, de los 16,7 ms que tiene un cuadro a 60 FPS. Las colisiones son el 58 % de la simulación (0,9 ms). Con eso la cuadrícula de colisiones queda fuera | Medición sobre el PR 19 |
| Documentación | `README.md` con instrucciones, controles, modo trampa y estructura | main |
| Sonidos | `sounds_service` y `sounds.json` | PR 22 |
| Editor de niveles | Mayús + 9 con trampa activa abre el editor en la escena de juego, como en la semana 6: cámara libre, rejilla, el clic pone o arrastra rocas, minas, bases y el inicio de la nave, y el clic derecho borra. R cambia la ronda, M la música, X el EXTRA CANNON y S guarda el nivel con el formato de los niveles en `editor_level.json` o en el navegador. La entrada EDITOR de opciones lo abre | PR 26 y 27; músicas desde `sounds.json` en PR 28 |
| Interfaz con ECS | Las pantallas se arman con prefabs y el texto que cambia usa `CChangingText`, que dibuja un solo sistema. Título, pausa y opciones comparten un `CMenu` cuyas entradas se describen en `interface.json`; el selector de dispositivo guarda sus textos en `CInputSelector` y la música del título se reintenta con `system_music_retry`; instrucciones y créditos muestran sus páginas con la misma navegación. Una sola salida de escena con `CEventSceneExit`, y game over con los eventos de continuar y de fin del tiempo | PR 23 |

## Bonos

Los diez bonos de la sección 1.3 del plan se construyen después de los requisitos obligatorios. La cutscene al empezar y las escenas de victoria y game over ya están en `main` desde el PR 22.
