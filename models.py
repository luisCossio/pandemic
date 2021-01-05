from typing import List, Any

import easy_shaders as es
import basic_shapes as bs  # bullshit
import transformations as tr
import scene_graph as sg

import random

from OpenGL.GL import *


class basic_model:
    rat_position: sg.SceneGraphNode

    def __init__(self):
        pass

    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')


class snake_model(basic_model):
    segments: List[sg.SceneGraphNode]

    def __init__(self, Size_field, Size=1):

        """ little big epidemic """
        # Figuras básicas
        delta_x = 1
        delta_y = 1
        scale = 1.9 / Size_field
        self.size_body = Size;
        self.delta_x = delta_x
        self.delta_y = delta_y
        # shape_body = bs.createTextureQuad("figures/snake_body3.png", 1, 1)
        # print(type(shape_body))
        gpu_body_quad = es.toGPUShape(bs.createTextureQuad("figures/snake_body4.png", 1, 1), GL_REPEAT,
                                      GL_NEAREST)  # body
        gpu_head_quad = es.toGPUShape(bs.createTextureQuad("figures/snake_head4.png", 1, 1), GL_REPEAT,
                                      GL_NEAREST)  # head
        gpu_tail_quad = es.toGPUShape(bs.createTextureQuad("figures/snake_tail4.png", 1, 1), GL_REPEAT,
                                      GL_NEAREST)  # tail

        self.gpu_body = gpu_body_quad

        # tail
        tail_segment_snake = sg.SceneGraphNode("tail_segment_snake")
        tail_segment_snake.transform = tr.rotationZ(-tr.pi / 2)
        tail_segment_snake.childs += [gpu_tail_quad]

        tail = sg.SceneGraphNode('tail')
        # tail.transform = tr.translate(0.0, -delta_y, 0.0)
        tail.transform = tr.translate(-delta_x, 0.0, 0.0)
        tail.childs += [tail_segment_snake]

        self.tail = tail
        # body
        body_segments = []
        body = sg.SceneGraphNode('body_' + str(Size - 1))
        # body.transform = tr.translate(0.0, -delta_y, 0.0)
        body.transform = tr.translate(-delta_x, 0.0, 0.0)

        segment_snake = sg.SceneGraphNode("segment_snake_" + str(Size - 1))

        segment_snake.transform = tr.rotationZ(-tr.pi / 2)
        segment_snake.childs += [gpu_body_quad]
        body.childs += [segment_snake, self.tail]

        body_segments.append(body)

        self.segments = body_segments
        for i in range(1, Size):
            # self.extend()

            body_segment = sg.SceneGraphNode('body_' + str(Size - i - 1))
            # body_segment.transform = tr.translate(0.0, -delta_y, 0.0)
            body_segment.transform = tr.translate(-delta_x, 0.0, 0.0)
            piece_snake = sg.SceneGraphNode("segment_snake_" + str(Size - i - 1))
            piece_snake.transform = tr.rotationZ(-tr.pi / 2)

            piece_snake.childs += [gpu_body_quad]
            body_segment.childs += [piece_snake, body_segments[-1]]
            self.segments.append(body_segment)

        # self.segments = body_segments
        # head
        starting_pos_x, starting_pos_y = self.get_starting_positions(Size_field)
        head = sg.SceneGraphNode('head')
        # head.transform = tr.composes(tr.translate(starting_pos_x, starting_pos_y, 0.0),tr.rotationZ(-tr.pi/2))
        head.transform = tr.translate(starting_pos_x, starting_pos_y, 0.0)

        segment_snake_head = sg.SceneGraphNode("segment_snake_head")
        segment_snake_head.transform = tr.rotationZ(-tr.pi / 2)
        segment_snake_head.childs += [gpu_head_quad]
        head.childs += [segment_snake_head, self.segments[-1]]

        snake = sg.SceneGraphNode('epidemic')
        snake.transform = tr.composes(tr.uniformScale(scale), tr.translate(0.0, 0.0, 0.0))
        snake.childs += [head]

        self.model = snake
        self.turns = []

        self.pos_x, self.pos_y = 1 + int(Size_field / 2 + 0.5), int(
            Size_field / 2 + 0.5)  # posicion de [1,..,Size_of_field]
        self.size_field = Size_field
        self.corners = [(self.pos_x - 1 - Size, self.pos_y)]

        self.direction_head = 0  # 0 = right,1 = up, 2 = left, 3 = down

        # steps = 10
        # self.step = delta_x/steps
        self.dead = False

        self.move_just_a_moment_before = False

    def get_starting_positions(self, Size_field):
        if Size_field % 2 == 0:
            return 0.5, 0.5
        else:
            return 1, 0

    def forward(self):
        """
        Method to move te epidemic forwards in the current direction of movement (head direction).

        :return: None
        """
        if self.dead:
            # print("you are dead")
            return
        self.move_just_a_moment_before = True
        self.update_position()
        # print(" positions: ",self.pos_x,", ",self.pos_y)
        if self.out_of_field():
            self.dead = True
            print("exit field.")
            self.die()
            return

        elif self.snake_bites_its_tail():
            self.dead = True
            print("bite its tail.")
            self.die()
            return

        delta_x, delta_y = self.get_current_direction()
        self.model.childs[0].transform = tr.composes(tr.translate(delta_x, delta_y, 0.0),
                                                     self.model.childs[0].transform)  # move head
        self.update_turns()

    def extend(self):
        """
        Method to add a segment between the tail and the end of the body of the epidemic

        :return: None
        """
        # print("extending ... ")
        body_segment = sg.SceneGraphNode('body_' + str(len(self.segments)))

        # body_segment.transform = tr.translate(0.0, -self.delta_y, 0.0)
        body_segment.transform = self.tail.transform

        piece_snake = sg.SceneGraphNode("segment_snake_" + str(len(self.segments)))
        piece_snake.transform = self.tail.childs[0].transform

        piece_snake.childs += [self.gpu_body]
        body_segment.childs += [piece_snake, self.segments[0].childs[1]]  # set tail as child

        self.segments.insert(0, body_segment)
        self.segments[1].childs[1] = self.segments[0]

        self.retreat_tail()
        # self.print_snake()
        # print("#####")

    def print_snake(self):
        """
        method to show all the epidemic nodes names

        :return:
        """
        print(self.model.name)
        self.print_recursively(self.model.childs[0])

    def turn_left(self):
        """
        method to turn left the direction of the epidemic.

        :return:
        """
        if self.direction_head == 1 or self.direction_head == 3:  # 1= up, 3=down
            self.direction_head = 2
            self.rotate_head(tr.pi / 2)

        # elif self.direction == 1:#3=down
        #     self.direction = 2

    def turn_right(self):
        if self.direction_head == 1 or self.direction_head == 3:  # 1= up,
            # self.turns += [0]
            self.direction_head = 0
            self.rotate_head(-tr.pi / 2)
        # elif self.direction == 3:#3=down
        #
        #     self.direction = 0
        #     self.rotate_head(0)

    def turn_up(self):
        if self.direction_head == 0 or self.direction_head == 2:  # 0= right,
            self.direction_head = 1
            # self.model.childs[0].transform = tr.translate(0.0 ,self.delta_y, 0.0)
            self.rotate_head(0)
        # elif self.direction == 2:  # 2 = left
        #     self.direction = 1
        #     self.rotate_head(0)

    def turn_down(self):
        if self.direction_head == 0 or self.direction_head == 2:  # 0= right,
            self.direction_head = 3
            self.rotate_head(tr.pi)
        # elif self.direction == 2:  # 2 = left
        #
        #     self.direction = 3

    def rotate_head(self, Angle):
        if self.dead:
            return
        self.model.childs[0].childs[0].transform = tr.rotationZ(Angle)  # rotate head
        # self.segments[-1].transform =  # turn neck
        self.turns += [0]
        self.corners += [(self.pos_x, self.pos_y)]
        self.forward()

    def print_recursively(self, Node):
        if isinstance(Node, sg.SceneGraphNode):
            print(Node.name)
            for i in range(len(Node.childs)):
                self.print_recursively(Node.childs[i])

    # def print_snake2(self):
    #     print(self.model.name)
    #     # print(self.print_recursively(self.model.childs[0]))
    #     for i in reversed(range(len(self.segments))):
    #
    #         print("iteracion: ",self.segments[i].name)
    #     self.print_recursively(self.segments[0].childs[0])
    #     self.print_recursively(self.segments[0].childs[1])

    def get_current_direction(self):
        if self.direction_head == 0:
            return self.delta_x, 0
        elif self.direction_head == 1:
            return 0, self.delta_y
        elif self.direction_head == 2:
            return -self.delta_x, 0
        elif self.direction_head == 3:
            return 0, -self.delta_y

    def update_turns(self):
        if len(self.turns) > 0:
            # print("number of turns: ",len(self.turns))
            for i, index in enumerate(self.turns):
                if index == 0:
                    # print("updating neck")
                    self.update_neck()
                else:
                    # print("updating body")
                    self.update_body_segment_view(index)
                self.turns[i] += 1
            # print("current turn 0: ", self.turns[0])
            if self.turns[0] == len(self.segments) + 1:
                self.turns.pop(0)
                self.corners.pop(1)
                # print("eliminated last element")

                # if len(self.turns)>0:
                #     print("new turn 0:     ",self.turns[0])

    def get_head_direction(self):
        return self.model.childs[0].childs[0].transform

    def update_neck(self):
        delta_x, delta_y = self.get_current_direction()
        self.segments[-1].transform = tr.translate(-delta_x, -delta_y, 0.0)
        self.segments[-1].childs[0].transform = self.get_head_direction()

    def update_body_segment_view(self, Index):
        """
        Method to update the node/image of a given segment of the epidemic
        :param Index: segment of the body
        :return: None
        """
        # print("current_index: ",-Index)
        # print("body size: ",len(self.segments))
        transformation_translate_current_segment = self.segments[-Index].transform
        transformation_visual_current_segment = self.segments[-Index].childs[0].transform
        if Index == len(self.segments):
            self.update_tail_view(transformation_translate_current_segment,
                                  transformation_visual_current_segment)
        else:
            self.segments[-Index - 1].transform = transformation_translate_current_segment
            self.segments[-Index - 1].childs[0].transform = transformation_visual_current_segment

    def update_tail_view(self, Tr_axis, Tr_direction):
        # print("Update tail")
        # self.print_recursively(self.tail)
        # self.print_snake()
        # self.segments[0].transformation = tr.translate(0,-self.delta_y*2,0)#update las segment
        # self.segments[0].transform = Tr_axis#update las segment
        # self.segments[0].childs[0].transform = Tr_direction
        self.tail.transform = Tr_axis
        self.tail.childs[0].transform = Tr_direction

    def update_position(self):
        self.update_tail_position()

        if self.direction_head == 0:
            self.pos_x += 1
        elif self.direction_head == 1:
            self.pos_y -= 1
        elif self.direction_head == 2:
            self.pos_x -= 1
        elif self.direction_head == 3:
            self.pos_y += 1

    def out_of_field(self):
        if self.pos_x == 0:
            return self.direction_head == 2
        elif self.pos_x == self.size_field + 1:
            return self.direction_head == 0
        elif self.pos_y == 0:
            return self.direction_head == 1
        elif self.pos_y == self.size_field + 1:
            return self.direction_head == 3
        return False

    def retreat_tail(self):
        # print("current tail position :",self.corners[0])
        if len(self.corners) > 1:
            # print("number corners: ",len(self.corners))
            # print("corners: ",self.corners[0])
            # print("corners: ", self.corners[1])
            delta_x, delta_y = self.get_delta_tail(1)
            x, y = self.corners[0]

            if delta_x > 0:
                self.corners[0] = (x - 1, y)

            elif delta_y < 0:
                self.corners[0] = (x, y + 1)

            elif delta_x < 0:
                self.corners[0] = (x + 1, y)

            else:
                self.corners[0] = (x, y - 1)
        else:
            x, y = self.corners[0]
            if self.direction_head == 0:
                self.corners[0] = (x - 1, y)

            elif self.direction_head == 1:
                self.corners[0] = (x, y + 1)

            elif self.direction_head == 2:
                self.corners[0] = (x + 1, y)

            elif self.direction_head == 3:
                self.corners[0] = (x, y - 1)

        # print("new tail position :",self.corners[0])

    def snake_bites_its_tail(self):
        # print("number corners",len(self.corners))
        for i in range(1, len(self.corners)):
            # print("current position: ",self.pos_x,", ",self.pos_y)
            # print("index: ",i)
            # print("current:  ", self.corners[i])
            # print("previous: ", self.corners[i - 1])

            delta_x, delta_y = self.get_delta_tail(i)

            if delta_x == 0:  # vertical segment
                # print("vertical segment")
                if self.pos_x == self.corners[i - 1][0]:  # same column
                    # print("same column")
                    if delta_y > 0:
                        if self.corners[i - 1][1] <= self.pos_y and self.pos_y <= self.corners[i][1]:
                            return True
                    else:
                        if self.corners[i - 1][1] >= self.pos_y and self.pos_y >= self.corners[i][1]:
                            return True
            else:
                # print("horizontal segment")
                if self.pos_y == self.corners[i - 1][1]:  # same row
                    # print("same row")
                    if delta_x > 0:
                        # print("positive delta")
                        if self.corners[i - 1][0] <= self.pos_x and self.pos_x <= self.corners[i][0]:
                            return True
                    else:
                        # print("negative delta")
                        if self.corners[i - 1][0] >= self.pos_x and self.pos_x >= self.corners[i][0]:
                            return True
        return False

    def update_tail_position(self):
        if len(self.corners) == 1:
            # print("moving tail forward")
            x, y = self.corners[0]
            if self.direction_head == 0:
                self.corners[0] = (x + 1, y)

            elif self.direction_head == 1:
                self.corners[0] = (x, y - 1)

            elif self.direction_head == 2:
                self.corners[0] = (x - 1, y)

            elif self.direction_head == 3:
                self.corners[0] = (x, y + 1)
        else:
            # print("movint tail to next border")
            self.update_position_tail()

    def update_position_tail(self):
        """
        Method to update the position of the tail if there is a corner between the head and the end of it.

        :return: None
        """
        delta_x, delta_y = self.get_delta_tail(1)

        if delta_x == 0:
            if delta_y > 0:
                self.corners[0] = (self.corners[0][0] + 0, self.corners[0][1] + 1)
            else:
                self.corners[0] = (self.corners[0][0] + 0, self.corners[0][1] - 1)
        else:
            if delta_x > 0:
                self.corners[0] = (self.corners[0][0] + 1, self.corners[0][1] + 0)
            else:
                self.corners[0] = (self.corners[0][0] - 1, self.corners[0][1] + 0)

    def get_delta_tail(self, index):
        return self.corners[index][0] - self.corners[index - 1][0], self.corners[index][1] - self.corners[index - 1][1]

    def die(self):
        glClearColor(1, 0, 0, 1.0)  # Cambiamos a rojo

    def rat_eaten(self, rat):
        """

        :type rat: target
        :param rat: objective
        :return:
        """
        if rat.eaten(self.pos_x, self.pos_y):
            # print("extend")
            self.extend()
            return True
        return False

    def report(self):
        print("pos_snake x:{:d} y:{:d}".format(self.pos_x, self.pos_y))

    def just_moved(self):
        if self.move_just_a_moment_before:
            self.move_just_a_moment_before = False
            return True
        return False


