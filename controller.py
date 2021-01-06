



import glfw
import sys

class Controller(object):

    def __init__(self):
        self.pandemic = None
        # self.direction =

    def set_model(self, m):
        self.pandemic = m

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return

        # print("current key: ",key)
        # print("current action: ", action)
        if key == glfw.KEY_ESCAPE:
            glfw.terminate()
            sys.exit()

        # Controlador modifica al modelo
        elif action == glfw.RELEASE:
            # print('Move left')
            # self.model.move_left()
            # print("nothing")
            # print(key)
            return

        elif key == glfw.KEY_RIGHT and action == glfw.PRESS:
            # print('Move rigth')
            # self.model.move_left()
            self.pandemic.next_day()

        elif key == glfw.KEY_P and action == glfw.PRESS:
            # print('Move rigth')
            # self.model.move_left()
            self.pandemic.show_plots()


        # elif key == glfw.KEY_LEFT and action == glfw.PRESS:
        #     print('Move left')
        #     # self.model.move_left()
        #     self.pandemic.next_day()

        # elif key == glfw.KEY_W and action == glfw.PRESS:
        #     # print("UP")
        #     self.snake.turn_up()
        #
        # elif key == glfw.KEY_S and action == glfw.PRESS:
        #     # print("DOWN")
        #     self.snake.turn_down()
        #
        # elif key == glfw.KEY_A and action == glfw.PRESS:
        #     # print('Move left')
        #     # self.model.move_left()
        #     # print("left")
        #     self.snake.turn_left()
        #
        # elif key == glfw.KEY_D and action == glfw.PRESS:
        #     # print('Move left')
        #     # self.model.move_right()
        #     # print("right")
        #     self.snake.turn_right()

        # elif key == glfw.KEY_SPACE and action == glfw.PRESS:
        #     # print('Move left')
        #     # self.model.move_right()
        #     print("eat")
        #     self.epidemic.extend()
        # elif (key == glfw.KEY_LEFT or key == glfw.KEY_RIGHT) and action == glfw.RELEASE:
        #     self.model.move_center()

        # Raton toca la pantalla....
        else:
            print('Unknown key')
