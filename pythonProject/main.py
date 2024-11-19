from fileinput import close


#TODO data preprocessing


#TODO LSH part


#TODO data post-processing

#look for candidate pairs
#go over all buckets to find candidate pairs
#create a list of all candidate pairs, no duplicates, lowest index first

def find_candidate_pairs(minhash):
    #create set of tuples for candidate pairs
    #set automatically takes care of duplicates
    candidates = set()



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
    intersection = len(cand1.intersection(cand2))
    union = len(cand1.union(cand2))

    #true if jaccard similarity is bigger then 0.5
    return intersection/union > 0.5


def print_pair_to_file(cand1, cand2, write_mode):
    with open('pairs.txt', write_mode) as f:
        f.write(str(cand1)+ ','+ str(cand2)+'\n')
        close()

# print similar pairs to file
def find_and_print_pairs(minhash_table, signature_matrix, candidate_data):
    #go over the buckets to find candidate pairs
    candidate_pairs = find_candidate_pairs(minhash_table)
    print('pairs')
    write_mode = 'w'
    for (cand1, cand2) in candidate_pairs:
        #first compare signatures
        if compare_cand_signatures(signature_matrix(cand1), signature_matrix(cand2)):
           #if signatures seem similar, compare the original data
           if compare_cand_original(cand1, cand2):
               #original is also similar so write to file
               print_pair_to_file(cand1, cand2, write_mode)
               #after first pair is written, append to file instead of writing
               write_mode = 'a'


if __name__ == "__main__":
    print('main')
    find_candidate_pairs("hey")

    print_pair_to_file(1, 3, 'w')
    print_pair_to_file(1, 4, 'a')
    print_pair_to_file(1, 5, 'a')
    print_pair_to_file(1, 6, 'a')