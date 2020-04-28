# -*- coding: utf-8 -*-
"""COVID_VGG19.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Cuhofu8uJkVcbBEbQsdi_4-va_iRrY69
"""

# Mount colab notebook to Google drive
from google.colab import drive
drive.mount('/content/drive/')

## IMPORT PACKAGES AND DEFINE A FEW VARIABLES TO BE USED LATER

# define and move to dataset directory
datasetdir = '/content/drive/My Drive/COVID_DL/in'
import os
os.chdir(datasetdir)

# import the needed packages
import matplotlib.pyplot as plt
import matplotlib.image as img
import tensorflow.keras as keras
import numpy as np

from tensorflow.keras.preprocessing.image import ImageDataGenerator

batch_size = 128

def generators(shape, preprocessing): 
    '''Create the training and validation datasets for 
    a given image shape.
    '''
    imgdatagen = ImageDataGenerator(
        preprocessing_function = preprocessing,
        horizontal_flip = True, 
        validation_split = 0.1,
    )

    height, width = shape

    train_dataset = imgdatagen.flow_from_directory(
        os.getcwd(),
        target_size = (height, width), 
        classes = ('NORMAL','COVID-19','Viral Pneumonia'),
        batch_size = batch_size,
        subset = 'training', 
    )

    val_dataset = imgdatagen.flow_from_directory(
        os.getcwd(),
        target_size = (height, width), 
        classes = ('NORMAL','COVID-19','Viral Pneumonia'),
        batch_size = batch_size,
        subset = 'validation'
    )
    return train_dataset, val_dataset

def plot_history(history, yrange):
    '''Plot loss and accuracy as a function of the epoch,
    for the training and validation datasets.
    '''
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    # Get number of epochs
    epochs = range(len(acc))

    # Plot training and validation accuracy per epoch
    plt.plot(epochs, acc)
    plt.plot(epochs, val_acc)
    plt.title('Training and validation accuracy')
    plt.xlabel("Epoch #")
    plt.ylabel("Accuracy")
    plt.ylim(yrange)
    plt.legend(loc="lower right")
    
    # Plot training and validation loss per epoch
    plt.figure()

    plt.plot(epochs, loss)
    plt.plot(epochs, val_loss)
    plt.title('Training and validation loss')
    plt.xlabel("Epoch #")
    plt.ylabel("Loss")
    plt.legend(loc="lower right")

    plt.show()

"""## FEATURE EXTRACTION WITH MODEL - VGG19"""

vgg19 = keras.applications.vgg19
vgg = vgg19.VGG19(weights='imagenet')
vgg.summary()

vgg19 = keras.applications.vgg19
conv_model = vgg19.VGG19(weights='imagenet', include_top=False)
conv_model.summary()

from keras.preprocessing import image

img_path = '/content/drive/My Drive/COVID_DL/in/NORMAL/NORMAL (1).png'

# loading the image: 
img = image.load_img(img_path, target_size=(224, 224))
# turn it into a numpy array
x = image.img_to_array(img)
print(np.min(x), np.max(x))
print(x.shape)
# expand the shape of the array, 
# a new axis is added at the beginning:
xs = np.expand_dims(x, axis=0)
print(xs.shape)
# preprocess input array for VGG16
xs = vgg19.preprocess_input(xs)
# evaluate the model to extract the features
features = conv_model.predict(xs)
print(features.shape)

train_dataset, val_dataset = generators((224,224), preprocessing=vgg19.preprocess_input)

conv_model = vgg19.VGG19(weights='imagenet', include_top=False, input_shape=(224,224,3))

x = keras.layers.Flatten()(conv_model.output)
# three hidden layers
x = keras.layers.Dense(100, activation='relu')(x)
x = keras.layers.Dense(100, activation='relu')(x)
x = keras.layers.Dense(100, activation='relu')(x)
# final softmax layer with three categories
predictions = keras.layers.Dense(3, activation='softmax')(x)

# creating the full model:
full_model = keras.models.Model(inputs=conv_model.input, outputs=predictions)
full_model.summary()

for layer in conv_model.layers:
    layer.trainable = False

full_model.summary()

