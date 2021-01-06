# coding=utf-8
"""
Luis Cossio, CC3501, 2019-2

"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import easy_shaders2 as es2
import controller as cr
# import models as md
import pandemic_manager as pm
import text_renderer as tx

if __name__ == "__main__":
    """
    View program
    """
    # Initialize glfw
    if not glfw.init():
        sys.exit()
    width = 600
    height = 600

    controller = cr.Controller()
    window = glfw.create_window(width, height, "Snake World", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

    # A simple shader program with position and texture coordinates as inputs.
    pipeline = es.SimpleTextureTransformShaderProgram()

    pipeline_objects = es.SimpleTransformShaderProgram()

    textPipeline = tx.TextureTextRendererShaderProgram()

    # Enabling transparencies
    # glEnable(GL_BLEND)
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating texture with all characters
    textBitsTexture = tx.generateTextBitsTexture()

    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)
    # # Telling OpenGL to use our shader program
    # glUseProgram(pipeline.shaderProgram)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    dim_x = 15

    dim_y = dim_x
    steps = 60
    pandemic = pm.pandemic_manager(steps = steps)


    # snake = md.snake_model(dim_x)
    # rat = md.target(dim_x)

    controller.set_model(pandemic)
    # controller.set_target(rat)


    # Creating shapes on GPU memory
    # gpuFloor = es.toGPUShapePattern(bs.createTextureQuad(["figures/grass3.png", "figures/grass4.png"]), dim_x, dim_y,
    #                                 GL_REPEAT,
    #                                 GL_NEAREST)  # GL_NEAREST is about a metric to wich pixel color use.
    gpuFloor = es.toGPUShape(bs.createTextureQuad("figures/city.png",1,1), GL_REPEAT, GL_NEAREST)
    # gpuFloor = es.toGPUShape(bs.createTextureQuad("figures/city2.png",1,1), GL_REPEAT, GL_NEAREST)
    # GL_NEAREST is about a metric to wich pixel color use.
    # In this case the nearest to the element en the gpuhape.
    # floorTransform = np.matmul(tr.translate(0, 0, 0), tr.scale(2, 1, 1))

    # game over text
    headerText = "Game over"
    headerCharSize = 0.1
    headerCenterX = headerCharSize * len(headerText) / 2
    headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
    gpuGameOver = es2.toGPUShape(headerShape, GL_STATIC_DRAW, gpuText3DTexture)
    translation_text = tr.translate(-headerCenterX, 0, 0)
    headerTransform = tr.matmul([
        # tr.translate(0.0, 0, 0),
        translation_text,
    ])

    floorTransform = tr.scale(1.9, 1.9, 1)
    t0 = 0
    time_step = 4.5/steps*1
    dead = False
    # sign = 1
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        ti = glfw.get_time()
        dt = ti - t0

        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(pipeline.shaderProgram)

        # Drawing the shapes
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, floorTransform)
        pipeline.drawShape(gpuFloor)

        # snake.draw(pipeline)
        glUseProgram(pipeline_objects.shaderProgram)
        # rat.draw(pipeline_objects)
        # snake.rat_eaten(rat)

        # if dead:
        #     glUseProgram(textPipeline.shaderProgram)
        #
        #     glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0, 0, 0, 1)
        #     glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1, 1, 1, 0)
        #     glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE,
        #                        headerTransform)
        #     # es.updateGPUShape(gpuGameOver, headerShape, GL_DYNAMIC_DRAW)
        #     textPipeline.drawShape(gpuGameOver)
        #
        #     # if dt > 1:
        #     #     sign *= -1
        #     #     t0 = ti
        #     d_rot_z = np.cos(5 * dt)
        #
        #     headerTransform = tr.composes(tr.rotationZ(d_rot_z * np.pi / 8), translation_text)
        #     # if dt>3:
        #
        # elif snake.just_moved():
        #     t0 = ti
        #
        # elif dt > time_step:
        #     t0 = ti
        #     if snake.dead:
        #         dead = True
        #     else:
        #         snake.forward()
        if dt > time_step:
            t0 = ti
            pandemic.next_action(pipeline_objects)
        else:
            pandemic.draw(pipeline_objects)
            # pandemic.report()

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()