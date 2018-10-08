from keras.layers import Dense, Dropout, GlobalAveragePooling2D, Flatten
from keras.models import Model, load_model
from keras.applications.xception import Xception, preprocess_input
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, EarlyStopping
import argparse
import numpy as np
from utils.data import create_generator_from_stash
import matplotlib.pyplot as plt

gen = create_generator_from_stash('data/train_numpy')

from keras import backend as K


def weighted_categorical_crossentropy(weights):
    """
    A weighted version of keras.objectives.categorical_crossentropy

    Variables:
        weights: numpy array of shape (C,) where C is the number of classes

    Usage:
        weights = np.array([0.5,2,10]) # Class one at 0.5, class 2 twice the normal weights, class 3 10x.
        loss = weighted_categorical_crossentropy(weights)
        model.compile(loss=loss,optimizer='adam')
    """

    weights = K.variable(weights)

    def loss(y_true, y_pred):
        # scale predictions so that the class probas of each sample sum to 1
        y_pred /= K.sum(y_pred, axis=-1, keepdims=True)
        # clip to prevent NaN's and Inf's
        y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())
        # calc
        loss = y_true * K.log(y_pred) * weights
        loss = -K.sum(loss, -1)
        return loss

    return loss

def build_model():
    base_model = Xception(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(5, activation='softmax')(x)
    m = Model(inputs=base_model.input, outputs=predictions)
    for layer in base_model.layers:
        layer.trainable = False

    # m.compile(loss=weighted_categorical_crossentropy((1, 6, 6, 13, 13)), optimizer='adam', metrics=['accuracy'])
    m.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

def build_model_scratch():
    base_model = Xception(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(5, activation='softmax')(x)
    m = Model(inputs=base_model.input, outputs=predictions)
    # m.compile(loss=weighted_categorical_crossentropy((1, 6, 6, 13, 13)), optimizer='adam', metrics=['accuracy'])
    m.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return m

def build_model_double(model_save_file):
    double_model = load_model(model_save_file)
    for layer in double_model.layers[-15:]:
        layer.trainable = True
    double_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return double_model