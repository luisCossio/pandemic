from typing import List

import numpy as np

import Individuals as ind
import models as md
from sklearn.cluster import DBSCAN

class map_of_city:
    population: List[ind.individual]

    def __init__(self, population, contagious_prob, radius_contagious = 10, city_size = 100, number_of_centers = 4):
        # population characteristics
        self.population = population
        self.population_size = len(population)
        # self.models_population = models

        # disease properties
        self.radius = radius_contagious
        self.contagious_prob = contagious_prob
        self.number_of_centers = number_of_centers

        # city properties
        self.city_size = city_size
        self.centers_radius = radius_contagious*3  # this is how big radius of centers are.
        self.centers = self.get_centers(number_of_centers)
        self.center_models = self.get_centers_models()

    def draw(self, pipeline):
        for i in range(len(self.population)):
            self.population[i].draw(pipeline)

        for i in range(self.number_of_centers):
            self.center_models[i].draw(pipeline)


    def step(self):
        for i in range(self.population_size):
            location = self.population[i].move()
            location = self.limits(location)
            location = self.modify_location_centers(location)
            self.population[i].model.update_location(location)
            # for j in range(self.number_of_centers):
            # self.models_population[i].update_location(location)
            # self.population[i].pass_one_day()

    def step_and_update_cases(self):
        locations = []
        # disease = []
        for i in range(self.population_size):
            location = self.population[i].move()
            location = self.limits(location)
            location = self.modify_location_centers(location)
            self.population[i].model.update_location(location)
            locations += [location]

            # for j in range(self.number_of_centers):
            # self.models_population[i].update_location(location)
            # self.population[i].pass_one_day()

        self.update_sick(locations)

    def limits(self, location):
        location = np.minimum(location,self.city_size)
        return np.maximum(location,0)

    def get_centers(self, number_of_centers):
        centers = []
        for i in range(number_of_centers):
            centers += [self.get_random_position()]
        return centers
    
    def get_centers_models(self):
        models = []
        for i in range(self.number_of_centers):
            models += [md.center_graph(self.city_size,self.centers[i])]
        return models

    def get_random_position(self):
        return np.random.uniform(0, self.city_size, [2, 1])

    def modify_location_centers(self, location):
        for i in range(self.number_of_centers):
            dist = self.distance_between(location, self.centers[i])
            if dist < self.centers_radius:
                return self.modify_location(dist,location,self.centers[i])
        return location

    def update_sick(self, locations):
        locations = np.concatenate(locations, axis=1)
        clustering = DBSCAN(eps=self.radius, min_samples=1, algorithm='kd_tree').fit(locations.transpose())
        indexes = [[] for i in range(clustering.labels_.max() + 1)]
        for i, cluster in enumerate(clustering.labels_):
            indexes[cluster] += [i]
        for i in range(clustering.labels_.max() + 1):
            for index in (indexes[i]):
                if self.population[index].is_sick() and len(indexes[i]) > 1:
                    self.infect_cluster(indexes[i])
                    break

    def infect_cluster(self, cluster):
        for index in cluster:
            if self.contagious_prob > np.random.uniform():
                self.population[index].get_sick()

    def next_day(self):
        for i in range(self.population_size):
            self.population[i].pass_one_day()

    def distance_between(self, pos1, pos2):
        return np.linalg.norm(pos1-pos2)

    def modify_location(self, dist_to_center, pos_individual, center):
        alpha = dist_to_center/self.radius
        return pos_individual*alpha + (1-alpha)*center