full_model.compile(loss='categorical_crossentropy',
                  optimizer=keras.optimizers.Adamax(lr=0.001),
                  metrics=['accuracy'])
history = full_model.fit_generator(
    train_dataset, 
    validation_data = val_dataset,
    steps_per_epoch= train_dataset.samples // batch_size,
    validation_steps= val_dataset.samples // batch_size,
    epochs=5,
)

plot_history(history, yrange=(0.9,1))
plt.savefig("/content/drive/My Drive/COVID_DL/plot1.png")

# Save the model
full_model.save_weights('vgg19.h5')

# Evaluate model accuracy on validation dataset
steps_test = val_dataset.n / batch_size
result = full_model.evaluate(val_dataset, steps=steps_test)

# Calculate the accuracy on test set classification of X-Rays
print("Validation-set classification accuracy: {0:.2%}".format(result[1]))
print("Validation-set classification loss: {0:.2%}".format(result[0]))

# Load the saved model
conv_model = vgg19.VGG19(weights='imagenet', include_top=False, input_shape=(224,224,3))
for layer in conv_model.layers:
    layer.trainable = False
x = keras.layers.Flatten()(conv_model.output)
# three hidden layers
x = keras.layers.Dense(100, activation='relu')(x)
x = keras.layers.Dense(100, activation='relu')(x)
x = keras.layers.Dense(100, activation='relu')(x)
# final softmax layer with three categories 
predictions = keras.layers.Dense(3, activation='softmax')(x)
full_model = keras.models.Model(inputs=conv_model.input, outputs=predictions)

# load weights of saved model
full_model.load_weights('vgg19.h5')

"""### MODEL EVALUATION"""

from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input

