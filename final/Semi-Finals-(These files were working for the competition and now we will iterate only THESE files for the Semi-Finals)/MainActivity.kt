@file:Suppress("DefaultLocale", "SpellCheckingInspection")
package com.example.artifact_scanner

import android.Manifest
import android.content.ContentValues
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import coil.compose.AsyncImage
import coil.request.ImageRequest
import androidx.compose.material.icons.automirrored.outlined.HelpOutline
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.ChatBubbleOutline

//----------------------------------------------------
// Recursive asset loader
//----------------------------------------------------
fun loadAllAssetImagesRecursively(context: Context, path: String): List<String> {
    val result = mutableListOf<String>()
    val supported = listOf("jpg", "jpeg", "png", "webp", "bmp", "gif")
    val list = context.assets.list(path) ?: return emptyList()

    for (file in list) {
        val full = if (path.isEmpty()) file else "$path/$file"
        if (file.contains(".")) {
            if (supported.any { file.lowercase().endsWith(it) }) result.add(full)
        } else {
            result.addAll(loadAllAssetImagesRecursively(context, full))
        }
    }
    return result
}

//----------------------------------------------------
// Save NEW artifact into folder (ONLY saving function)
//----------------------------------------------------
fun saveNewArtifactToMediaStore(context: Context, bitmap: Bitmap, label: String): Uri? {
    val collection =
        if (Build.VERSION.SDK_INT >= 29)
            MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
        else MediaStore.Images.Media.EXTERNAL_CONTENT_URI

    val fileName = "artifact_${label}_${System.currentTimeMillis()}.jpg"

    val values = ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, fileName)
        put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
        if (Build.VERSION.SDK_INT >= 29) {
            put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/Artifact_Photos/$label")
            put(MediaStore.Images.Media.IS_PENDING, 1)
        }
    }

    val resolver = context.contentResolver
    val uri = resolver.insert(collection, values)

    uri?.let {
        resolver.openOutputStream(it)?.use { stream ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, stream)
        }
        if (Build.VERSION.SDK_INT >= 29) {
            values.clear()
            values.put(MediaStore.Images.Media.IS_PENDING, 0)
            resolver.update(uri, values, null, null)
        }
    }

    return uri
}

//----------------------------------------------------
// Load newly added artifacts
//----------------------------------------------------
fun loadNewArtifactImagesFromMediaStore(context: Context): List<Uri> {
    val result = mutableListOf<Uri>()
    val collection =
        if (Build.VERSION.SDK_INT >= 29)
            MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL)
        else MediaStore.Images.Media.EXTERNAL_CONTENT_URI

    val projection = arrayOf(MediaStore.Images.Media._ID)

    val cursor = context.contentResolver.query(
        collection,
        projection,
        "${MediaStore.Images.Media.RELATIVE_PATH} LIKE ?",
        arrayOf("Pictures/Artifact_Photos/%"),
        "${MediaStore.Images.Media.DATE_ADDED} DESC"
    )

    cursor?.use {
        val idCol = it.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
        while (it.moveToNext()) {
            val id = it.getLong(idCol)
            result += Uri.withAppendedPath(collection, id.toString())
        }
    }

    return result
}

//----------------------------------------------------
// MAIN ACTIVITY
//----------------------------------------------------
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

