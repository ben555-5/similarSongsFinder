class BestResultCache:
    def __init__(self, max_size=10):
        self.cache = []  # (title: str, score: int)
        self.max_size = max_size

    def update_result(self, title, score):
        self.cache.append((title, score))
        self.cache.sort(key=lambda x: x[1], reverse=True)
        self.cache = self.cache[:self.max_size]

    def get_best_results(self):
        return self.cache