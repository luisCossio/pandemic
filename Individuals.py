import sys

import numpy as np
from numpy.core._multiarray_umath import ndarray
import models as md


class individual:
    model: md.individual_graph
    start_direction: ndarray
    end_direction: ndarray
    end_position: ndarray
    start_position: ndarray
    hermite_matrix: ndarray

    def __init__(self, state_person=1, state_sickness=1, prob_of_death=0.1, days_until_recovered=10,
                 steps=24, city_size=100):
        # Cinematic properties
        self.time = 0
        #         self.range = np.random.uniform(0,city_size)
        self.range = city_size
        self.steps = steps
        self.delta = 1 / self.steps
        self.current_step = 0
        self.city_size = city_size
        self.start_position = np.random.uniform(0, 100, [2, 1])
        self.end_position = self.get_random_position(self.range)
        self.start_direction = self.get_random_vector()
        self.end_direction = self.get_random_vector()
        self.matrix_cinematic = np.concatenate([self.start_position, self.end_position,
                                                -self.start_direction, -self.end_direction], axis=1)

        self.hermite_matrix = np.array([[1, -1, -1, 1], [0, 0, 3, -2],
                                        [0, 1, -2, 1], [0, 0, -1, 1]],
                                       dtype=np.float32)
        self.move = self.steps_forward  # set movement action

        #  Health state properties
        self.health_condition = state_person  # health state of the person. 0 for very Healthy, 1 for average, 2 for vulnerable

        self.probability_of_death = prob_of_death

        self.days_sick = 0
        self.days_until_recovered = days_until_recovered
        self.state_sickness = state_sickness  # 0 for dead, 1 for susceptible, 2 for sick, 3 for immune
        # model
        self.model = md.individual_graph(self.city_size, self.start_position,
                                         self.state_sickness)

        self.pass_one_day = None
        self.is_sick = self.non_sick_person_exam

        if state_sickness == 2:
            self.get_sick = self.get_sick_non_receptive_person
            self.get_sick_non_immune()

        else:
            self.get_sick = self.get_sick_non_immune
            self.pass_one_day = self.non_sick_day

        # print('positions : \n start:',self.start_position,' \n end: ',self.end_position)

    def reached_position(self):
        # print('before: \n start:',self.start_position,' \n end: ',self.end_position)
        # print('before: \n start:',self.start_direction,' \n end: ',self.end_direction)
        pos = self.start_position.copy()
        self.start_position = self.end_position.copy()
        self.end_position = pos
        self.start_direction = self.end_position
        self.end_direction = self.get_random_vector()
        # print('positions : \n start:',self.start_position,' \n end: ',self.end_position)
        # print('after : \n start:',self.start_direction,' \n end: ',self.end_direction)
        self.matrix_cinematic = np.concatenate([self.start_position, self.end_position,
                                                self.start_direction, self.end_direction], axis=1)

    def get_random_position(self, radius):
        """

        :rtype: ndarray
        """
        pos = self.start_position + np.random.uniform(-radius / 2, radius / 2, [2, 1])
        counter = 0
        # print("start: ",self.start_position)
        while pos[0] < 0 or pos[0] > self.city_size:
            pos[0] = self.start_position[0] + np.random.uniform(-radius / 2, radius / 2, [1])
            counter += 1
            # print("new: ", pos)
            if counter > 5:
                pos[0] = np.random.uniform(0, self.city_size)
                # if pos[0] > 0:
                #     pos[0] = self.city_size-1
                # else:
                #     pos[0] = 0
                break
        counter = 0
        while pos[1] < 0 or pos[1] > self.city_size:
            pos[1] = self.start_position[1] + np.random.uniform(-radius / 2, radius / 2, [1])
            counter += 1
            # print("new: ", pos)
            if counter > 5:
                pos[1] = np.random.uniform(0, self.city_size)
                # if pos[1] > 0:
                #     pos[1] = self.city_size - 1
                # else:
                #     pos[1] = 0
                break
        return pos
    def get_random_vector(self):
        """
        Method to get a random vector, used mainly to get a unitary direction to define next position

        :rtype: ndarray
        """
        vector = np.random.normal(0, 25, [2, 1])
        # return vector / np.linalg.norm(vector)
        return vector

    def steps_forward(self):
        # print("time: {:.2f}".format(self.time))
        # print("time: {:d}/{:d}".format(self.current_step,self.steps))
        if self.current_step == self.steps:
            # print("end moving")
            self.reached_position()
            self.time = 0
            self.current_step = 0
            # self.model.update_location(self.start_position)
            return self.start_position
        # print("move forward")
        time = np.array([[1], [self.time], [self.time ** 2], [self.time ** 3]])
        self.time += self.delta
        self.current_step += 1
        # pos = self.hermite_location(time)
        # self.model.update_location(pos)
        # return pos
        return self.hermite_location(time)

    def death_state_no_move(self):
        """
        Method to give the position of dead units. Dead units don't move
        :rtype: ndarray
        :return:
        """
        return self.start_position



    def hermite_location(self, time):
        # print("shape Cinematic:",self.matrix_cinematic.shape)
        # print("shape hermite_matrix:",self.hermite_matrix.shape)
        # print("shape time:",time.shape)
        return np.matmul(self.matrix_cinematic, np.matmul(self.hermite_matrix, time))

    def strong_immune_system_sick(self):
        if np.random.uniform() < self.probability_of_death / 50:
            self.set_death_state()
            return True
        self.sickness_evolution_one_day()
        return False

    def average_immune_system_sick(self):
        if np.random.uniform() < self.probability_of_death:
            self.set_death_state()
            return True
        self.sickness_evolution_one_day()
        return False

    def weak_immune_system_sick(self):
        if np.random.uniform() < self.probability_of_death * 2:
            self.set_death_state()
            return True

        self.sickness_evolution_one_day()
        return False

    def non_sick_day(self):
        pass

    def sickness_evolution_one_day(self):
        self.days_sick += 1
        # print("increase in days: ", self.days_sick)
        if self.days_sick > self.days_until_recovered:
            # print("cured")
            self.state_sickness = 3  # recovered/immune
            self.get_sick = self.get_sick_non_receptive_person
            self.model.update_state(3)
            self.pass_one_day = self.non_sick_day
            self.is_sick = self.non_sick_person_exam


    def set_death_state(self):
        # print("new death")
        self.start_position = self.steps_forward()  # last step
        self.move = self.death_state_no_move
        self.get_sick = self.get_sick_non_receptive_person
        self.state_sickness = 0
        self.model.update_state(0)
        self.pass_one_day = self.non_sick_day
        self.is_sick = self.non_sick_person_exam

    def get_sick_non_immune(self):
        self.state_sickness = 2
        self.is_sick = self.sick_person_exam
        self.model.update_state(2)
        if self.health_condition == 0:
            self.pass_one_day = self.strong_immune_system_sick

        elif self.health_condition == 1:
            self.pass_one_day = self.average_immune_system_sick
        else:
            self.pass_one_day = self.weak_immune_system_sick

    def get_sick_non_receptive_person(self):
        """
        Method that simulates that an immune person or dead person enter in contact with the virus. Nothing happens
        in this representation.
        :return:
        """
        pass

    def sick_person_exam(self):
        return True

    def non_sick_person_exam(self):
        return False

    def set_model(self, model):
        self.model = model

    def draw(self, pipeline):
        self.model.draw(pipeline)