class target(basic_model):

    def __init__(self, Size_field):

        self.size_field = Size_field
        self.delta_x = 1
        self.delta_y = 1

        gpu_red = es.toGPUShape(bs.createColorQuad(1, 0, 0))  # red
        rotated_apple_side = sg.SceneGraphNode("rotated_apple")
        rotated_apple_side.transform = tr.rotationZ(-3.1415 / 4)
        rotated_apple_side.childs += [gpu_red]

        left_side_apple = sg.SceneGraphNode("left_side_apple")
        left_side_apple.transform = tr.translate(-0.25, 0.2, 0)
        left_side_apple.childs += [rotated_apple_side]

        right_side_apple = sg.SceneGraphNode("right_side_apple")
        right_side_apple.transform = tr.translate(0.25, 0.2, 0)
        right_side_apple.childs += [rotated_apple_side]

        lower_side_apple = sg.SceneGraphNode("lower_side_apple")
        lower_side_apple.transform = tr.matmul([tr.translate(0.0, -0.5, 0), tr.uniformScale(0.5)])
        lower_side_apple.childs += [gpu_red]

        apple = sg.SceneGraphNode("apple")
        apple.transform = tr.scale(0.5, 0.5, 1)
        apple.childs += [left_side_apple, right_side_apple, lower_side_apple]

        # apple_tr = sg.SceneGraphNode('appleTR')
        # apple_tr.childs += [apple]

        # apple.childs += [gpu_red]

        # gpu_body = es.toGPUShape(bs.createTextureQuad("figures/rat.png", 1, 1), GL_REPEAT,GL_NEAREST)  # tail

        if Size_field % 2 == 0:
            self.conversion = self.positions_to_coordinates_even
        else:
            self.conversion = self.positions_to_coordinates_odd
        self.list_locations = [i for i in range(1, Size_field + 1)]

        # print("positions: ",self.list_locations)
        # rat
        rat_pos = sg.SceneGraphNode("rat_pos")

        self.position_x = None
        self.position_y = None
        rat_pos.childs += [apple]
        self.rat_position = rat_pos
        self.update()

        rat = sg.SceneGraphNode("rat")
        rat.transform = tr.uniformScale(1.9 / Size_field)
        rat.childs += [rat_pos]
        self.model = rat

    def positions_to_coordinates_even(self, value):
        return (value - self.size_field / 2) - 0.5

    def positions_to_coordinates_odd(self, value):
        return value - int(self.size_field / 2 + 0.5)

    def update(self):
        random_pos_x = random.choice(self.list_locations)
        random_pos_y = random.choice(self.list_locations)
        # print("current x: ",self.delta_x * self.conversion(random_pos_x))
        self.rat_position.transform = tr.translate(self.delta_x * self.conversion(random_pos_x),
                                                   -self.delta_y * self.conversion(random_pos_y), 0)
        self.position_x = random_pos_x
        self.position_y = random_pos_y
        # print("rat is in the position: ",random_pos_x," ,",random_pos_y)

    def eaten(self, X, Y):
        died = X == self.position_x and Y == self.position_y
        if died:
            print("same position")
            self.update()
            return True
        # print("Not same position {:d}~={:d} or  {:d}~={:d}".format(X,self.position_x,Y, self.position_y))

        return False

    def report(self):
        print("pos_Apple x:{:d} y:{:d}".format(self.position_x, self.position_y))