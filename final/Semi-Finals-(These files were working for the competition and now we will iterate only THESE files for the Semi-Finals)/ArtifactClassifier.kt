package com.example.artifact_scanner

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import ai.onnxruntime.*
import java.nio.FloatBuffer

data class HeadPrediction(
    val head: String,
    val label: String,
    val confidence: Float
)

class ArtifactClassifier(context: Context) {

    private val env: OrtEnvironment = OrtEnvironment.getEnvironment()
    private val session: OrtSession

    // Model expects 160×160 ImageNet preprocessed tensors
    private val inputWidth = 160
    private val inputHeight = 160

    private val mean = floatArrayOf(0.485f, 0.456f, 0.406f)
    private val std = floatArrayOf(0.229f, 0.224f, 0.225f)

    // Minimum probability for known labels
    private val unknownThreshold = 0.40f

    /**
     * ONNX outputs in this exact order:
     * 1. output_Culture
     * 2. output_Materials
     * 3. output_Production date
     * 4. output_region
     * 5. output_Object type
     *
     * Your final filenames (underscore versions):
     * Culture.txt
     * Materials.txt
     * Production_date.txt
     * region.txt
     * Object_type.txt
     */
    private val headNames = listOf(
        "Culture",
        "Materials",
        "Production_date",
        "region",
        "Object_type"
    )

    private val labelsPerHead: Map<String, List<String>>

    init {
        val modelBytes = context.assets.open("model.onnx").readBytes()
        session = env.createSession(modelBytes)

        // Load label files
        val temp = mutableMapOf<String, List<String>>()

        for (head in headNames) {
            val filename = "labels/${head}.txt"
            try {
                val list = context.assets.open(filename)
                    .bufferedReader()
                    .readLines()

                temp[head] = list
            } catch (e: Exception) {
                Log.e("ArtifactClassifier", "Missing label file: $filename", e)
                temp[head] = emptyList()
            }
        }

        labelsPerHead = temp
    }

    fun classify(bitmap: Bitmap): List<HeadPrediction> {
        val resized = Bitmap.createScaledBitmap(bitmap, inputWidth, inputHeight, true)
        val inputData = preprocess(resized)

        val inputName = session.inputNames.first()

        // Convert FloatArray → FloatBuffer (required by ONNX Runtime)
        val floatBuffer = FloatBuffer.wrap(inputData)

        val inputTensor = OnnxTensor.createTensor(
            env,
            floatBuffer,
            longArrayOf(1, 3, inputHeight.toLong(), inputWidth.toLong())
        )

        inputTensor.use { tensor ->
            val results = session.run(mapOf(inputName to tensor))
            val predictions = mutableListOf<HeadPrediction>()

            for (i in headNames.indices) {
                val head = headNames[i]
                val labels = labelsPerHead[head] ?: emptyList()

                val raw = results[i].value
                val logits: FloatArray = when (raw) {
                    is Array<*> -> (raw as Array<FloatArray>)[0]
                    is FloatArray -> raw
                    else -> continue
                }

                val probs = softmax(logits)
                val maxIndex = probs.indices.maxByOrNull { probs[it] } ?: 0
                val confidence = probs[maxIndex]

                val label =
                    if (confidence < unknownThreshold) "Unknown"
                    else labels.getOrNull(maxIndex) ?: "Unknown"

                predictions += HeadPrediction(head, label, confidence)
            }

            return predictions
        }
    }

    // Preprocess bitmap → normalized CHW float array
    private fun preprocess(bitmap: Bitmap): FloatArray {
        val out = FloatArray(3 * inputWidth * inputHeight)
        val plane = inputWidth * inputHeight

        for (y in 0 until inputHeight) {
            for (x in 0 until inputWidth) {
                val pixel = bitmap.getPixel(x, y)

                var r = ((pixel shr 16) and 0xFF) / 255f
                var g = ((pixel shr 8) and 0xFF) / 255f
                var b = (pixel and 0xFF) / 255f

                r = (r - mean[0]) / std[0]
                g = (g - mean[1]) / std[1]
                b = (b - mean[2]) / std[2]

                val idx = y * inputWidth + x

                out[idx] = r
                out[idx + plane] = g
                out[idx + 2 * plane] = b
            }
        }

        return out
    }

    private fun softmax(logits: FloatArray): FloatArray {
        val max = logits.maxOrNull() ?: 0f
        val exps = logits.map { Math.exp((it - max).toDouble()) }
        val sum = exps.sum()

        return FloatArray(logits.size) { i ->
            (exps[i] / sum).toFloat()
        }
    }
}