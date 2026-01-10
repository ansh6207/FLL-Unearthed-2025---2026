package com.example.artifact_scanner

import android.Manifest
import android.content.ContentValues
import android.content.Context
import android.content.pm.PackageManager
import android.content.res.AssetManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.CloudDownload
import androidx.compose.material.icons.filled.Collections
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Photo
import androidx.compose.material.icons.outlined.HelpOutline
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import coil.compose.AsyncImage
import coil.request.ImageRequest
import java.util.Locale

// Recursive loader for asset images
fun loadAllAssetImagesRecursively(assetManager: AssetManager, path: String): List<String> {
    val result = mutableListOf<String>()
    val supportedExtensions = listOf("jpg", "jpeg", "png", "webp", "bmp", "gif")
    try {
        val files = assetManager.list(path) ?: return emptyList()
        for (file in files) {
            val fullPath = if (path.isEmpty()) file else "$path/$file"
            if (file.contains(".")) {
                if (supportedExtensions.any { file.lowercase().endsWith(it) }) {
                    result.add(fullPath)
                }
            } else {
                result.addAll(loadAllAssetImagesRecursively(assetManager, fullPath))
            }
        }
    } catch (e: Exception) {
        Log.e("AssetLoad", "Failed to load assets from $path", e)
    }
    return result
}

// Save bitmap to MediaStore and get Uri
fun saveImageToMediaStore(context: Context, bitmap: Bitmap): Uri {
    val fileName = "artifact_${System.currentTimeMillis()}.jpg"
    val values = ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, fileName)
        put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/Artifact_Photos")
            put(MediaStore.Images.Media.IS_PENDING, 1)
        }
    }
    val resolver = context.contentResolver
    val uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
        ?: throw RuntimeException("Failed to create new MediaStore record.")
    resolver.openOutputStream(uri)?.use {
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, it)
    }
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        values.clear()
        values.put(MediaStore.Images.Media.IS_PENDING, 0)
        resolver.update(uri, values, null, null)
    }
    return uri
}

// Save new artifact image in MediaStore under Pictures/Artifact_Photos/{label}/
fun saveNewArtifactToMediaStore(context: Context, bitmap: Bitmap, predictedLabel: String): Uri? {
    val resolver = context.contentResolver
    val collection = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
    } else {
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI
    }

    val displayName = "new_artifact_${predictedLabel}_${System.currentTimeMillis()}.jpg"
    val values = ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, displayName)
        put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/Artifact_Photos/$predictedLabel")
            put(MediaStore.Images.Media.IS_PENDING, 1)
        }
    }

    val uri = resolver.insert(collection, values)

    uri?.let {
        resolver.openOutputStream(it)?.use { outStream ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, outStream)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            values.clear()
            values.put(MediaStore.Images.Media.IS_PENDING, 0)
            resolver.update(uri, values, null, null)
        }
    }

    return uri
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                ArtifactScannerApp()
            }
        }
    }
}

@OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)
@Composable
fun ArtifactScannerApp() {
    val context = LocalContext.current
    val classifier = remember { ArtifactClassifier(context) }
    var predictions by remember { mutableStateOf<List<Pair<String, Float>>?>(null) }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (!granted) {
            Toast.makeText(context, "Permission denied – cannot save images.", Toast.LENGTH_SHORT).show()
        }
    }

    LaunchedEffect(Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            context.checkSelfPermission(Manifest.permission.READ_MEDIA_IMAGES)
            != PackageManager.PERMISSION_GRANTED
        ) {
            permissionLauncher.launch(Manifest.permission.READ_MEDIA_IMAGES)
        }
    }

    var selectedScreen by remember { mutableStateOf("home") }
    var savedImageUris by remember { mutableStateOf<List<Uri>>(emptyList()) }
    var selectedImageUri by remember { mutableStateOf<Uri?>(null) }
    var archiveImages by remember { mutableStateOf<List<String>>(emptyList()) }

    fun loadSavedImages() {
        val images = mutableListOf<Uri>()
        val collection = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL)
        } else {
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI
        }
        val projection = arrayOf(MediaStore.Images.Media._ID, MediaStore.Images.Media.RELATIVE_PATH)
        val cursor = context.contentResolver.query(
            collection,
            projection,
            "${MediaStore.Images.Media.RELATIVE_PATH} LIKE ?",
            arrayOf("Pictures/Artifact_Photos%"),
            "${MediaStore.Images.Media.DATE_ADDED} DESC"
        )
        cursor?.use {
            val idCol = it.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
            while (it.moveToNext()) {
                val id = it.getLong(idCol)
                images += Uri.withAppendedPath(collection, id.toString())
            }
        }
        savedImageUris = images
    }

    fun loadArchiveImages(context: Context, folder: String = "filtered_dataset"): List<String> {
        return loadAllAssetImagesRecursively(context.assets, folder)
    }

    LaunchedEffect(selectedScreen) {
        when (selectedScreen) {
            "library" -> loadSavedImages()
            "archive" -> archiveImages = loadArchiveImages(context)
        }
    }

    val takePictureLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.TakePicturePreview()
    ) { bitmap: Bitmap? ->
        bitmap?.let {
            val uri = saveImageToMediaStore(context, it)
            savedImageUris = listOf(uri) + savedImageUris
            predictions = classifier.classify(it)
            Toast.makeText(context, "Image saved and classified!", Toast.LENGTH_SHORT).show()

            val topPrediction = predictions?.maxByOrNull { prediction -> prediction.second }
            topPrediction?.let { (label, confidence) ->
                Log.d("NewArtifact", "Prediction: $label ($confidence)")

                val assetSubfolders = context.assets.list("filtered_dataset")?.toList() ?: emptyList()
                Log.d("NewArtifact", "Asset folders: $assetSubfolders")

                if (!assetSubfolders.contains(label)) {
                    Log.d("NewArtifact", "Saving new artifact with label: $label")
                    saveNewArtifactToMediaStore(context, it, label)
                    Toast.makeText(context, "New artifact added!", Toast.LENGTH_SHORT).show()
                } else {
                    Log.d("NewArtifact", "Artifact already exists in dataset. Not saving.")
                }
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Artifact Scanner") },
                actions = {
                    IconButton(onClick = { selectedScreen = "help" }) {
                        Icon(Icons.Outlined.HelpOutline, contentDescription = "Help")
                    }
                }
            )
        },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = selectedScreen == "home",
                    onClick = { selectedScreen = "home" },
                    icon = { Icon(Icons.Filled.Home, contentDescription = "Home") },
                    label = { Text("Home") }
                )
                NavigationBarItem(
                    selected = selectedScreen == "library",
                    onClick = { selectedScreen = "library" },
                    icon = { Icon(Icons.Filled.Photo, contentDescription = "Library") },
                    label = { Text("Library") }
                )
                NavigationBarItem(
                    selected = selectedScreen == "archive",
                    onClick = { selectedScreen = "archive" },
                    icon = { Icon(Icons.Filled.Collections, contentDescription = "Archive") },
                    label = { Text("Browse") }
                )
                NavigationBarItem(
                    selected = selectedScreen == "new_artifacts",
                    onClick = { selectedScreen = "new_artifacts" },
                    icon = { Icon(Icons.Filled.CloudDownload, contentDescription = "New Artifacts") },
                    label = { Text("New Artifacts") }
                )
            }
        }
    ) { innerPadding ->
        Column(
            Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .padding(16.dp)
        ) {
            when (selectedScreen) {
                "home" -> {
                    Text("Artifact Scanner", style = MaterialTheme.typography.headlineMedium)
                    Spacer(Modifier.height(24.dp))
                    Button(
                        onClick = { takePictureLauncher.launch(null) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Take Photo")
                    }
                    predictions?.let { predictionList ->
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Top Predictions:", style = MaterialTheme.typography.titleMedium)
                        Spacer(modifier = Modifier.height(8.dp))
                        for ((label, confidence) in predictionList) {
                            Text("• $label (${String.format(Locale.US, "%.1f", confidence * 100)}%)")
                        }
                    }
                }
                "library" -> {
                    Text("Artifact Library", style = MaterialTheme.typography.titleLarge)
                    Spacer(Modifier.height(8.dp))
                    if (savedImageUris.isEmpty()) {
                        Text("No images saved yet.")
                    } else {
                        LazyVerticalGrid(
                            columns = GridCells.Adaptive(minSize = 120.dp),
                            modifier = Modifier.fillMaxSize()
                        ) {
                            items(savedImageUris) { uri ->
                                val thumb = remember(uri) {
                                    context.contentResolver.openInputStream(uri)?.use {
                                        BitmapFactory.decodeStream(it)
                                    }
                                }
                                thumb?.let {
                                    Image(
                                        bitmap = it.asImageBitmap(),
                                        contentDescription = null,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .aspectRatio(1f)
                                            .padding(4.dp)
                                            .clickable { selectedImageUri = uri }
                                    )
                                }
                            }
                        }
                    }
                }
                "archive" -> {
                    val pageSize = 200
                    val currentPage = remember { mutableIntStateOf(0) }
                    val selectedImage = remember { mutableStateOf<String?>(null) }
                    val pagedImages = archiveImages.take((currentPage.intValue + 1) * pageSize)
                    Box {
                        LazyVerticalGrid(
                            columns = GridCells.Adaptive(minSize = 120.dp),
                            contentPadding = PaddingValues(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            modifier = Modifier.fillMaxSize()
                        ) {
                            items(pagedImages) { assetPath ->
                                AsyncImage(
                                    model = ImageRequest.Builder(context)
                                        .data("file:///android_asset/$assetPath")
                                        .crossfade(true)
                                        .build(),
                                    contentDescription = null,
                                    contentScale = ContentScale.Crop,
                                    modifier = Modifier
                                        .aspectRatio(1f)
                                        .clickable { selectedImage.value = assetPath }
                                )
                            }
                            item {
                                if (pagedImages.size < archiveImages.size) {
                                    Button(
                                        onClick = { currentPage.intValue++ },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(8.dp)
                                    ) {
                                        Text("Load More")
                                    }
                                }
                            }
                        }
                        selectedImage.value?.let { imagePath ->
                            Dialog(onDismissRequest = { selectedImage.value = null }) {
                                Box(
                                    modifier = Modifier
                                        .fillMaxSize()
                                        .clickable { selectedImage.value = null }
                                        .background(Color.Black)
                                ) {
                                    AsyncImage(
                                        model = ImageRequest.Builder(context)
                                            .data("file:///android_asset/$imagePath")
                                            .crossfade(true)
                                            .build(),
                                        contentDescription = null,
                                        contentScale = ContentScale.Fit,
                                        modifier = Modifier
                                            .fillMaxSize()
                                            .padding(16.dp)
                                    )
                                }
                            }
                        }
                    }
                }
                "new_artifacts" -> {
                    NewArtifactGallery(selectedScreen)
                }

                "help" -> {
                    HelpScreen()
                }
            }
            selectedImageUri?.let { uri ->
                AlertDialog(
                    onDismissRequest = { selectedImageUri = null },
                    confirmButton = {},
                    dismissButton = {
                        TextButton(onClick = {
                            context.contentResolver.delete(uri, null, null)
                            savedImageUris = savedImageUris.filter { it != uri }
                            selectedImageUri = null
                        }) { Text("Delete") }
                    },
                    title = { Text("Artifact Image") },
                    text = {
                        val full = remember(uri) {
                            context.contentResolver.openInputStream(uri)?.use {
                                BitmapFactory.decodeStream(it)
                            }
                        }
                        full?.let {
                            Image(
                                bitmap = it.asImageBitmap(),
                                contentDescription = null,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .aspectRatio(it.width.toFloat() / it.height)
                            )
                        }
                    }
                )
            }
        }
    }
}

// Load new artifact images from MediaStore under Pictures/Artifact_Photos
fun loadNewArtifactImagesFromMediaStore(context: Context): List<Uri> {
    val uris = mutableListOf<Uri>()
    val collection = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL)
    } else {
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI
    }
    val projection = arrayOf(MediaStore.Images.Media._ID, MediaStore.Images.Media.RELATIVE_PATH)
    val selection = "${MediaStore.Images.Media.RELATIVE_PATH} LIKE ?"
    val selectionArgs = arrayOf("Pictures/Artifact_Photos/%")
    val sortOrder = "${MediaStore.Images.Media.DATE_ADDED} DESC"

    context.contentResolver.query(collection, projection, selection, selectionArgs, sortOrder)?.use { cursor ->
        val idCol = cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
        while (cursor.moveToNext()) {
            val id = cursor.getLong(idCol)
            val uri = Uri.withAppendedPath(collection, id.toString())
            uris.add(uri)
        }
    }

    return uris
}

