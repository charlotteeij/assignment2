import numpy as np
import scipy.sparse
import hashlib
from itertools import combinations


def generate_signatures(data_file, num_permutations=100):

    data = np.load(data_file)
    users = data[:, 0]
    movies = data[:, 1]
    ranking = data[:, 2]

    matrix = scipy.sparse.csr_matrix((ranking, [users, movies]))
    print(matrix)

    print(np.shape(matrix))
    num_users = int(max(users))
    num_movies = int(max(movies))

    permutations = []
    for _ in range(num_permutations):
        permutations.append(np.random.permutation(num_movies + 1))

    signatures = np.zeros((num_permutations, num_users + 1), dtype=int)
    for num, permutation in enumerate(permutations):
        for user in range(1, num_users + 1):
            user_movies = matrix[user].indices
            if len(user_movies) > 0:
                signatures[num, user] = np.min(permutation[user_movies])
    signatures = signatures[:, 1:]

    print(signatures)
    return signatures, num_users


def hash_band(band):

    return hashlib.md5(band.tobytes()).hexdigest()

def lsh(signatures, num_users, rows_per_band, num_bands, seed=None):

    if seed is not None:
        np.random.seed(seed)

    buckets = [{} for _ in range(num_bands)]  # List of dictionaries

    for user_id in range(num_users):
        user_signature = signatures[:, user_id]
        for band_idx in range(num_bands):
            start_row = band_idx * rows_per_band
            end_row = start_row + rows_per_band
            band = user_signature[start_row:end_row]

            band_hash = hash_band(band)
            if band_hash not in buckets[band_idx]:
                buckets[band_idx][band_hash] = []
            buckets[band_idx][band_hash].append(user_id)

    print("LSH Finished")
    return buckets


if __name__ == "__main__":

    data_file = 'user_movie_rating.npy'
    num_permutations = 100
    rows_per_band = 5
    seed = 42

    signatures, num_users = generate_signatures(data_file, num_permutations)
    num_bands = signatures.shape[0] // rows_per_band  # Total bands
    buckets = lsh(signatures, num_users, rows_per_band, num_bands, seed=seed)

