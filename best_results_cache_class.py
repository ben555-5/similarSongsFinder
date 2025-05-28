# keeps the best "max_size" results given their rank
class BestResultCache:
    def __init__(self, max_size=10):
        self.cache = []  # list of tuples of (result, rank)
        self.max_size = max_size

    def get_best_results(self):
        return self.cache[:self.max_size]

    def update_result(self, result, rank):
        if len(self.cache) < self.max_size:
            self.cache.append((result, rank))
        else:
            # if cache is full, replace the worst result if the new one is better
            if rank > self.cache[-1][1]:
                self.cache[-1] = (result, rank)

        self.cache.sort(reverse=True, key=lambda x: x[1])  # sort by rank


