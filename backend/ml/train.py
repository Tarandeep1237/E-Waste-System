import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os
import logging

logger = logging.getLogger(__name__)

# E-Waste Categories mapped for the model
CATEGORIES = [
    'Smartphone', 
    'Laptop', 
    'Keyboard/Mouse', 
    'Cables/Wires', 
    'Battery', 
    'Display/Monitor', 
    'Printer/Scanner'
]

def build_model(num_classes=len(CATEGORIES)):
    """
    Build a fine-tuned MobileNetV2 model for E-Waste classification.
    """
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    # Freeze the base model
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(optimizer=Adam(learning_rate=0.001), 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])
    return model

def train_model(dataset_path, epochs=10, batch_size=32):
    """
    Train the model using the provided dataset path.
    Assumes dataset is organized as: dataset_path/category_name/images.jpg
    """
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset path {dataset_path} does not exist.")
        return

    # Image augmentation & preprocessing
    datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )

    train_generator = datagen.flow_from_directory(
        dataset_path,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='training'
    )

    val_generator = datagen.flow_from_directory(
        dataset_path,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation'
    )

    model = build_model(num_classes=train_generator.num_classes)
    
    logger.info("Starting training...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=epochs
    )

    # Save the model
    os.makedirs('saved_models', exist_ok=True)
    model.save('saved_models/ewaste_mobilenetv2.h5')
    logger.info("Model saved to saved_models/ewaste_mobilenetv2.h5")

if __name__ == '__main__':
    # To train, uncomment and provide path
    # train_model('path/to/dataset')
    pass
