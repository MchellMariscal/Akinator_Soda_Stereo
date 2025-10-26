# Akinator_Soda_Stereo
# 🎸 Akinator: Soda Stereo (Adivina la Canción)

## 🎤 Descripción del Proyecto
Akinator: Soda Stereo es una implementación del popular juego Akinator, pero enfocado exclusivamente en la discografía de la banda argentina **Soda Stereo**.

El programa guía al usuario a través de una serie de preguntas de Sí/No para intentar adivinar una canción en la que el usuario está pensando. Si el juego no logra adivinar, el jugador tiene la opción de **enseñarle la nueva canción**, guardándola en la base de datos para futuras partidas, ¡permitiendo que el Akinator aprenda!

Este juego está desarrollado en Python utilizando la librería **Pygame** para la interfaz gráfica. Además, está adaptado para ser ejecutado en el navegador web usando **Pygame-ce** y **Emscripten** (vía PyGbag).

## 🌟 Características
* **Adivinación por Puntuación:** Utiliza un sistema de puntuación (`__score__`) basado en la respuesta a las preguntas (`Sí`, `No`, etc.) para clasificar y reducir las opciones de canciones candidatas.
* **Aprendizaje del Juego:** Si el juego pierde o no adivina con suficiente confianza, permite al usuario ingresar la canción y sus atributos para ampliar su base de datos.
* **Persistencia de Datos:** La base de datos de canciones y sus atributos se guarda en el archivo **`Juego/canciones.json`**.
* **Interfaz Gráfica:**
    * Ventana de 900x600.
    * Uso de colores temáticos (Dorado/Arena, Gris Oscuro).
    * Implementación de imágenes para el fondo y el personaje (Akinator/Gustavo Cerati) si están disponibles.
* **Compatibilidad Web:** El código ha sido parchado para funcionar tanto en el escritorio como en un navegador web (usando `pygbag` y Pygame-ce).

## ⚙️ Requisitos e Instalación

### 1. Requisitos para Escritorio (Pygame)
Para ejecutar este juego localmente, necesitas tener instalado **Python 3.x** y la librería **Pygame**:

```bash
pip install pygame