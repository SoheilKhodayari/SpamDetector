import pickle
from collections import defaultdict
from hash_Dict import D

class Classifier(object):
    def __init__(self):
        self.features = D(int)
        self.labels = D(int)
        self.feature_counts = D(lambda: D(int))
        self.total_count = 0
   
    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as fh:
            features, labels, fc, total = pickle.load(fh)
        inst = cls()
        inst.features.update(features)
        inst.labels.update(labels)
        for feature, labels in fc.items():
            for label, ct in labels.items():
                inst.feature_counts[feature][label] = ct
        inst.total_count = total
        return inst
    #savin the database -->>byte stream
    def save(self, filename):
        fc = {}
        for feature, labels in self.feature_counts.items():
            fc[feature] = {}
            for label, ct in labels.items():
                fc[feature][label] = ct
        features = dict(self.features)
        labels = dict(self.labels)
        total = self.total_count
        with open(filename, 'wb') as fh:
            pickle.dump((features, labels, fc, total), fh)

    def train(self, features, labels):
        for label in labels:
            for feature in features:
                self.feature_counts[feature][label] += 1
                self.features[feature] += 1

            self.labels[label] += 1
        self.total_count += 1

    def feature_probability(self, feature, label):
        feature_count = self.feature_counts[feature][label]

        label_count = self.labels[label]

        if feature_count and label_count:
            # divide by the count of all features in the given category
            return float(feature_count) / label_count
        return 0

    def weighted_probability(self, feature, label, weight=1.0, ap=0.5):

        initial_prob = self.feature_probability(feature, label)
        feature_total = self.features[feature]

        return float((weight * ap) + (feature_total * initial_prob)) / (weight + feature_total)

    def document_probability(self, features, label):

        p = 1
        if not features:
            return 1 if label=="spam" else 0
        else:
            for feature in features:
                p *= self.weighted_probability(feature, label)
        return p

    def probability(self, features, label):
        if not self.total_count:
            # avoid doing a divide by zero
            return 0
        label_prob = float(self.labels[label]) / self.total_count


        doc_prob = self.document_probability(features, label)


        return doc_prob * label_prob

    def classify(self, features, limit=5):

        probs = {}
        for label in self.labels.keys():
            probs[label] = self.probability(features, label)

        # sort the results so the highest probabilities come first
        return sorted(probs.items(), key=lambda (k,v): v, reverse=True)[:limit]