img_path = '/content/drive/My Drive/COVID_DL/in/COVID-19/COVID-19 (101).png'
img = image.load_img(img_path, target_size=(224,224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)
print(full_model.predict(x))
plt.imshow(img)



# Evaluate the model on all images in training set
import sys

def true_and_predicted_labels(dataset):
    labels = np.zeros((dataset.n,3))
    preds = np.zeros_like(labels)
    for i in range(len(dataset)):
        sys.stdout.write('evaluating batch {}\r'.format(i))
        sys.stdout.flush()
        batch = dataset[i]
        batch_images = batch[0]
        batch_labels = batch[1]
        batch_preds = full_model.predict(batch_images)
        start = i*batch_size
        labels[start:start+batch_size] = batch_labels
        preds[start:start+batch_size] = batch_preds
    return labels, preds

train_labels, train_preds = true_and_predicted_labels(train_dataset)

def plot_covid_score(preds, labels, range=(0,1)):
    # get the covid score for all images
    covid_score = preds[:,2]
    # get the covid score for other images
    # we use the true labels to select other images
    n_covid_score = covid_score[labels[:,0]>0.5]
    # and for covid
    c_covid_score = covid_score[labels[:,0]<0.5]
    # just some plotting parameters
    params = {'bins':100, 'range':range, 'alpha':0.6}
    plt.hist(n_covid_score, **params)
    plt.hist(c_covid_score, **params)
    plt.yscale('log')

plot_covid_score(train_preds, train_labels)

# For the covid score above we now compute the accuracy
threshold = 0.3

def predicted_labels(preds, threshold):
    '''Turn predictions (floats in the last two dimensions) 
    into labels (0 or 1).'''
    pred_labels = np.zeros_like(preds)
    # covid score lower than threshold: set others label to 1
    # covid score higher than threshold: set others label to 0
    pred_labels[:,0] = preds[:,2]<threshold
    # covid score higher than threshold: set covid label to 1
    # cat score lower than threshold: set covid label to 0
    pred_labels[:,1] = preds[:,2]>=threshold
    return pred_labels

train_pred_labels = predicted_labels(train_preds, threshold)
print('predicted labels:')
print(train_pred_labels)
print('true labels:')
print(train_labels)

# Quantify misclassified examples IN train dataset

def misclassified(labels, pred_labels, print_report=True):
    def report(categ, n_misclassified, n_examples): 
        print('{:<4} {:>3} misclassified samples ({:4.2f}%)'.format(
            categ,
            n_misclassified, 
            100*(1-float(n_misclassified)/n_examples))
        )
    # total number of examples
    n_examples = len(labels)
    # total number of covid
    n_covid = sum(labels[:,0])
    # total number of others
    n_others = sum(labels[:,2])
    # boolean mask for misidentified examples
    mask_all = pred_labels[:,0] != labels[:,0]
    # boolean mask for misidentified covid    
    mask_covid = np.logical_and(mask_all,labels[:,1]>0.5)
    # boolean mask for misidentified others    
    mask_others = np.logical_and(mask_all,labels[:,1]<0.5)
    if print_report:
        report('all', sum(mask_all), n_examples)
        report('covid', sum(mask_covid), n_covid)
        report('other lung images', sum(mask_others), n_others)
    return mask_all, mask_covid, mask_others

_ = misclassified(train_labels, train_pred_labels)

# Quantify misclassified examples in validation dataset

val_labels, val_preds = true_and_predicted_labels(val_dataset)
val_pred_labels = predicted_labels(val_preds, threshold=0.3)
_ = misclassified(val_labels, val_pred_labels)

val_pred_labels = predicted_labels(val_preds, 0.3)
_ = misclassified(val_labels, val_pred_labels)

"""## VIEW SOME MISCLASSIFIED IMAGES"""

import sys

dataset = val_dataset
misclassified_imgs = dict(others=[], covid=[])
for i in range(len(dataset)):
    if i%100: 
        sys.stdout.write('evaluating batch {}\r'.format(i))
        sys.stdout.flush()
    batch = dataset[i]
    batch_images = batch[0]
    batch_labels = batch[1]
    batch_preds = full_model.predict(batch_images)
    batch_pred_labels = predicted_labels(batch_preds, threshold=0.85)
    mask_all, mask_covid, mask_others = misclassified(
        batch_labels, 
        batch_pred_labels,
        print_report=False                                  
    )
    misclassified_imgs['others'].extend(batch_images[mask_others])
    misclassified_imgs['covid'].extend(batch_images[mask_covid])

print([(label, len(imgs)) for label,imgs in misclassified_imgs.items()])

def plot_images(imgs, i):
    ncols, nrows = (5, 2) 
    start = i*ncols*nrows
    fig = plt.figure( figsize=(ncols*5, nrows*5), dpi=50)
    for i, img in enumerate(imgs[start:start+ncols*nrows]):
        plt.subplot(nrows, ncols, i+1)
        plt.imshow(img)
        plt.axis('off')

plot_images(misclassified_imgs['covid'],0)
# These images are really bad with an unclear output

# To tackle the nature of images above let us check the version of keras used here first
import keras_applications
keras_applications.__version__

# Let us undo preprocessing in images and see

def undo_preprocessing(x):
    mean = [103.939, 116.779, 123.68]
    x[..., 0] += mean[0]
    x[..., 1] += mean[1]
    x[..., 2] += mean[2]
    x = x[..., ::-1]

a = np.arange(12).reshape(2,2,3)
print(a)

a[...,::-1]

# Now let's try our unprocessing function on one image
img = misclassified_imgs['covid'][5]
plt.imshow(img)

import copy
new_img = copy.copy(img)
undo_preprocessing(new_img)
plt.imshow(new_img.astype('int'))

# This function created here works as expected and can be applied to the other images now

def plot_images(imgs, i):
    ncols, nrows = (5, 2) 
    start = i*ncols*nrows
    fig = plt.figure( figsize=(ncols*5, nrows*5), dpi=50)
    for i, img in enumerate(imgs[start:start+ncols*nrows]):
        img_unproc = copy.copy(img)
        undo_preprocessing(img_unproc)
        plt.subplot(nrows, ncols, i+1)
        plt.imshow(img_unproc.astype('int'))
        plt.axis('off')

plot_images(misclassified_imgs['covid'],0)

"""## BIBLIOGRAPHY (only for the code)

##### Code adopted from https://thedatafrog.com/en/articles/image-recognition-transfer-learning/

##### Undertsanding the model and the various parameters involved https://www.jeremyjordan.me/evaluating-a-machine-learning-model/

##### Code adopted and modified in some places 
https://colab.research.google.com/github/Hvass-Labs/TensorFlow-Tutorials/blob/master/10_Fine-Tuning.ipynb
"""