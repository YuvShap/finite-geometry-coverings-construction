import itertools
import galois
import numpy as np
import math


class CoveringConstructor:
    def __init__(self, q, t, m, chosen_points_indices):
        self.__q = q
        self.__GF = galois.GF(q)
        self.__number_of_rows = m - t + 1
        self.__number_of_cols = m + 1
        self.__chosen_points = self.__translate_chosen_indices_to_points(chosen_points_indices)

    def __translate_chosen_indices_to_points(self, chosen_points_indices):
        chosen_points = np.zeros((self.__number_of_cols, len(chosen_points_indices)), dtype=int)
        for point_i, chosen_point_index in enumerate(chosen_points_indices):
            n = 1
            current_sum = 1
            while current_sum < chosen_point_index + 1:
                n += 1
                current_sum += (self.__q ** (n-1))

            left = (chosen_point_index + 1) - int((self.__q ** (n - 1) - 1) // (self.__q - 1)) - 1
            point = np.zeros(self.__number_of_cols, dtype=int)
            for i in range(n - 1):
                point[i] = left % self.__q
                left = math.floor(left / self.__q)
            point[n - 1] = 1
            point = np.flip(point)
            chosen_points[:, point_i] = point.T
        return self.__GF(chosen_points)

    def __create_block(self, matrix):
        result = matrix @ self.__chosen_points
        result = result.view(np.ndarray)
        result2 = np.max(result, axis=0)
        return np.nonzero(result2 == 0)[0]

    def __get_possible_matrices_for_leading_indices(self, leading_indices):
        free_entries = [(row_index, col_index) for row_index in range(self.__number_of_rows) for col_index in
                        range(leading_indices[row_index] + 1, self.__number_of_cols) if col_index not in leading_indices]
        free_x = np.asarray([x for x,y in free_entries])
        free_y = np.asarray([y for x,y in free_entries])
        matrix = self.__GF(np.zeros((self.__number_of_rows, self.__number_of_cols), dtype=int))
        for row_index in range(self.__number_of_rows):
            matrix[row_index, leading_indices[row_index]] = 1
        if len(free_entries) > 0:
            for option in itertools.product(range(0, self.__q), repeat=len(free_entries)):
                matrix[free_x, free_y] = np.asarray(option)
                yield matrix
        else:
            yield matrix

    def stream_induced_covering(self, part_index, num_of_parts, conn):
        matrix_index = 0
        for leading_indices in itertools.combinations(range(self.__number_of_cols - 1, -1, -1), self.__number_of_rows):
            for matrix in self.__get_possible_matrices_for_leading_indices(leading_indices):
                if matrix_index % num_of_parts == part_index:
                    block = self.__create_block(matrix)
                    if conn is not None:
                        conn.send(block)
                    else:
                        print(block)
                matrix_index += 1

