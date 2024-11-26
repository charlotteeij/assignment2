import numpy as np
import scipy.sparse
import hashlib
from itertools import combinations
from fileinput import close


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

    sign = np.zeros((num_permutations, num_users + 1), dtype=int)
    for num, permutation in enumerate(permutations):
        for user in range(1, num_users + 1):
            user_movies = matrix[user].indices
            if len(user_movies) > 0:
                sign[num, user] = np.min(permutation[user_movies])
    sign = sign[:, 1:]

    print(sign)
    return sign, num_users, matrix


def hash_band(band):

    return hashlib.md5(band.tobytes()).hexdigest()

def lsh(signatures, num_users, rows_per_band, num_bands, seed=None):
    print('start LSH')
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

#look for candidate pairs
#go over all buckets to find candidate pairs
#create a list of all candidate pairs, no duplicates, lowest index first
def find_candidate_pairs(minhash):
    #create list of tuples for candidate pairs
    candidates = set()

    #iterate over all the buckets
    for num, band_id in enumerate(minhash):
        for key, value in minhash[num].items():
            #ignore buckets that are too big (more than 10 items)
            if len(value) > 10:
                continue
            #find all possible pair combinations
            for i in range(len(value)):
                for j in range(i + 1, len(value)):
                    #make sure the lowest value is the first item
                    if value[i] < value[j]:
                        candidates.add((value[i], value[j]))
                    else:
                        candidates.add((value[j], value[i]))
    # print('candidates', candidates)
    return candidates

#compare candidate pairs (signature)
#jaccard similarity > 0,5 -> at least 50% of similar positions in the signature
def compare_cand_signatures(sign1, sign2):
    #The similarity of signatures is the fraction of the positions in which they agree
    #keep track of the portion of positions in which they agree
    count_sim = 0
    #target of similarities is 50%, so if this target is reached no need to compare further
    target_count = len(sign1)/2
    for i in range(len(sign1)):
        #if similar count one
        if sign1[i] == sign2[i]:
            count_sim += 1
        #if similarity passed the target then return true
        if count_sim >= target_count:
            return True
    #similarity did not pass target, so return False
    return False

#compare candidate pairs (original)
def compare_cand_original(cand1, cand2):
    #calc jaccard similarity by dividing the size of the intersection (all items)
    # by the size of the union (same items)
    cand1_set = set(cand1)
    cand2_set = set(cand2)
    intersection = len(cand1_set.intersection(cand2_set))
    union = len(cand1_set.union(cand2_set))
    similarity = intersection / union
    #true if jaccard similarity is bigger then 0.5
    return similarity > 0.5

def print_pair_to_file(cand1, cand2, write_mode):
    with open('pairs.txt', write_mode) as f:
        f.write(str(cand1)+ ','+ str(cand2)+'\n')
        close()

# print similar pairs to file
def find_and_print_pairs(minhash_table, signatures, candidate_data):
    #go over the buckets to find candidate pairs
    candidate_pairs = find_candidate_pairs(minhash_table)
    print('amount of candidate pairs:', len(candidate_pairs))
    write_mode = 'w'
    for (cand1, cand2) in candidate_pairs:
        #first compare signatures
        if compare_cand_signatures(signatures[:, cand1], signatures[:, cand2]):
           print('signature check passed', cand1, cand2)
           #if signatures seem similar, compare the original data
           if compare_cand_original(candidate_data[cand1].indices, candidate_data[cand2].indices):
               print('candidate check passed', cand1, cand2)
               #original is also similar so write to file
               print_pair_to_file(cand1, cand2, write_mode)
               #after first pair is written, append to file instead of writing
               write_mode = 'a'


if __name__ == "__main__":

    data_file = 'user_movie_rating.npy'
    num_permutations = 100
    rows_per_band = 5
    seed = 42

    signatures, num_users, matrix = generate_signatures(data_file, num_permutations)
    num_bands = signatures.shape[0] // rows_per_band  # Total bands
    buckets = lsh(signatures, num_users, rows_per_band, num_bands, seed=seed)

    find_and_print_pairs(buckets, signatures, matrix)