//----------------------------------------------------
// ROOT COMPOSABLE
//----------------------------------------------------
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ArtifactScannerApp() {
    val context = LocalContext.current
    val classifier = remember { ArtifactClassifier(context) }

    var predictions by remember { mutableStateOf<List<HeadPrediction>?>(null) }
    var selectedScreen by remember { mutableStateOf("home") }
    var savedImageUris by remember { mutableStateOf<List<Uri>>(emptyList()) }
    var selectedImageUri by remember { mutableStateOf<Uri?>(null) }
    var archiveImages by remember { mutableStateOf<List<String>>(emptyList()) }
    var showLibraryPicker by remember { mutableStateOf(false) }
    var predictionsByUri by remember {
        mutableStateOf<Map<Uri, List<HeadPrediction>>>(emptyMap())
    }
    var lastPredictions by remember {
        mutableStateOf<List<HeadPrediction>>(emptyList())
    }
    // Expert chat state (ADD-ONLY)
    var expertChatMessages by remember {
        mutableStateOf<List<ExpertChatMessage>>(emptyList())
    }

    //------------------------------------------------
    // Permissions
    //------------------------------------------------
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) {
        if (!it) Toast.makeText(context, "Permission denied.", Toast.LENGTH_SHORT).show()
    }

    LaunchedEffect(Unit) {
        if (Build.VERSION.SDK_INT >= 33 &&
            context.checkSelfPermission(Manifest.permission.READ_MEDIA_IMAGES)
            != PackageManager.PERMISSION_GRANTED
        ) {
            permissionLauncher.launch(Manifest.permission.READ_MEDIA_IMAGES)
        }
    }

    //------------------------------------------------
    // FIXED TAKE-PICTURE LAUNCHER WITH NO DUPLICATES
    //------------------------------------------------
    val takePictureLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.TakePicturePreview()
    ) { bitmap ->
        bitmap?.let { bmp ->

            // 1. Classify first
            predictions = classifier.classify(bmp)
            lastPredictions = predictions ?: emptyList()

            // 2. Extract culture
            val culture = predictions?.firstOrNull { it.head == "Culture" }
            val predictedLabel = culture?.label ?: "Unknown"

            // 3. Validate label exists in dataset
            val datasetFolders = context.assets.list("filtered_dataset")?.toList() ?: emptyList()
            val finalLabel =
                if (predictedLabel == "Unknown" || !datasetFolders.contains(predictedLabel))
                    "Unknown"
                else predictedLabel

            // 4. Save ONCE into the correct folder
            val savedUri = saveNewArtifactToMediaStore(context, bmp, finalLabel)
            savedUri?.let {
                predictionsByUri = predictionsByUri + (it to lastPredictions)
            }

            savedUri?.let {
                savedImageUris = listOf(it) + savedImageUris
                Toast.makeText(
                    context,
                    "Saved to Artifact_Photos/$finalLabel",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    fun formatPredictions(preds: List<HeadPrediction>): String {
        if (preds.isEmpty()) return "No AI predictions available."

        return buildString {
            append("AI Predictions:\n")
            preds.forEach {
                append("${it.head.replace("_", " ")}: ")
                append("${it.label} (${(it.confidence * 100).toInt()}%)\n")
            }
        }
    }

    //------------------------------------------------
    // Load saved images helper
    //------------------------------------------------
    fun loadSavedImages() {
        val list = mutableListOf<Uri>()
        val collection =
            if (Build.VERSION.SDK_INT >= 29)
                MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL)
            else MediaStore.Images.Media.EXTERNAL_CONTENT_URI

        val projection = arrayOf(MediaStore.Images.Media._ID)

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
                list += Uri.withAppendedPath(collection, id.toString())
            }
        }

        savedImageUris = list
    }

    //------------------------------------------------
    // Load archive
    //------------------------------------------------
    fun loadArchiveImagesNow() {
        archiveImages = loadAllAssetImagesRecursively(context, "filtered_dataset")
    }

    //------------------------------------------------
    // Screen switch logic
    //------------------------------------------------
    LaunchedEffect(selectedScreen) {
        when (selectedScreen) {
            "library" -> loadSavedImages()
            "archive" -> loadArchiveImagesNow()
        }
    }

    //------------------------------------------------
    // UI
    //------------------------------------------------
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Artifact Scanner") },
                actions = {
                    IconButton(onClick = { selectedScreen = "help" }) {
                        Icon(Icons.AutoMirrored.Outlined.HelpOutline, null)
                    }
                }
            )
        },

        floatingActionButton = {
            if (selectedScreen != "expert_chat") {
                FloatingActionButton(
                    onClick = { selectedScreen = "expert_chat" }
                ) {
                    Icon(Icons.Filled.ChatBubbleOutline, contentDescription = "Ask Expert")
                }
            }
        },

        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = selectedScreen == "home",
                    onClick = { selectedScreen = "home" },
                    icon = { Icon(Icons.Filled.Home, null) },
                    label = { Text("Home") }
                )
                NavigationBarItem(
                    selected = selectedScreen == "library",
                    onClick = { selectedScreen = "library" },
                    icon = { Icon(Icons.Filled.Photo, null) },
                    label = { Text("Library") }
                )
                NavigationBarItem(
                    selected = selectedScreen == "archive",
                    onClick = { selectedScreen = "archive" },
                    icon = { Icon(Icons.Filled.Collections, null) },
                    label = { Text("Browse") }
                )
                NavigationBarItem(
                    selected = selectedScreen == "new_artifacts",
                    onClick = { selectedScreen = "new_artifacts" },
                    icon = { Icon(Icons.Filled.CloudDownload, null) },
                    label = { Text("New") }
                )
            }
        }
    ) { pad ->

        Column(
            modifier = Modifier
                .padding(pad)
                .fillMaxSize()
                .padding(16.dp)
        ) {

            when (selectedScreen) {

                //------------------------------------------------
                // HOME
                //------------------------------------------------
                "home" -> {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(8.dp)
                    ) {

                        Text(
                            "Artifact Scanner",
                            style = MaterialTheme.typography.headlineLarge,
                            modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)
                        )

                        Text(
                            "Scan an artifact and let the AI determine culture, materials, age, region, and type.",
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.padding(bottom = 20.dp),
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )

                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { takePictureLauncher.launch(null) },
                            shape = RoundedCornerShape(20.dp),
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.primaryContainer
                            ),
                            elevation = CardDefaults.cardElevation(5.dp)
                        ) {
                            Row(
                                modifier = Modifier.padding(24.dp).fillMaxWidth(),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    Icons.Filled.CameraAlt,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.primary,
                                    modifier = Modifier.size(40.dp)
                                )
                                Spacer(Modifier.width(20.dp))
                                Column {
                                    Text(
                                        "Scan Artifact",
                                        style = MaterialTheme.typography.titleLarge,
                                        color = MaterialTheme.colorScheme.primary
                                    )
                                    Text(
                                        "Take a photo to start analysis",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        }

                        Spacer(Modifier.height(20.dp))

                        predictions?.let { preds ->
                            Text(
                                "Analysis Results",
                                style = MaterialTheme.typography.titleLarge,
                                modifier = Modifier.padding(bottom = 12.dp)
                            )

                            LazyColumn(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .weight(1f),
                                verticalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                items(preds) { p ->
                                    Card(
                                        shape = RoundedCornerShape(16.dp),
                                        colors = CardDefaults.cardColors(
                                            containerColor = MaterialTheme.colorScheme.surfaceVariant
                                        ),
                                        elevation = CardDefaults.cardElevation(2.dp),
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        Row(
                                            modifier = Modifier
                                                .padding(16.dp)
                                                .fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween,
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Column {
                                                Text(
                                                    p.head.replace("_", " "),
                                                    style = MaterialTheme.typography.titleMedium
                                                )
                                                Text(
                                                    p.label,
                                                    style = MaterialTheme.typography.bodyLarge,
                                                    color =
                                                        if (p.label == "Unknown")
                                                            MaterialTheme.colorScheme.error
                                                        else
                                                            MaterialTheme.colorScheme.onSurfaceVariant
                                                )
                                            }

                                            Surface(
                                                shape = RoundedCornerShape(12.dp),
                                                color = MaterialTheme.colorScheme.primaryContainer
                                            ) {
                                                Text(
                                                    "${String.format(java.util.Locale.US, "%.1f", p.confidence * 100)}%",
                                                    modifier = Modifier.padding(
                                                        horizontal = 12.dp,
                                                        vertical = 6.dp
                                                    ),
                                                    style = MaterialTheme.typography.bodyMedium,
                                                    color = MaterialTheme.colorScheme.primary
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                //------------------------------------------------
                // LIBRARY
                //------------------------------------------------
                "library" -> {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(horizontal = 12.dp)
                    ) {
                        Text(
                            "Saved Artifacts",
                            style = MaterialTheme.typography.headlineMedium,
                            modifier = Modifier.padding(vertical = 12.dp)
                        )

                        if (savedImageUris.isEmpty()) {
                            Text(
                                "No saved images yet.",
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        } else {
                            LazyVerticalGrid(
                                columns = GridCells.Adaptive(130.dp),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp),
                                modifier = Modifier.fillMaxSize()
                            ) {
                                items(savedImageUris) { uri ->
                                    Card(
                                        modifier = Modifier
                                            .aspectRatio(1f)
                                            .clickable { selectedImageUri = uri },
                                        shape = RoundedCornerShape(16.dp),
                                        elevation = CardDefaults.cardElevation(3.dp)
                                    ) {
                                        val bmp =
                                            remember(uri) {
                                                context.contentResolver.openInputStream(uri)
                                                    ?.use {
                                                        BitmapFactory.decodeStream(it)
                                                    }
                                            }
                                        bmp?.let {
                                            Image(
                                                bitmap = it.asImageBitmap(),
                                                contentDescription = null,
                                                modifier = Modifier.fillMaxSize(),
                                                contentScale = ContentScale.Crop
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                //------------------------------------------------
                // ARCHIVE
                //------------------------------------------------
                "archive" -> {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(horizontal = 12.dp)
                    ) {
                        Text(
                            "Browse Archive",
                            style = MaterialTheme.typography.headlineMedium,
                            modifier = Modifier.padding(vertical = 12.dp)
                        )

                        val pageSize = 200
                        val page = remember { mutableStateOf(0) }
                        val selectedImage = remember { mutableStateOf<String?>(null) }

                        val visible =
                            archiveImages.take((page.value + 1) * pageSize)

                        LazyVerticalGrid(
                            columns = GridCells.Adaptive(140.dp),
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(bottom = 80.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(visible) { assetPath ->
                                Card(
                                    shape = RoundedCornerShape(14.dp),
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .aspectRatio(1f)
                                        .clickable {
                                            selectedImage.value = assetPath
                                        },
                                    elevation = CardDefaults.cardElevation(3.dp)
                                ) {
                                    AsyncImage(
                                        model = ImageRequest.Builder(context)
                                            .data("file:///android_asset/$assetPath")
                                            .crossfade(true)
                                            .build(),
                                        contentDescription = null,
                                        contentScale = ContentScale.Crop,
                                        modifier = Modifier.fillMaxSize()
                                    )
                                }
                            }

                            if (visible.size < archiveImages.size) {
                                item {
                                    Button(
                                        onClick = { page.value++ },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(8.dp),
                                        shape = RoundedCornerShape(12.dp)
                                    ) { Text("Load More") }
                                }
                            }
                        }

                        selectedImage.value?.let { img ->
                            Dialog(onDismissRequest = { selectedImage.value = null }) {
                                Box(
                                    modifier = Modifier
                                        .fillMaxSize()
                                        .background(Color.Black.copy(alpha = 0.85f))
                                        .clickable { selectedImage.value = null },
                                    contentAlignment = Alignment.Center
                                ) {
                                    AsyncImage(
                                        model = "file:///android_asset/$img",
                                        contentDescription = null,
                                        contentScale = ContentScale.Fit,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(20.dp)
                                    )
                                }
                            }
                        }
                    }
                }

                //------------------------------------------------
                // NEW ARTIFACTS
                //------------------------------------------------
                "new_artifacts" -> {
                    val uris =
                        remember(selectedScreen) {
                            loadNewArtifactImagesFromMediaStore(context)
                        }

                    Column(
                        modifier = Modifier.fillMaxSize().padding(horizontal = 12.dp)
                    ) {
                        Text(
                            "New Artifacts",
                            style = MaterialTheme.typography.headlineMedium,
                            modifier = Modifier.padding(vertical = 12.dp)
                        )

                        if (uris.isEmpty()) {
                            Box(
                                modifier = Modifier.fillMaxSize(),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    "No new artifacts found.",
                                    style = MaterialTheme.typography.bodyLarge,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        } else {
                            LazyVerticalGrid(
                                columns = GridCells.Adaptive(130.dp),
                                modifier = Modifier.fillMaxSize(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp),
                                contentPadding = PaddingValues(bottom = 60.dp)
                            ) {
                                items(uris) { uri ->
                                    Card(
                                        modifier = Modifier.aspectRatio(1f),
                                        shape = RoundedCornerShape(16.dp),
                                        elevation = CardDefaults.cardElevation(3.dp)
                                    ) {
                                        AsyncImage(
                                            model = uri,
                                            contentDescription = null,
                                            modifier = Modifier.fillMaxSize(),
                                            contentScale = ContentScale.Crop
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                //------------------------------------------------
                // EXPERT CHAT (ADD-ONLY)
                //------------------------------------------------
                "expert_chat" -> {
                    var input by remember { mutableStateOf("") }

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(12.dp)
                    ) {

                        Text(
                            "Ask an Expert",
                            style = MaterialTheme.typography.headlineMedium,
                            modifier = Modifier.padding(bottom = 8.dp)
                        )

                        LazyColumn(
                            modifier = Modifier
                                .weight(1f)
                                .fillMaxWidth(),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(expertChatMessages) { msg ->
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement =
                                        if (msg.isUser) Arrangement.End else Arrangement.Start
                                ) {
                                    Card(
                                        shape = RoundedCornerShape(14.dp),
                                        colors = CardDefaults.cardColors(
                                            containerColor =
                                                if (msg.isUser)
                                                    MaterialTheme.colorScheme.primaryContainer
                                                else
                                                    MaterialTheme.colorScheme.surfaceVariant
                                        ),
                                        modifier = Modifier.widthIn(max = 280.dp)
                                    ) {
                                        Column(Modifier.padding(10.dp)) {

                                            msg.imageUri?.let {
                                                AsyncImage(
                                                    model = it,
                                                    contentDescription = null,
                                                    modifier = Modifier
                                                        .fillMaxWidth()
                                                        .height(150.dp),
                                                    contentScale = ContentScale.Crop
                                                )
                                                Spacer(Modifier.height(6.dp))
                                            }

                                            if (msg.text.isNotBlank()) {
                                                Text(msg.text)
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            IconButton(onClick = {
                                showLibraryPicker = true
                            }) {
                                Icon(Icons.Filled.Photo, contentDescription = "Attach from Library")
                            }

                            TextField(
                                value = input,
                                onValueChange = { input = it },
                                placeholder = { Text("Type a message…") },
                                modifier = Modifier.weight(1f),
                                shape = RoundedCornerShape(14.dp)
                            )

                            IconButton(onClick = {
                                if (input.isNotBlank()) {
                                    expertChatMessages =
                                        expertChatMessages +
                                                ExpertChatMessage(input, null, true) +
                                                ExpertChatMessage("Ok.", null, false)
                                    input = ""
                                }
                            }) {
                                Icon(Icons.AutoMirrored.Filled.Send, contentDescription = "Send")
                            }
                        }
                    }
                }

                //------------------------------------------------
                // HELP
                //------------------------------------------------
                "help" -> HelpScreen()
            }

            if (showLibraryPicker) {
                AlertDialog(
                    onDismissRequest = { showLibraryPicker = false },
                    title = { Text("Select Artifact from Library") },
                    text = {
                        LazyColumn {
                            items(savedImageUris) { uri ->
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clickable {
                                            expertChatMessages =
                                                expertChatMessages +
                                                        ExpertChatMessage(
                                                            text = formatPredictions(predictionsByUri[uri] ?: emptyList()),
                                                            imageUri = uri,
                                                            isUser = true
                                                        ) +
                                                        ExpertChatMessage("Ok.", null, false)

                                            showLibraryPicker = false
                                        }
                                        .padding(8.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    AsyncImage(
                                        model = uri,
                                        contentDescription = null,
                                        modifier = Modifier.size(60.dp),
                                        contentScale = ContentScale.Crop
                                    )
                                    Spacer(Modifier.width(12.dp))
                                    Text("Attach this artifact")
                                }
                            }
                        }
                    },
                    confirmButton = {},
                    dismissButton = {
                        TextButton(onClick = { showLibraryPicker = false }) {
                            Text("Cancel")
                        }
                    }
                )
            }

            //------------------------------------------------
            // Fullscreen viewer
            //------------------------------------------------
            selectedImageUri?.let { uri ->
                AlertDialog(
                    onDismissRequest = { selectedImageUri = null },
                    title = { Text("Artifact Image") },
                    text = {
                        val bmp =
                            remember(uri) {
                                context.contentResolver.openInputStream(uri)?.use {
                                    BitmapFactory.decodeStream(it)
                                }
                            }
                        bmp?.let {
                            Image(
                                bitmap = it.asImageBitmap(),
                                null,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .aspectRatio(it.width.toFloat() / it.height),
                                contentScale = ContentScale.Fit
                            )
                        }
                    },
                    confirmButton = {},
                    dismissButton = {
                        TextButton(
                            onClick = {
                                context.contentResolver.delete(uri, null, null)
                                savedImageUris =
                                    savedImageUris.filter { it != uri }
                                selectedImageUri = null
                            }
                        ) { Text("Delete") }
                    }
                )
            }
        }
    }
}

//----------------------------------------------------
// HELP SCREEN
//----------------------------------------------------
@Composable
fun HelpScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Text("How to Use", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))

        HelpCard("Take Photo", "Scan new artifacts.", Icons.Filled.CameraAlt)
        HelpCard("Library", "View saved photos.", Icons.Filled.Photo)
        HelpCard("Browse", "Explore archive dataset.", Icons.Filled.Collections)
        HelpCard("New Artifacts", "See new discovered items.", Icons.Filled.CloudDownload)
        HelpCard("Ask an Expert", "Tap the chat button in the bottom-right to message an expert.", Icons.Filled.ChatBubbleOutline)
        HelpCard("Help", "Tap the help icon for instructions.", Icons.Filled.Info)
    }
}

@Composable
fun HelpCard(title: String, desc: String, icon: ImageVector) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Row(modifier = Modifier.padding(16.dp)) {
            Icon(icon, null, modifier = Modifier.size(40.dp))
            Spacer(Modifier.width(16.dp))
            Column {
                Text(title, style = MaterialTheme.typography.titleMedium)
                Text(desc)
            }
        }
    }
}

//----------------------------------------------------
// Expert chat message model (ADD-ONLY)
//----------------------------------------------------
data class ExpertChatMessage(
    val text: String,
    val imageUri: Uri? = null,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis()
)