import json
import map_of_city as mc
import Individuals as ind
import models as md


class pandemic_manager:
    def __init__(self, path='/home/luis/2020/computacion grafica/pandemic/virus.json'):
        with open(path) as f:
            population_characteristics = json.load(f)

        self.steps_per_day = 15
        self.current_step = 0
        self.city_size = 100

        # self.population = self.create_population(population_characteristics['Initial_population'],
        population = self.create_population(4,
                                            population_characteristics['Death_rate'],
                                            population_characteristics['Days_to_heal'],
                                            population_characteristics['Number_sick'],
                                            population_characteristics['Percentage_healthy'],
                                            population_characteristics['Percentage_normal'],
                                            self.steps_per_day,
                                            self.city_size)

        # models_population = self.add_model(population)
        # self.add_model(population)

        self.map = mc.map_of_city(population,
                                  population_characteristics['Contagious_prob'],
                                  population_characteristics['Radius'],
                                  self.city_size,
                                  population_characteristics['Number_urban_centers'])

        self.next_action = self.stay_still

    def create_population(self, n_population, death_rate, days_to_heal, number_sick_people, percentage_healthy_people,
                          percentage_normal_people, steps_per_day, city_size):
        population = self.get_sick_population(death_rate, days_to_heal, number_sick_people, percentage_healthy_people,
                                              percentage_normal_people, steps_per_day, city_size)
        n_healthy = int((n_population - number_sick_people) * percentage_healthy_people)
        n_normal = int((n_population - number_sick_people) * percentage_normal_people)
        if percentage_normal_people + percentage_normal_people > 1:
            raise ValueError("Invalid combinations of percentage values {:.2f} and {:.2f}".format(
                percentage_healthy_people, percentage_normal_people))
        n_risk = max(n_population - number_sick_people - n_healthy - n_normal, 0)

        for i in range(n_healthy):
            population += [ind.individual(0, 1, death_rate, days_to_heal, steps_per_day, city_size)]

        for i in range(n_normal):
            population += [ind.individual(1, 1, death_rate, days_to_heal, steps_per_day, city_size)]

        for i in range(n_risk):
            population += [ind.individual(2, 1, death_rate, days_to_heal, steps_per_day, city_size)]

        return population

    def get_sick_population(self, death_rate, days_to_heal, number_sick_people, percentage_healthy_people,
                            percentage_normal_people, steps_per_day, city_size):
        # print("days to heal: ",days_to_heal)
        population_sick = []
        n_healthy = int((number_sick_people) * percentage_healthy_people / \
                        (percentage_healthy_people + percentage_normal_people))
        for i in range(n_healthy):

            population_sick += [ind.individual(state_person=0,state_sickness=2, prob_of_death = death_rate,
                                              days_until_recovered = days_to_heal,steps = steps_per_day,
                                               city_size= city_size)]

        for i in range(n_healthy,number_sick_people):
            population_sick += [ind.individual(state_person=1,state_sickness=2, prob_of_death = death_rate,
                                              days_until_recovered = days_to_heal,steps = steps_per_day,
                                               city_size= city_size)]

        print("number sick people: ",len(population_sick))
        return population_sick

    def add_model(self, population):
        """
        Method to get the models (graphic models) of the population


        :type population: List(ind.individual)
        :param population:
        :rtype: (List(md.individual_graph))
        :return:
        """
        n_population = len(population)
        # models_citizen = []
        for i in range(n_population):
            # models_citizen.append(md.individual_graph(self.city_size, population[i].start_position,
            #                                           population[i].state_sickness))
            population.set_model(md.individual_graph(self.city_size, population[i].start_position,
                                                      population[i].state_sickness))
        # return models_citizen

    def next_day(self):
        if self.current_step == 0:
            # print("next day")
            self.next_action = self.next_step

    def next_step(self, pipeline):
        if self.current_step == self.steps_per_day:
            self.map.step_and_update_cases()
            # self.map.check_contagious()

        elif self.current_step == self.steps_per_day * 2 + 1:
            # print("still mode")
            self.map.step_and_update_cases()
            self.current_step = -1
            self.next_action = self.stay_still
            self.map.check_sick_people()
            self.map.next_day()
            # self.map.check_contagious()

        else:
            self.map.step()

        self.current_step += 1
        self.map.draw(pipeline)

    def stay_still(self, pipeline):
        """
        Method to interact with the displaying graphic interface. No movement action perform on the graphs.

        :return:
        """
        self.draw(pipeline)

    def draw(self, pipeline):
        self.map.draw(pipeline)
