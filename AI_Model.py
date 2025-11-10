import tensorflow as tf
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# === CONFIG ===
dataset_dir = "filtered_dataset"
img_height, img_width = 180, 180
batch_size = 32
model_dir = "artifact_model"
tflite_model_path = "artifact_model.tflite"
label_file = "labels.txt"

# === Load datasets ===
raw_train_ds = tf.keras.utils.image_dataset_from_directory(
    dataset_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
    label_mode="categorical"
)

raw_val_ds = tf.keras.utils.image_dataset_from_directory(
    dataset_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
    label_mode="categorical"
)

# Extract class names BEFORE caching
class_names = raw_train_ds.class_names
num_classes = len(class_names)

# Cache, shuffle, prefetch
AUTOTUNE = tf.data.AUTOTUNE
train_ds = raw_train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = raw_val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# === Define model ===
model = tf.keras.Sequential([
    tf.keras.layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(128, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# === Train model ===
history = model.fit(train_ds, validation_data=val_ds, epochs=10)

# === Export SavedModel for TFLite ===
model.export(model_dir)

# === Convert to TensorFlow Lite ===
converter = tf.lite.TFLiteConverter.from_saved_model(model_dir)
tflite_model = converter.convert()
with open(tflite_model_path, "wb") as f:
    f.write(tflite_model)

# === Save class names to labels.txt ===
with open(label_file, "w") as f:
    for label in class_names:
        f.write(label + "\n")

# === Plot training history (optional) ===
plt.plot(history.history['accuracy'], label='train_acc')
plt.plot(history.history['val_accuracy'], label='val_acc')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Training History')
plt.legend()
plt.savefig("training_history.png")
plt.close()

print("✅ Training complete. Model exported to:")
print(f"  - {tflite_model_path}")
print(f"  - {label_file}")
print(f"  - Training graph: training_history.png")
