package com.example.artifact_scanner

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.DataType
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel
import kotlin.math.min

class ArtifactClassifier(context: Context) {
    private val interpreter: Interpreter
    private val labels: List<String>

    init {
        val assetManager = context.assets

        // Load TFLite model from assets
        val model = loadModelFile(context, "artifact_model.tflite")
        interpreter = Interpreter(model)

        // Load label list from assets
        labels = assetManager.open("labels.txt")
            .bufferedReader()
            .readLines()
            .filter { it.isNotBlank() }
    }

    fun classify(image: Bitmap): List<Pair<String, Float>> {
        // Prepare model input
        val inputBuffer = preprocessImage(image)

        // Detect model output shape dynamically
        val outputTensor = interpreter.getOutputTensor(0)
        val outputShape = outputTensor.shape() // [1, num_classes]
        val numClasses = outputShape[1]
        val output = Array(1) { FloatArray(numClasses) }

        // Run inference safely
        interpreter.run(inputBuffer, output)

        val probs = output[0]
        val count = min(labels.size, probs.size)
        val result = mutableListOf<Pair<String, Float>>()

        for (i in 0 until count) {
            result += labels[i] to probs[i]
        }

        return result
            .sortedByDescending { it.second }
            .take(5) // Top 5 predictions
    }

    /**
     * Preprocess image dynamically depending on model input type (FLOAT32 or UINT8)
     */
    private fun preprocessImage(bitmap: Bitmap): ByteBuffer {
        val inputTensor = interpreter.getInputTensor(0)
        val shape = inputTensor.shape() // e.g. [1, 224, 224, 3]
        val dataType = inputTensor.dataType()
        val inputSize = shape[1] // assuming square input

        val resized = Bitmap.createScaledBitmap(bitmap, inputSize, inputSize, true)

        return if (dataType == DataType.FLOAT32) {
            // Float32 model
            val byteBuffer = ByteBuffer.allocateDirect(4 * inputSize * inputSize * 3)
            byteBuffer.order(ByteOrder.nativeOrder())

            for (y in 0 until inputSize) {
                for (x in 0 until inputSize) {
                    val pixel = resized.getPixel(x, y)
                    byteBuffer.putFloat((pixel shr 16 and 0xFF) / 255f)
                    byteBuffer.putFloat((pixel shr 8 and 0xFF) / 255f)
                    byteBuffer.putFloat((pixel and 0xFF) / 255f)
                }
            }
            byteBuffer
        } else {
            // Quantized UINT8 model
            val byteBuffer = ByteBuffer.allocateDirect(inputSize * inputSize * 3)
            byteBuffer.order(ByteOrder.nativeOrder())

            for (y in 0 until inputSize) {
                for (x in 0 until inputSize) {
                    val pixel = resized.getPixel(x, y)
                    byteBuffer.put((pixel shr 16 and 0xFF).toByte())
                    byteBuffer.put((pixel shr 8 and 0xFF).toByte())
                    byteBuffer.put((pixel and 0xFF).toByte())
                }
            }
            byteBuffer
        }
    }

    /**
     * Load the .tflite model file from assets
     */
    private fun loadModelFile(context: Context, fileName: String): ByteBuffer {
        val fileDescriptor = context.assets.openFd(fileName)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }
}