@Composable
fun NewArtifactGallery(selectedScreen: String) {
    val context = LocalContext.current
    var newArtifactUris by remember { mutableStateOf(listOf<Uri>()) }

    LaunchedEffect(selectedScreen) {
        if (selectedScreen == "new_artifacts") {
            newArtifactUris = loadNewArtifactImagesFromMediaStore(context)
            Log.d("NewArtifact", "Loaded ${newArtifactUris.size} new artifact images")
        }
    }

    if (newArtifactUris.isEmpty()) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("No new artifacts found.")
        }
    } else {
        LazyVerticalGrid(columns = GridCells.Adaptive(128.dp)) {
            items(newArtifactUris) { uri ->
                AsyncImage(
                    model = uri,
                    contentDescription = null,
                    modifier = Modifier
                        .padding(4.dp)
                        .size(128.dp)
                        .clip(RoundedCornerShape(8.dp)),
                    contentScale = ContentScale.Crop
                )
            }
        }
    }
}

@Composable
fun HelpScreen() {
    val scrollState = rememberScrollState()
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp)
    ) {
        Text("How to Use Artifact Scanner", style = MaterialTheme.typography.headlineMedium)

        Spacer(Modifier.height(16.dp))

        HelpCard(
            title = "Take a Picture",
            description = "Tap the camera icon to scan a new artifact.",
            icon = Icons.Filled.CameraAlt
        )

        HelpCard(
            title = "View Saved Artifacts",
            description = "Go to the Library tab to see your saved images.",
            icon = Icons.Filled.Photo
        )

        HelpCard(
            title = "Browse Archive",
            description = "Open the Browse tab to explore the Smithsonian Archive images.",
            icon = Icons.Filled.Collections
        )

        HelpCard(
            title = "New Artifacts",
            description = "Check the New Artifacts tab to see recently discovered artifacts.",
            icon = Icons.Filled.CloudDownload
        )

        HelpCard(
            title = "More Info",
            description = "Tap the help icon anytime for guidance.",
            icon = Icons.Filled.Info
        )
    }
}

@Composable
fun HelpCard(title: String, description: String, icon: ImageVector) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        elevation = CardDefaults.cardElevation()
    ) {
        Row(modifier = Modifier.padding(16.dp)) {
            Icon(icon, contentDescription = title, modifier = Modifier.size(40.dp))
            Spacer(Modifier.width(16.dp))
            Column {
                Text(title, style = MaterialTheme.typography.titleMedium)
                Text(description, style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}