package com.example.artifact_scanner

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
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

        // Load the TFLite model
        val model = loadModelFile(context, "artifact_model.tflite")
        interpreter = Interpreter(model)

        // Load labels
        labels = assetManager.open("labels.txt")
            .bufferedReader()
            .readLines()
    }

    fun classify(image: Bitmap): List<Pair<String, Float>> {
        val input = preprocessImage(image)
        val output = Array(1) { FloatArray(labels.size) }

        interpreter.run(input, output)

        val probs = output[0]
        return probs
            .mapIndexed { i, prob -> labels[i] to prob }
            .sortedByDescending { it.second }
            .take(5) // top 5
    }

    private fun preprocessImage(bitmap: Bitmap): ByteBuffer {
        val inputSize = 224
        val resized = Bitmap.createScaledBitmap(bitmap, inputSize, inputSize, true)

        val byteBuffer = ByteBuffer.allocateDirect(4 * inputSize * inputSize * 3)
        byteBuffer.order(ByteOrder.nativeOrder())

        for (y in 0 until inputSize) {
            for (x in 0 until inputSize) {
                val pixel = resized.getPixel(x, y)
                byteBuffer.putFloat((pixel shr 16 and 0xFF) / 255f) // R
                byteBuffer.putFloat((pixel shr 8 and 0xFF) / 255f)  // G
                byteBuffer.putFloat((pixel and 0xFF) / 255f)       // B
            }
        }

        return byteBuffer
    }

    private fun loadModelFile(context: Context, fileName: String): ByteBuffer {
        val fileDescriptor = context.assets.openFd(fileName)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }
}