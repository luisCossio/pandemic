# coding=utf-8
"""
Daniel Calderon, CC3501, 2020-1
Simple Text Renderer using OpenGL Textures
Font: IBM text mode 8x8
"""

from OpenGL.GL import *
import OpenGL.GL.shaders
import font8x8_basic as f88
import numpy as np
import basic_shapes as bs
import easy_shaders as es
import easy_shaders2 as es2


def toBit(number, bit):
    return int((number & bit) != 0)


def generateTextBitsTexture():

    assert f88.font8x8_basic.shape == (128,8)

    bits = np.zeros(shape=(8,8,128), dtype=np.uint8)
    
    for k in range(128):
        for i in range(8):
            row = f88.font8x8_basic[k, i]
            bits[0, i, k] = toBit(row, 1)
            bits[1, i, k] = toBit(row, 2)
            bits[2, i, k] = toBit(row, 4)
            bits[3, i, k] = toBit(row, 8)
            bits[4, i, k] = toBit(row, 16)
            bits[5, i, k] = toBit(row, 32)
            bits[6, i, k] = toBit(row, 64)
            bits[7, i, k] = toBit(row, 128)

    return bits


def toOpenGLTexture(textBitsTexture):

    assert textBitsTexture.shape == (8, 8, 128)

    data = np.copy(textBitsTexture)
    data.reshape((8*8*128,1), order='C')

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_3D, texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glTexImage3D(GL_TEXTURE_3D, 0, GL_RED, 128, 8, 8, 0, GL_RED, GL_UNSIGNED_BYTE, data)

    return texture


def getCharacterShape(char):

    # Getting the unicode code of the character as int
    # Example: ord('a') = 97
    k = ord(char)

    # Vertices are created between 0 and 1 in (x,y,0)
    vertices = [
        # space, texture
        0, 0, 0, k, 8, 0, \
        1, 0, 0, k, 8, 8, \
        1, 1, 0, k, 0, 8, \
        0, 1, 0, k, 0, 0
    ]

    indices = [
        # Bottom right triangle
        0,1,2,\
        # Top left triangle
        2,3,0
    ]

    return bs.Shape(vertices, indices)


def textToShape(text, charWidth, charHeight):

    shape = bs.Shape([],[])

    for i in range(len(text)):
        char = text[i]
        charShape = getCharacterShape(char)
        bs.applyOffset(charShape, 6, [i, 0, 0])
        bs.scaleVertices(charShape, 6, [charWidth, charHeight, 1])
        bs.merge(shape, 6, charShape)

    return shape



class TextureTextRendererShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 transform;

            in vec3 position;
            in vec3 texCoords;

            out vec3 outTexCoords;

            void main()
            {
                gl_Position = transform * vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 130

            in vec3 outTexCoords;

            out vec4 outColor;

            uniform vec4 fontColor;
            uniform vec4 backColor;

            uniform sampler3D samplerTex;

            void main()
            {
                vec4 data = texelFetch(samplerTex, ivec3(outTexCoords.xyz), 0);
                if (data.r != 0)
                {
                    outColor = fontColor;
                }
                else
                {
                    outColor = backColor;
                }
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def drawShape(self, shape, mode=GL_TRIANGLES):
        assert isinstance(shape, es.GPUShape) or isinstance(shape, es2.GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)
        glBindTexture(GL_TEXTURE_3D, shape.texture)

        # 3d vertices + 2d texture coordinates => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)

