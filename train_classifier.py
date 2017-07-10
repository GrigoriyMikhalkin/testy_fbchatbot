import csv

from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer

from classifiers.preprocessors import normalizing_preprocessor


DATASET_PATH = './data/dataset.csv'
CLASSIFIER_PATH = './data/forest.pkl'
VECTORIZER_PATH = './data/vectorizer.pkl'


def vectorize_data(data):
    """
    Vectorizing data for training

    :param: data: list: raw data
    :return: numpy.array: vectorized data
    """

    vectorizer = CountVectorizer(analyzer='word',
                                 preprocessor=normalizing_preprocessor,
                                 stop_words=None, max_df=0.8)
    vectorized_data = vectorizer.fit_transform(data)
    data_array = vectorized_data.toarray()

    # pickle vectorizer
    joblib.dump(vectorizer, VECTORIZER_PATH)

    return data_array


def main():
    """
    Training classifier and then pickling it for use in chatbot
    """
    with open(DATASET_PATH, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        unprocessed_data = []
        labels = []
        for row in reader:
            unprocessed_data.append(row['sentence'])
            labels.append(row['category'])

        # process and vectorize data
        vectorized_data = vectorize_data(unprocessed_data)

        # train classifier
        forest = RandomForestClassifier(n_estimators=10)
        forest.fit(vectorized_data, labels)

        # pickling classifier
        joblib.dump(forest, CLASSIFIER_PATH)


if __name__ == '__main__':
    main()
