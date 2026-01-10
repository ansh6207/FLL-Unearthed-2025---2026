import tensorflow as tf
import numpy as np
from PIL import Image

tflite_model_path = "artifact_model.tflite"
labels_path = "labels.txt"
test_image_path = "test.jpg"

# Load labels
with open(labels_path, "r") as f:
    class_names = [line.strip() for line in f if line.strip()]

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()

# Read model I/O details
input_details = interpreter.get_input_details()[0]
output_details = interpreter.get_output_details()[0]
h, w = input_details["shape"][1:3]
dtype = input_details["dtype"]

# Prepare image matching model input size
img = Image.open(test_image_path).convert("RGB").resize((w, h))
img_array = np.array(img).astype(np.float32) / 255.0
input_data = np.expand_dims(img_array, axis=0)

# Adjust dtype/quantization if required (e.g., for uint8 models)
if dtype != np.float32:
    scale, zero_point = input_details.get("quantization", (0.0, 0))
    if scale and scale > 0:
        input_data = (input_data / scale + zero_point).astype(dtype)
    else:
        input_data = input_data.astype(dtype)

# Run inference
input_index = input_details["index"]
output_index = output_details["index"]
interpreter.set_tensor(input_index, input_data)
interpreter.invoke()
output = interpreter.get_tensor(output_index)[0]

# Show top-3 predictions
top_k = np.argsort(output)[::-1][:3]
print("\nPrediction Results:")
for i in top_k:
    label = class_names[i] if i < len(class_names) else f"class_{i}"
    confidence = float(output[i])
    print(f"- {label} ({confidence:.2f})")

if output[top_k[0]] < 0.5:
    print("\nLow confidence in prediction. Try another image or angle.")