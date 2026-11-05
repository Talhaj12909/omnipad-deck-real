```python
#!/usr/bin/env python3
"""
OmniPad Deck — Automated Android Project Generator (setup_project.py)
Generates the complete, compilable Android project structure, Gradle configuration,
XML resources, Kotlin + Jetpack Compose source files (Modules 1-5), and GitHub Actions workflow.
Run: python3 setup_project.py
"""

import os
from pathlib import Path

PROJECT_FILES = {
    "settings.gradle.kts": """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "OmniPadDeck"
include(":app")
""",

    "build.gradle.kts": """plugins {
    id("com.android.application") version "8.7.3" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false
}
""",

    "gradle.properties": """org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
kotlin.code.style=official
""",

    "app/proguard-rules.pro": """-keep class com.omnipad.deck.** { *; }
-keep class rikka.shizuku.** { *; }
-dontwarn rikka.shizuku.**
""",

    "app/build.gradle.kts": """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.omnipad.deck"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.omnipad.deck"
        minSdk = 29
        targetSdk = 35
        versionCode = 100
        versionName = "1.0.0-universal"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
        debug {
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
        freeCompilerArgs += listOf(
            "-opt-in=androidx.compose.material3.ExperimentalMaterial3Api",
            "-opt-in=androidx.compose.foundation.ExperimentalFoundationApi",
            "-opt-in=androidx.compose.ui.ExperimentalComposeUiApi",
            "-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi"
        )
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
    implementation("androidx.lifecycle:lifecycle-service:2.8.7")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.fragment:fragment-ktx:1.8.5")
    implementation("androidx.savedstate:savedstate-ktx:1.2.1")

    val composeBom = platform("androidx.compose:compose-bom:2024.12.01")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")

    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")

    val cameraXVersion = "1.4.1"
    implementation("androidx.camera:camera-core:$cameraXVersion")
    implementation("androidx.camera:camera-camera2:$cameraXVersion")
    implementation("androidx.camera:camera-lifecycle:$cameraXVersion")
    implementation("androidx.camera:camera-view:$cameraXVersion")
    implementation("com.google.mlkit:barcode-scanning:17.3.0")

    implementation("com.google.zxing:core:3.5.3")
    implementation("androidx.biometric:biometric:1.1.0")
    implementation("androidx.palette:palette-ktx:1.0.0")

    val shizukuVersion = "13.1.5"
    implementation("dev.rikka.shizuku:api:$shizukuVersion")
    implementation("dev.rikka.shizuku:provider:$shizukuVersion")
}
""",

    "app/src/main/res/values/strings.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">OmniPad Deck</string>
    <string name="accessibility_service_description">OmniPad Auto-Suspending Global Trackpad and Shortcut Receiver</string>
</resources>
""",

    "app/src/main/res/xml/method.xml": """<?xml version="1.0" encoding="utf-8"?>
<input-method xmlns:android="http://schemas.android.com/apk/res/android"
    android:settingsActivity="com.omnipad.deck.ui.MainActivity"
    android:supportsInlineSuggestions="true">
    <subtype
        android:icon="@android:drawable/ic_menu_edit"
        android:imeSubtypeLocale="en_US"
        android:imeSubtypeMode="keyboard"
        android:isAsciiCapable="true"
        android:label="OmniPad Wi-Fi Deck (0px Viewport)" />
</input-method>
""",

    "app/src/main/res/xml/accessibility_service_config.xml": """<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeWindowStateChanged|typeViewFocused"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagRetrieveInteractiveWindows|flagRequestFilterKeyEvents"
    android:canPerformGestures="true"
    android:canRequestFilterKeyEvents="true"
    android:canRetrieveWindowContent="true"
    android:description="@string/accessibility_service_description"
    android:notificationTimeout="50"
    android:settingsActivity="com.omnipad.deck.ui.MainActivity" />
""",

    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.bluetooth" android:required="false" />
    <uses-feature android:name="android.hardware.bluetooth_le" android:required="false" />
    <uses-feature android:name="android.hardware.wifi.direct" android:required="false" />
    <uses-feature android:name="android.hardware.sensor.gyroscope" android:required="false" />

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />
    <uses-permission android:name="android.permission.CHANGE_WIFI_MULTICAST_STATE" />
    <uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />

    <uses-permission
        android:name="android.permission.NEARBY_WIFI_DEVICES"
        android:usesPermissionFlags="neverForLocation"
        tools:targetApi="tiramisu" />

    <uses-permission
        android:name="android.permission.ACCESS_FINE_LOCATION"
        android:maxSdkVersion="32" />
    <uses-permission
        android:name="android.permission.ACCESS_COARSE_LOCATION"
        android:maxSdkVersion="32" />

    <uses-permission
        android:name="android.permission.BLUETOOTH"
        android:maxSdkVersion="30" />
    <uses-permission
        android:name="android.permission.BLUETOOTH_ADMIN"
        android:maxSdkVersion="30" />

    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
    <uses-permission android:name="android.permission.BLUETOOTH_ADVERTISE" />

    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.USE_BIOMETRIC" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />

    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_CONNECTED_DEVICE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <application
        android:allowBackup="false"
        android:icon="@android:drawable/sym_def_app_icon"
        android:label="@string/app_name"
        android:roundIcon="@android:drawable/sym_def_app_icon"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.DeviceDefault.NoActionBar"
        android:usesCleartextTraffic="false">

        <activity
            android:name=".ui.MainActivity"
            android:configChanges="orientation|screenSize|screenLayout|smallestScreenSize|keyboard|keyboardHidden|uiMode"
            android:exported="true"
            android:launchMode="singleTask"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".receiver.WifiZeroHeightImeService"
            android:directBootAware="true"
            android:exported="true"
            android:label="OmniPad Zero-Height Wi-Fi Keyboard"
            android:permission="android.permission.BIND_INPUT_METHOD">
            <intent-filter>
                <action android:name="android.view.InputMethod" />
            </intent-filter>
            <meta-data
                android:name="android.view.im"
                android:resource="@xml/method" />
        </service>

        <service
            android:name=".receiver.AutoSuspendingTrackpadAccessibilityService"
            android:exported="true"
            android:label="OmniPad Auto-Suspending Pointer Receiver"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/accessibility_service_config" />
        </service>

        <service
            android:name=".service.QuickLaunchTileService"
            android:exported="true"
            android:icon="@android:drawable/ic_menu_share"
            android:label="OmniPad Deck"
            android:permission="android.permission.BIND_QUICK_SETTINGS_TILE">
            <intent-filter>
                <action android:name="android.service.quicksettings.action.QS_TILE" />
            </intent-filter>
        </service>

        <service
            android:name=".service.ConnectionKeepAliveForegroundService"
            android:enabled="true"
            android:exported="false"
            android:foregroundServiceType="connectedDevice" />

        <provider
            android:name="rikka.shizuku.ShizukuProvider"
            android:authorities="${applicationId}.shizuku"
            android:enabled="true"
            android:exported="true"
            android:multiprocess="false"
            android:permission="android.permission.INTERACT_ACROSS_USERS_FULL" />

    </application>
</manifest>
""",

    "app/src/main/java/com/omnipad/deck/core/permissions/RuntimePermissionOrchestrator.kt": """package com.omnipad.deck.core.permissions

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat

object RuntimePermissionOrchestrator {

    fun getRequiredMeshPermissions(): Array<String> {
        val permissions = mutableListOf<String>()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.NEARBY_WIFI_DEVICES)
        } else {
            permissions.add(Manifest.permission.ACCESS_FINE_LOCATION)
            permissions.add(Manifest.permission.ACCESS_COARSE_LOCATION)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            permissions.add(Manifest.permission.BLUETOOTH_CONNECT)
            permissions.add(Manifest.permission.BLUETOOTH_ADVERTISE)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        return permissions.toTypedArray()
    }

    fun hasMeshPermissions(context: Context): Boolean {
        return getRequiredMeshPermissions().all { perm ->
            ContextCompat.checkSelfPermission(context, perm) == PackageManager.PERMISSION_GRANTED
        }
    }

    fun hasBluetoothPermissions(context: Context): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.BLUETOOTH_CONNECT
            ) == PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.BLUETOOTH_ADVERTISE
                ) == PackageManager.PERMISSION_GRANTED
        } else {
            true
        }
    }

    fun hasWifiP2pPermissions(context: Context): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.NEARBY_WIFI_DEVICES
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) == PackageManager.PERMISSION_GRANTED
        }
    }
}
""",

    "app/src/main/java/com/omnipad/deck/core/haptics/AdaptiveHapticEngine.kt": """package com.omnipad.deck.core.haptics

import android.content.Context
import android.media.AudioAttributes
import android.media.SoundPool
import android.os.Build
import android.os.VibrationAttributes
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.atomic.AtomicLong
import kotlin.math.exp
import kotlin.math.sin

class AdaptiveHapticEngine(private val context: Context) {

    private val engineScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    private val vibrator: Vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        val manager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
        manager.defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
    }

    private val supportsLraPrimitives: Boolean = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        vibrator.areAllPrimitivesSupported(
            VibrationEffect.Composition.PRIMITIVE_TICK,
            VibrationEffect.Composition.PRIMITIVE_CLICK
        )
    } else {
        false
    }

    private val supportsLowTickPrimitive: Boolean = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        vibrator.areAllPrimitivesSupported(VibrationEffect.Composition.PRIMITIVE_LOW_TICK)
    } else {
        false
    }

    private val supportsAmplitudeControl: Boolean = vibrator.hasAmplitudeControl()
    private val lastDetentTimestampNanos = AtomicLong(0L)

    private val soundPool: SoundPool
    private var soundIdKeyDown: Int = 0
    private var soundIdKeyUp: Int = 0
    private var soundIdDialTick: Int = 0
    var acousticsEnabled: Boolean = true
    var hapticsEnabled: Boolean = true

    init {
        val audioAttributes = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_ASSISTANCE_SONIFICATION)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build()

        soundPool = SoundPool.Builder()
            .setMaxStreams(8)
            .setAudioAttributes(audioAttributes)
            .build()

        engineScope.launch(Dispatchers.IO) {
            synthesizeAndLoadMechanicalAcoustics()
        }
    }

    fun performPreClickHomingDetent(isHomeBarKey: Boolean = true) {
        if (!hapticsEnabled || !vibrator.hasVibrator()) return
        val now = System.nanoTime()
        if (now - lastDetentTimestampNanos.get() < 18_000_000L) return
        lastDetentTimestampNanos.set(now)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && supportsLraPrimitives) {
            val primitive = if (isHomeBarKey || !supportsLowTickPrimitive) {
                VibrationEffect.Composition.PRIMITIVE_TICK
            } else {
                VibrationEffect.Composition.PRIMITIVE_LOW_TICK
            }
            val scale = if (isHomeBarKey) 0.45f else 0.25f
            val effect = VibrationEffect.startComposition()
                .addPrimitive(primitive, scale)
                .compose()
            vibrateWithHardwareAttributes(effect)
        } else {
            val durationMs = if (isHomeBarKey) 6L else 4L
            val amplitude = if (supportsAmplitudeControl) {
                if (isHomeBarKey) 75 else 45
            } else {
                VibrationEffect.DEFAULT_AMPLITUDE
            }
            vibrateWithHardwareAttributes(VibrationEffect.createOneShot(durationMs, amplitude))
        }
    }

    fun performMechanicalKeyPress(isKeyDown: Boolean, isModifierOrSpace: Boolean = false) {
        if (acousticsEnabled) {
            val soundId = if (isKeyDown) soundIdKeyDown else soundIdKeyUp
            if (soundId != 0) {
                val pitch = if (isModifierOrSpace) 0.88f else 1.0f
                val volume = if (isKeyDown) 0.55f else 0.30f
                soundPool.play(soundId, volume, volume, 1, 0, pitch)
            }
        }

        if (!hapticsEnabled || !vibrator.hasVibrator()) return

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && supportsLraPrimitives) {
            val effect = if (isKeyDown) {
                val scale = if (isModifierOrSpace) 0.90f else 0.72f
                VibrationEffect.startComposition()
                    .addPrimitive(VibrationEffect.Composition.PRIMITIVE_CLICK, scale)
                    .compose()
            } else {
                VibrationEffect.startComposition()
                    .addPrimitive(VibrationEffect.Composition.PRIMITIVE_TICK, 0.32f)
                    .compose()
            }
            vibrateWithHardwareAttributes(effect)
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q && !supportsAmplitudeControl) {
            val effectId = if (isKeyDown) {
                VibrationEffect.EFFECT_CLICK
            } else {
                VibrationEffect.EFFECT_TICK
            }
            vibrateWithHardwareAttributes(VibrationEffect.createPredefined(effectId))
        } else {
            val durationMs = if (isKeyDown) 10L else 6L
            val amplitude = if (supportsAmplitudeControl) {
                if (isKeyDown) 160 else 70
            } else {
                VibrationEffect.DEFAULT_AMPLITUDE
            }
            vibrateWithHardwareAttributes(VibrationEffect.createOneShot(durationMs, amplitude))
        }
    }

    fun performRotaryDialDetent(angularVelocityRadPerSec: Float, precisionTier: Int) {
        val now = System.nanoTime()
        if (now - lastDetentTimestampNanos.get() < 14_000_000L) return
        lastDetentTimestampNanos.set(now)

        if (acousticsEnabled && soundIdDialTick != 0) {
            val pitch = when (precisionTier) {
                0 -> 0.85f
                1 -> 1.05f
                else -> 1.28f
            }
            soundPool.play(soundIdDialTick, 0.35f, 0.35f, 1, 0, pitch)
        }

        if (!hapticsEnabled || !vibrator.hasVibrator()) return

        val normalizedVelocity = (angularVelocityRadPerSec / 12f).coerceIn(0.25f, 1.0f)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && supportsLraPrimitives) {
            val primitive = when (precisionTier) {
                0 -> VibrationEffect.Composition.PRIMITIVE_CLICK
                else -> VibrationEffect.Composition.PRIMITIVE_TICK
            }
            val scale = when (precisionTier) {
                0 -> (0.55f + 0.45f * normalizedVelocity).coerceIn(0.4f, 1.0f)
                1 -> (0.35f + 0.45f * normalizedVelocity).coerceIn(0.3f, 0.85f)
                else -> (0.22f + 0.30f * normalizedVelocity).coerceIn(0.2f, 0.55f)
            }
            val effect = VibrationEffect.startComposition()
                .addPrimitive(primitive, scale)
                .compose()
            vibrateWithHardwareAttributes(effect)
        } else {
            val amplitude = if (supportsAmplitudeControl) {
                val baseAmp = when (precisionTier) {
                    0 -> 180
                    1 -> 125
                    else -> 80
                }
                (baseAmp * normalizedVelocity).toInt().coerceIn(50, 255)
            } else {
                VibrationEffect.DEFAULT_AMPLITUDE
            }
            vibrateWithHardwareAttributes(VibrationEffect.createOneShot(8L, amplitude))
        }
    }

    fun performTrackpadMorphSnap(enteringTrackpad: Boolean) {
        if (!hapticsEnabled || !vibrator.hasVibrator()) return

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && supportsLraPrimitives) {
            val composition = VibrationEffect.startComposition()
            if (enteringTrackpad) {
                composition.addPrimitive(VibrationEffect.Composition.PRIMITIVE_TICK, 0.5f)
                composition.addPrimitive(VibrationEffect.Composition.PRIMITIVE_CLICK, 0.9f, 22)
            } else {
                composition.addPrimitive(VibrationEffect.Composition.PRIMITIVE_CLICK, 0.6f)
            }
            vibrateWithHardwareAttributes(composition.compose())
        } else {
            vibrateWithHardwareAttributes(
                VibrationEffect.createOneShot(
                    if (enteringTrackpad) 14L else 8L,
                    if (supportsAmplitudeControl) 190 else VibrationEffect.DEFAULT_AMPLITUDE
                )
            )
        }
    }

    private fun vibrateWithHardwareAttributes(effect: VibrationEffect) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val attributes = VibrationAttributes.Builder()
                .setUsage(VibrationAttributes.USAGE_HARDWARE_FEEDBACK)
                .build()
            vibrator.vibrate(effect, attributes)
        } else {
            val audioAttrs = AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_ASSISTANCE_SONIFICATION)
                .build()
            @Suppress("DEPRECATION")
            vibrator.vibrate(effect, audioAttrs)
        }
    }

    private fun synthesizeAndLoadMechanicalAcoustics() {
        val keyDownFile = File(context.cacheDir, "omnipad_key_down.wav")
        val keyUpFile = File(context.cacheDir, "omnipad_key_up.wav")
        val dialTickFile = File(context.cacheDir, "omnipad_dial_tick.wav")

        writeSynthesizedWav(keyDownFile, 14, 1450.0, 420.0, 320.0)
        writeSynthesizedWav(keyUpFile, 10, 1850.0, 620.0, 450.0)
        writeSynthesizedWav(dialTickFile, 7, 2200.0, 950.0, 650.0)

        soundIdKeyDown = soundPool.load(keyDownFile.absolutePath, 1)
        soundIdKeyUp = soundPool.load(keyUpFile.absolutePath, 1)
        soundIdDialTick = soundPool.load(dialTickFile.absolutePath, 1)
    }

    private fun writeSynthesizedWav(
        file: File,
        durationMs: Int,
        primaryFreqHz: Double,
        secondaryFreqHz: Double,
        decayRate: Double
    ) {
        val sampleRate = 44100
        val numSamples = (sampleRate * durationMs) / 1000
        val pcmData = ByteArray(numSamples * 2)
        val pcmBuffer = ByteBuffer.wrap(pcmData).order(ByteOrder.LITTLE_ENDIAN)

        for (i in 0 until numSamples) {
            val t = i.toDouble() / sampleRate
            val envelope = exp(-decayRate * t)
            val wave = (0.65 * sin(2.0 * Math.PI * primaryFreqHz * t) +
                0.35 * sin(2.0 * Math.PI * secondaryFreqHz * t)) * envelope
            val sample = (wave * Short.MAX_VALUE * 0.75).toInt().coerceIn(
                Short.MIN_VALUE.toInt(),
                Short.MAX_VALUE.toInt()
            ).toShort()
            pcmBuffer.putShort(sample)
        }

        val totalDataLen = pcmData.size + 36
        val header = ByteBuffer.allocate(44).order(ByteOrder.LITTLE_ENDIAN).apply {
            put("RIFF".toByteArray(Charsets.US_ASCII))
            putInt(totalDataLen)
            put("WAVE".toByteArray(Charsets.US_ASCII))
            put("fmt ".toByteArray(Charsets.US_ASCII))
            putInt(16)
            putShort(1)
            putShort(1)
            putInt(sampleRate)
            putInt(sampleRate * 2)
            putShort(2)
            putShort(16)
            put("data".toByteArray(Charsets.US_ASCII))
            putInt(pcmData.size)
        }.array()

        FileOutputStream(file).use { fos ->
            fos.write(header)
            fos.write(pcmData)
        }
    }

    fun release() {
        soundPool.release()
    }
}
""",

    "app/src/main/java/com/omnipad/deck/core/crypto/ZeroTrustCryptoEngine.kt": """package com.omnipad.deck.core.crypto

import android.graphics.Bitmap
import android.graphics.Color
import android.util.Base64
import com.google.zxing.BarcodeFormat
import com.google.zxing.EncodeHintType
import com.google.zxing.qrcode.QRCodeWriter
import com.google.zxing.qrcode.decoder.ErrorCorrectionLevel
import org.json.JSONArray
import org.json.JSONObject
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.KeyFactory
import java.security.KeyPair
import java.security.KeyPairGenerator
import java.security.MessageDigest
import java.security.PublicKey
import java.security.SecureRandom
import java.security.spec.ECGenParameterSpec
import java.security.spec.X509EncodedKeySpec
import java.util.concurrent.atomic.AtomicLong
import javax.crypto.Cipher
import javax.crypto.KeyAgreement
import javax.crypto.Mac
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

data class MultiPathPairingPayload(
    val version: Int = 1,
    val deviceName: String,
    val lanAddresses: List<String>,
    val tcpControlPort: Int,
    val udpSpatialPort: Int,
    val wifiDirectDeviceName: String,
    val wifiDirectMacOrPeerId: String,
    val bluetoothHidMac: String,
    val ecdhPublicKeyBase64: String,
    val pin6Digit: String,
    val timestampEpochMs: Long = System.currentTimeMillis()
) {
    fun toCompactQrString(): String {
        val json = JSONObject().apply {
            put("v", version)
            put("n", deviceName)
            put("ip", JSONArray(lanAddresses))
            put("tp", tcpControlPort)
            put("up", udpSpatialPort)
            put("wn", wifiDirectDeviceName)
            put("wm", wifiDirectMacOrPeerId)
            put("bm", bluetoothHidMac)
            put("pk", ecdhPublicKeyBase64)
            put("pin", pin6Digit)
            put("ts", timestampEpochMs)
        }
        val rawBytes = json.toString().toByteArray(Charsets.UTF_8)
        return "OMNIPAD1:" + Base64.encodeToString(
            rawBytes,
            Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING
        )
    }

    companion object {
        fun fromCompactQrString(qrString: String): MultiPathPairingPayload {
            require(qrString.startsWith("OMNIPAD1:")) { "Invalid OmniPad QR prefix" }
            val encoded = qrString.removePrefix("OMNIPAD1:")
            val decodedBytes = Base64.decode(
                encoded,
                Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING
            )
            val json = JSONObject(String(decodedBytes, Charsets.UTF_8))
            val ipArray = json.optJSONArray("ip") ?: JSONArray()
            val ips = mutableListOf<String>()
            for (i in 0 until ipArray.length()) {
                ips.add(ipArray.getString(i))
            }
            return MultiPathPairingPayload(
                version = json.optInt("v", 1),
                deviceName = json.optString("n", "Android Slate"),
                lanAddresses = ips,
                tcpControlPort = json.getInt("tp"),
                udpSpatialPort = json.getInt("up"),
                wifiDirectDeviceName = json.optString("wn", ""),
                wifiDirectMacOrPeerId = json.optString("wm", ""),
                bluetoothHidMac = json.optString("bm", ""),
                ecdhPublicKeyBase64 = json.getString("pk"),
                pin6Digit = json.getString("pin"),
                timestampEpochMs = json.optLong("ts", 0L)
            )
        }
    }
}

class ZeroTrustCryptoEngine {

    private val secureRandom = SecureRandom()
    private var localKeyPair: KeyPair = generateEphemeralEcKeyPair()
    private var activePin6Digit: String = generateRandom6DigitPin()

    @Volatile
    private var sessionKeys: DerivedSessionKeys? = null

    private val tcpTxSequence = AtomicLong(1L)
    private val tcpRxHighestSequence = AtomicLong(0L)

    private val udpTxSequence = AtomicLong(1L)
    private val udpReplayLock = Any()
    private var udpHighestSequence: Long = 0L
    private var udpReplayWindowBitmask: Long = 0L

    data class DerivedSessionKeys(
        val tcpTxKey: SecretKeySpec,
        val tcpRxKey: SecretKeySpec,
        val udpTxKey: SecretKeySpec,
        val udpRxKey: SecretKeySpec,
        val tcpTxIvSalt: ByteArray,
        val tcpRxIvSalt: ByteArray,
        val udpTxIvSalt: ByteArray,
        val udpRxIvSalt: ByteArray,
        val sessionFingerprintHex: String
    )

    fun rotateEphemeralIdentity(): Pair<String, String> {
        localKeyPair = generateEphemeralEcKeyPair()
        activePin6Digit = generateRandom6DigitPin()
        sessionKeys = null
        tcpTxSequence.set(1L)
        tcpRxHighestSequence.set(0L)
        udpTxSequence.set(1L)
        synchronized(udpReplayLock) {
            udpHighestSequence = 0L
            udpReplayWindowBitmask = 0L
        }
        return getLocalPublicKeyBase64() to activePin6Digit
    }

    fun getLocalPublicKeyBase64(): String {
        return Base64.encodeToString(
            localKeyPair.public.encoded,
            Base64.NO_WRAP
        )
    }

    fun getActivePin6Digit(): String = activePin6Digit

    fun setActivePin6Digit(pin: String) {
        require(pin.length == 6 && pin.all { it.isDigit() }) { "PIN must be 6 digits" }
        activePin6Digit = pin
    }

    fun isSessionEstablished(): Boolean = sessionKeys != null

    fun getSessionFingerprint(): String = sessionKeys?.sessionFingerprintHex ?: "UNPAIRED"

    fun establishZeroTrustSession(
        remotePublicKeyBase64: String,
        pin6Digit: String,
        isInitiator: Boolean
    ): String {
        val remotePubBytes = Base64.decode(remotePublicKeyBase64, Base64.NO_WRAP)
        val keyFactory = KeyFactory.getInstance("EC")
        val remotePublicKey: PublicKey = keyFactory.generatePublic(X509EncodedKeySpec(remotePubBytes))

        val keyAgreement = KeyAgreement.getInstance("ECDH")
        keyAgreement.init(localKeyPair.private)
        keyAgreement.doPhase(remotePublicKey, true)
        val rawSharedSecret = keyAgreement.generateSecret()

        val localPubBytes = localKeyPair.public.encoded
        val (initiatorPub, responderPub) = if (isInitiator) {
            localPubBytes to remotePubBytes
        } else {
            remotePubBytes to localPubBytes
        }

        val saltDigest = MessageDigest.getInstance("SHA-256").apply {
            update("OMNIPAD-ZERO-TRUST-SALT-V1".toByteArray(Charsets.UTF_8))
            update(pin6Digit.toByteArray(Charsets.UTF_8))
            update(initiatorPub)
            update(responderPub)
        }.digest()

        val prk = hkdfExtract(salt = saltDigest, ikm = rawSharedSecret)

        val okm = hkdfExpand(
            prk = prk,
            info = "OMNIPAD-DECK-AES256-GCM-KEYS".toByteArray(Charsets.UTF_8),
            outputLength = 160
        )

        val initTcpKey = SecretKeySpec(okm.copyOfRange(0, 32), "AES")
        val respTcpKey = SecretKeySpec(okm.copyOfRange(32, 64), "AES")
        val initUdpKey = SecretKeySpec(okm.copyOfRange(64, 96), "AES")
        val respUdpKey = SecretKeySpec(okm.copyOfRange(96, 128), "AES")

        val initTcpSalt = okm.copyOfRange(128, 132)
        val respTcpSalt = okm.copyOfRange(132, 136)
        val initUdpSalt = okm.copyOfRange(136, 140)
        val respUdpSalt = okm.copyOfRange(140, 144)

        val fingerprintBytes = okm.copyOfRange(144, 152)
        val fingerprintHex = fingerprintBytes.joinToString("") { "%02X".format(it) }

        sessionKeys = if (isInitiator) {
            DerivedSessionKeys(
                tcpTxKey = initTcpKey,
                tcpRxKey = respTcpKey,
                udpTxKey = initUdpKey,
                udpRxKey = respUdpKey,
                tcpTxIvSalt = initTcpSalt,
                tcpRxIvSalt = respTcpSalt,
                udpTxIvSalt = initUdpSalt,
                udpRxIvSalt = respUdpSalt,
                sessionFingerprintHex = fingerprintHex
            )
        } else {
            DerivedSessionKeys(
                tcpTxKey = respTcpKey,
                tcpRxKey = initTcpKey,
                udpTxKey = respUdpKey,
                udpRxKey = initUdpKey,
                tcpTxIvSalt = respTcpSalt,
                tcpRxIvSalt = initTcpSalt,
                udpTxIvSalt = respUdpSalt,
                udpRxIvSalt = initUdpSalt,
                sessionFingerprintHex = fingerprintHex
            )
        }

        tcpTxSequence.set(1L)
        tcpRxHighestSequence.set(0L)
        udpTxSequence.set(1L)
        synchronized(udpReplayLock) {
            udpHighestSequence = 0L
            udpReplayWindowBitmask = 0L
        }

        return fingerprintHex
    }

    fun encryptTcpFrame(frameType: Byte, plaintext: ByteArray): ByteArray {
        val keys = sessionKeys ?: throw IllegalStateException("ZeroTrust session not established")
        val seq = tcpTxSequence.getAndIncrement()
        val iv = buildDeterministicIv(keys.tcpTxIvSalt, seq)
        val aad = buildAad(frameType, seq)

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, keys.tcpTxKey, GCMParameterSpec(128, iv))
        cipher.updateAAD(aad)
        val cipherTextWithTag = cipher.doFinal(plaintext)

        return ByteBuffer.allocate(8 + cipherTextWithTag.size)
            .order(ByteOrder.BIG_ENDIAN)
            .putLong(seq)
            .put(cipherTextWithTag)
            .array()
    }

    fun decryptTcpFrame(frameType: Byte, encryptedPayload: ByteArray): ByteArray {
        require(encryptedPayload.size >= 8 + 16) { "Encrypted TCP frame too short" }
        val keys = sessionKeys ?: throw IllegalStateException("ZeroTrust session not established")

        val buffer = ByteBuffer.wrap(encryptedPayload).order(ByteOrder.BIG_ENDIAN)
        val seq = buffer.long

        val prevSeq = tcpRxHighestSequence.get()
        if (seq <= prevSeq) {
            throw SecurityException("TCP replay or out-of-order frame detected: seq=$seq <= prev=$prevSeq")
        }

        val iv = buildDeterministicIv(keys.tcpRxIvSalt, seq)
        val aad = buildAad(frameType, seq)

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, keys.tcpRxKey, GCMParameterSpec(128, iv))
        cipher.updateAAD(aad)

        val plaintext = cipher.doFinal(encryptedPayload, 8, encryptedPayload.size - 8)
        tcpRxHighestSequence.set(seq)
        return plaintext
    }

    fun encryptUdpDatagram(packetType: Byte, plaintext: ByteArray): ByteArray {
        val keys = sessionKeys ?: throw IllegalStateException("ZeroTrust session not established")
        val seq = udpTxSequence.getAndIncrement()
        val iv = buildDeterministicIv(keys.udpTxIvSalt, seq)
        val aad = buildAad(packetType, seq)

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, keys.udpTxKey, GCMParameterSpec(128, iv))
        cipher.updateAAD(aad)
        val cipherTextWithTag = cipher.doFinal(plaintext)

        return ByteBuffer.allocate(1 + 8 + cipherTextWithTag.size)
            .order(ByteOrder.BIG_ENDIAN)
            .put(packetType)
            .putLong(seq)
            .put(cipherTextWithTag)
            .array()
    }

    fun decryptUdpDatagram(datagramBytes: ByteArray, length: Int): Pair<Byte, ByteArray>? {
        if (length < 1 + 8 + 16) return null
        val keys = sessionKeys ?: return null

        val buffer = ByteBuffer.wrap(datagramBytes, 0, length).order(ByteOrder.BIG_ENDIAN)
        val packetType = buffer.get()
        val seq = buffer.long

        synchronized(udpReplayLock) {
            if (!isUdpSequenceValidBeforeDecrypt(seq)) {
                return null
            }
        }

        val iv = buildDeterministicIv(keys.udpRxIvSalt, seq)
        val aad = buildAad(packetType, seq)

        return try {
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.DECRYPT_MODE, keys.udpRxKey, GCMParameterSpec(128, iv))
            cipher.updateAAD(aad)
            val plaintext = cipher.doFinal(datagramBytes, 9, length - 9)

            synchronized(udpReplayLock) {
                commitUdpSequenceAfterDecrypt(seq)
            }
            packetType to plaintext
        } catch (e: Exception) {
            null
        }
    }

    private fun isUdpSequenceValidBeforeDecrypt(seq: Long): Boolean {
        if (seq <= 0L) return false
        if (seq > udpHighestSequence) return true
        val diff = udpHighestSequence - seq
        if (diff >= 64L) return false
        val mask = 1L shl diff.toInt()
        return (udpReplayWindowBitmask and mask) == 0L
    }

    private fun commitUdpSequenceAfterDecrypt(seq: Long) {
        if (seq > udpHighestSequence) {
            val shift = seq - udpHighestSequence
            udpReplayWindowBitmask = if (shift >= 64L) {
                1L
            } else {
                (udpReplayWindowBitmask shl shift.toInt()) or 1L
            }
            udpHighestSequence = seq
        } else {
            val diff = udpHighestSequence - seq
            if (diff < 64L) {
                udpReplayWindowBitmask = udpReplayWindowBitmask or (1L shl diff.toInt())
            }
        }
    }

    private fun buildDeterministicIv(salt4Bytes: ByteArray, sequenceNumber: Long): ByteArray {
        return ByteBuffer.allocate(12)
            .order(ByteOrder.BIG_ENDIAN)
            .put(salt4Bytes, 0, 4)
            .putLong(sequenceNumber)
            .array()
    }

    private fun buildAad(typeByte: Byte, sequenceNumber: Long): ByteArray {
        return ByteBuffer.allocate(9)
            .order(ByteOrder.BIG_ENDIAN)
            .put(typeByte)
            .putLong(sequenceNumber)
            .array()
    }

    private fun generateEphemeralEcKeyPair(): KeyPair {
        val generator = KeyPairGenerator.getInstance("EC")
        generator.initialize(ECGenParameterSpec("secp256r1"), secureRandom)
        return generator.generateKeyPair()
    }

    private fun generateRandom6DigitPin(): String {
        val value = secureRandom.nextInt(900_000) + 100_000
        return value.toString()
    }

    private fun hkdfExtract(salt: ByteArray, ikm: ByteArray): ByteArray {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(salt, "HmacSHA256"))
        return mac.doFinal(ikm)
    }

    private fun hkdfExpand(prk: ByteArray, info: ByteArray, outputLength: Int): ByteArray {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(prk, "HmacSHA256"))

        val result = ByteArray(outputLength)
        var t = ByteArray(0)
        var offset = 0
        var counter = 1

        while (offset < outputLength) {
            mac.reset()
            mac.update(t)
            mac.update(info)
            mac.update(counter.toByte())
            t = mac.doFinal()

            val copyLen = minOf(t.size, outputLength - offset)
            System.arraycopy(t, 0, result, offset, copyLen)
            offset += copyLen
            counter++
        }
        return result
    }

    companion object {
        fun generatePairingQrBitmap(payload: MultiPathPairingPayload, sizePx: Int = 640): Bitmap {
            val content = payload.toCompactQrString()
            val hints = mapOf(
                EncodeHintType.ERROR_CORRECTION to ErrorCorrectionLevel.M,
                EncodeHintType.CHARACTER_SET to "UTF-8",
                EncodeHintType.MARGIN to 1
            )
            val bitMatrix = QRCodeWriter().encode(content, BarcodeFormat.QR_CODE, sizePx, sizePx, hints)
            val pixels = IntArray(sizePx * sizePx)
            for (y in 0 until sizePx) {
                val rowOffset = y * sizePx
                for (x in 0 until sizePx) {
                    pixels[rowOffset + x] = if (bitMatrix.get(x, y)) Color.BLACK else Color.WHITE
                }
            }
            return Bitmap.createBitmap(sizePx, sizePx, Bitmap.Config.ARGB_8888).apply {
                setPixels(pixels, 0, sizePx, 0, 0, sizePx, sizePx)
            }
        }
    }
}
""",

    "app/src/main/java/com/omnipad/deck/core/network/DualChannelSocketTransport.kt": """package com.omnipad.deck.core.network

import com.omnipad.deck.core.crypto.ZeroTrustCryptoEngine
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.io.DataInputStream
import java.io.DataOutputStream
import java.io.EOFException
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.ServerSocket
import java.net.Socket
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.hypot
import kotlin.math.pow

object TcpFrameType {
    const val HEARTBEAT_PING: Byte = 0x01
    const val HEARTBEAT_PONG: Byte = 0x02
    const val ECDH_HANDSHAKE_INIT: Byte = 0x03
    const val ECDH_HANDSHAKE_ACK: Byte = 0x04

    const val KEY_EVENT: Byte = 0x10
    const val MODIFIER_BITMASK: Byte = 0x11
    const val PRECOMPOSE_COMMIT: Byte = 0x12
    const val EXTRACTED_TEXT_SYNC: Byte = 0x13
    const val CLIPBOARD_SYNC: Byte = 0x14
    const val FILE_CHUNK: Byte = 0x15
    const val VAULT_PIPE_AUTOTYPE: Byte = 0x16
    const val WINDOW_ORCHESTRATOR_CMD: Byte = 0x17
    const val CREATIVE_DIAL_CMD: Byte = 0x18
    const val PRESENTATION_OVERLAY_CMD: Byte = 0x19
}

object UdpDatagramType {
    const val POINTER_DELTA: Byte = 0x01
    const val SCROLL_DELTA: Byte = 0x02
    const val PINCH_ZOOM: Byte = 0x03
    const val GYRO_AIR_MOUSE: Byte = 0x04
}

object ModifierBits {
    const val CTRL_LEFT: Int = 1 shl 0
    const val CTRL_RIGHT: Int = 1 shl 1
    const val SHIFT_LEFT: Int = 1 shl 2
    const val SHIFT_RIGHT: Int = 1 shl 3
    const val ALT_LEFT: Int = 1 shl 4
    const val ALT_RIGHT: Int = 1 shl 5
    const val META_SUPER: Int = 1 shl 6
    const val FN_KEY: Int = 1 shl 7
    const val CAPS_LOCK: Int = 1 shl 8
}

sealed class ControlFrame {
    data class KeyEventFrame(
        val keyCode: Int,
        val action: Int,
        val metaState: Int,
        val scanCode: Int = 0,
        val repeatCount: Int = 0
    ) : ControlFrame()

    data class ModifierBitmaskFrame(
        val activeBitmask: Int,
        val latchedBitmask: Int
    ) : ControlFrame()

    data class PrecomposeCommitFrame(
        val committedUtf8: String,
        val replaceBeforeCount: Int = 0,
        val newCursorOffset: Int = 1
    ) : ControlFrame()

    data class ExtractedTextSyncFrame(
        val fullFieldText: String,
        val selectionStart: Int,
        val selectionEnd: Int,
        val inputTypeFlags: Int
    ) : ControlFrame()

    data class ClipboardSyncFrame(
        val mimeType: String,
        val utf8Content: String,
        val timestampMs: Long = System.currentTimeMillis()
    ) : ControlFrame()

    data class FileChunkFrame(
        val transferId: Long,
        val chunkIndex: Int,
        val totalChunks: Int,
        val fileName: String,
        val mimeType: String,
        val chunkData: ByteArray
    ) : ControlFrame()

    data class VaultPipeAutoTypeFrame(
        val secretPayload: String,
        val appendEnterKey: Boolean,
        val interKeyDelayMs: Int = 6
    ) : ControlFrame()

    data class WindowOrchestratorCmdFrame(
        val commandId: Int,
        val targetDisplayId: Int = 0,
        val normalizedBoundsLeft: Float = 0f,
        val normalizedBoundsTop: Float = 0f,
        val normalizedBoundsRight: Float = 1f,
        val normalizedBoundsBottom: Float = 1f
    ) : ControlFrame()

    data class CreativeDialCmdFrame(
        val toolMode: Int,
        val stepDelta: Int,
        val precisionTier: Int,
        val argbColor: Int = 0,
        val targetAppPresetId: Int = 0
    ) : ControlFrame()

    data class PresentationOverlayCmdFrame(
        val mode: Int,
        val normalizedX: Float,
        val normalizedY: Float,
        val radiusDp: Float = 96f,
        val zoomFactor: Float = 2.0f
    ) : ControlFrame()
}

sealed class SpatialEvent {
    data class PointerDelta(
        val dx: Float,
        val dy: Float,
        val buttonMask: Int,
        val fingerCount: Int,
        val timestampNanos: Long
    ) : SpatialEvent()

    data class ScrollDelta(
        val horizontalScroll: Float,
        val verticalScroll: Float,
        val isFlingMomentum: Boolean
    ) : SpatialEvent()

    data class PinchZoom(
        val scaleFactorDelta: Float,
        val focusNormalizedX: Float,
        val focusNormalizedY: Float,
        val rotationDeltaRad: Float
    ) : SpatialEvent()

    data class GyroAirMouse(
        val yawDeltaDeg: Float,
        val pitchDeltaDeg: Float,
        val rollAngleDeg: Float,
        val laserTriggerHeld: Boolean
    ) : SpatialEvent()
}

class SpatialCursorIntegrator(
    @Volatile var screenWidthPx: Int = 2560,
    @Volatile var screenHeightPx: Int = 1600,
    @Volatile var baseSensitivity: Float = 1.65f
) {
    @Volatile
    var cursorX: Float = screenWidthPx / 2f
        private set

    @Volatile
    var cursorY: Float = screenHeightPx / 2f
        private set

    private var lastUpdateNanos: Long = 0L

    fun updateScreenBounds(widthPx: Int, heightPx: Int) {
        screenWidthPx = widthPx.coerceAtLeast(320)
        screenHeightPx = heightPx.coerceAtLeast(320)
        cursorX = cursorX.coerceIn(0f, (screenWidthPx - 1).toFloat())
        cursorY = cursorY.coerceIn(0f, (screenHeightPx - 1).toFloat())
    }

    @Synchronized
    fun integrateDelta(dx: Float, dy: Float, timestampNanos: Long): Pair<Float, Float> {
        val dtSeconds = if (lastUpdateNanos == 0L) {
            0.00416f
        } else {
            ((timestampNanos - lastUpdateNanos) / 1_000_000_000f).coerceIn(0.001f, 0.050f)
        }
        lastUpdateNanos = timestampNanos

        val distance = hypot(dx, dy)
        val velocityPxPerSec = distance / dtSeconds

        val accelerationMultiplier = (baseSensitivity * (1.0f + (velocityPxPerSec / 1400f).pow(0.65f)))
            .coerceIn(0.8f, 4.8f)

        val scaledDx = dx * accelerationMultiplier
        val scaledDy = dy * accelerationMultiplier

        cursorX = (cursorX + scaledDx).coerceIn(0f, (screenWidthPx - 1).toFloat())
        cursorY = (cursorY + scaledDy).coerceIn(0f, (screenHeightPx - 1).toFloat())

        return cursorX to cursorY
    }

    @Synchronized
    fun integrateAirMouseGyro(yawDeltaDeg: Float, pitchDeltaDeg: Float): Pair<Float, Float> {
        val pxPerDegreeX = screenWidthPx / 42f
        val pxPerDegreeY = screenHeightPx / 32f
        cursorX = (cursorX + yawDeltaDeg * pxPerDegreeX).coerceIn(0f, (screenWidthPx - 1).toFloat())
        cursorY = (cursorY + pitchDeltaDeg * pxPerDegreeY).coerceIn(0f, (screenHeightPx - 1).toFloat())
        return cursorX to cursorY
    }
}

object BinaryPacketCodec {

    fun encodeControlFrame(frame: ControlFrame): Pair<Byte, ByteArray> {
        return when (frame) {
            is ControlFrame.KeyEventFrame -> {
                val buf = ByteBuffer.allocate(20).order(ByteOrder.BIG_ENDIAN)
                buf.putInt(frame.keyCode)
                buf.putInt(frame.action)
                buf.putInt(frame.metaState)
                buf.putInt(frame.scanCode)
                buf.putInt(frame.repeatCount)
                TcpFrameType.KEY_EVENT to buf.array()
            }

            is ControlFrame.ModifierBitmaskFrame -> {
                val buf = ByteBuffer.allocate(8).order(ByteOrder.BIG_ENDIAN)
                buf.putInt(frame.activeBitmask)
                buf.putInt(frame.latchedBitmask)
                TcpFrameType.MODIFIER_BITMASK to buf.array()
            }

            is ControlFrame.PrecomposeCommitFrame -> {
                val strBytes = frame.committedUtf8.toByteArray(Charsets.UTF_8)
                val buf = ByteBuffer.allocate(12 + strBytes.size).order(ByteOrder.BIG_ENDIAN)
                buf.putInt(frame.replaceBeforeCount)
                buf.putInt(frame.newCursorOffset)
                buf.putInt(strBytes.size)
                buf.put(strBytes)
                TcpFrameType.PRECOMPOSE_COMMIT to buf.array()
            }

            is ControlFrame.ExtractedTextSyncFrame -> {
                val strBytes = frame.fullFieldText.toByteArray(Charsets.UTF_8)
                val buf = ByteBuffer.allocate(16 + strBytes.size).order(ByteOrder.BIG_ENDIAN)
                buf.putInt(frame.selectionStart)
                buf.putInt(frame.selectionEnd)
                buf.putInt(frame.inputTypeFlags)
                buf.putInt(strBytes.size)
                buf.put(strBytes)
                TcpFrameType.EXTRACTED_TEXT_SYNC to buf.array()
            }

            is ControlFrame.ClipboardSyncFrame -> {
                val mimeBytes = frame.mimeType.toByteArray(Charsets.UTF_8)
                val contentBytes = frame.utf8Content.toByteArray(Charsets.UTF_8)
                val buf = ByteBuffer.allocate(16 + mimeBytes.size + contentBytes.size)
                    .order(ByteOrder.BIG_ENDIAN)
                buf.putLong(frame.timestampMs)
                buf.putInt(mimeBytes.size)
                buf.put(mimeBytes)
                buf.putInt(contentBytes.size)
                buf.put(contentBytes)
                TcpFrameType.CLIPBOARD_SYNC to buf.array()
            }

            is ControlFrame.FileChunkFrame -> {
                val nameBytes = frame.fileName.toByteArray(Charsets.UTF_8)
                val mimeBytes = frame.mimeType.toByteArray(Charsets.UTF_8)
                val buf = ByteBuffer.allocate(
                    28 + nameBytes.size + mimeBytes.size + frame.chunkData.size
                ).order(ByteOrder.BIG_ENDIAN)
                buf.putLong(frame.transferId)
                buf.putInt(frame.chunkIndex)
                buf.putInt(frame.totalChunks)
                buf.putInt(nameBytes.size)
                buf.put(nameBytes)
                buf.putInt(mimeBytes.size)
                buf.put(mimeBytes)
                buf.putInt(frame.chunkData.size)
                buf.put(frame.chunkData)
                TcpFrameType.FILE_CHUNK to buf.array()
            }

            is ControlFrame.VaultPipeAutoTypeFrame -> {
                val secretBytes = frame.secretPayload.toByteArray(Charsets.UTF_8)
                val buf = ByteBuffer.allocate(9 + secretBytes.size).order(ByteOrder.BIG_ENDIAN)
                buf.put(if (frame.appendEnterKey) 1.toByte() else 0.toByte())
                buf.putInt(frame.interKeyDelayMs)
                buf.putInt(secretBytes.size)
                buf.put(secretBytes)
                TcpFrameType.VAULT_PIPE_AUTOTYPE to buf.array()
            }

            is ControlFrame.WindowOrchestratorCmdFrame -> {
                val buf = ByteBuffer.allocate(24).order(ByteOrder.BIG_ENDIAN)
                buf.putInt(frame.commandId)
                buf.putInt(frame.targetDisplayId)
                buf.putFloat(frame.normalizedBoundsLeft)
                buf.putFloat(frame.normalizedBoundsTop)
                buf.putFloat(frame.normalizedBoundsRight)
                buf.putFloat(frame.normalizedBoundsBottom)
                TcpFrameType.WINDOW_ORCHESTRATOR_CMD to buf.array()
            }

            is ControlFrame.CreativeDialCmdFrame -> {
                val buf = ByteBuffer.allocate(20).order(ByteOrder.BIG_ENDIAN)
                buf.putInt(frame.toolMode)
                buf.putInt(frame.stepDelta)
                buf.putInt(frame.precisionTier)
                buf.putInt(frame.argbColor)
                buf.putInt(frame.targetAppPresetId)
                TcpFrameType.CREATIVE_DIAL_CMD to buf.array()
            }

            is ControlFrame.PresentationOverlayCmdFrame -> {
                val buf = ByteBuffer.allocate(20).order(ByteOrder.BIG_ENDIAN)
                buf.putInt(frame.mode)
                buf.putFloat(frame.normalizedX)
                buf.putFloat(frame.normalizedY)
                buf.putFloat(frame.radiusDp)
                buf.putFloat(frame.zoomFactor)
                TcpFrameType.PRESENTATION_OVERLAY_CMD to buf.array()
            }
        }
    }

    fun decodeControlFrame(frameType: Byte, bytes: ByteArray): ControlFrame? {
        val buf = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN)
        return when (frameType) {
            TcpFrameType.KEY_EVENT -> ControlFrame.KeyEventFrame(
                keyCode = buf.int,
                action = buf.int,
                metaState = buf.int,
                scanCode = buf.int,
                repeatCount = buf.int
            )

            TcpFrameType.MODIFIER_BITMASK -> ControlFrame.ModifierBitmaskFrame(
                activeBitmask = buf.int,
                latchedBitmask = buf.int
            )

            TcpFrameType.PRECOMPOSE_COMMIT -> {
                val replaceBefore = buf.int
                val cursorOffset = buf.int
                val len = buf.int
                val strBytes = ByteArray(len)
                buf.get(strBytes)
                ControlFrame.PrecomposeCommitFrame(
                    committedUtf8 = String(strBytes, Charsets.UTF_8),
                    replaceBeforeCount = replaceBefore,
                    newCursorOffset = cursorOffset
                )
            }

            TcpFrameType.EXTRACTED_TEXT_SYNC -> {
                val selStart = buf.int
                val selEnd = buf.int
                val flags = buf.int
                val len = buf.int
                val strBytes = ByteArray(len)
                buf.get(strBytes)
                ControlFrame.ExtractedTextSyncFrame(
                    fullFieldText = String(strBytes, Charsets.UTF_8),
                    selectionStart = selStart,
                    selectionEnd = selEnd,
                    inputTypeFlags = flags
                )
            }

            TcpFrameType.CLIPBOARD_SYNC -> {
                val ts = buf.long
                val mimeLen = buf.int
                val mimeBytes = ByteArray(mimeLen)
                buf.get(mimeBytes)
                val contentLen = buf.int
                val contentBytes = ByteArray(contentLen)
                buf.get(contentBytes)
                ControlFrame.ClipboardSyncFrame(
                    mimeType = String(mimeBytes, Charsets.UTF_8),
                    utf8Content = String(contentBytes, Charsets.UTF_8),
                    timestampMs = ts
                )
            }

            TcpFrameType.FILE_CHUNK -> {
                val transferId = buf.long
                val chunkIdx = buf.int
                val totalChunks = buf.int
                val nameLen = buf.int
                val nameBytes = ByteArray(nameLen)
                buf.get(nameBytes)
                val mimeLen = buf.int
                val mimeBytes = ByteArray(mimeLen)
                buf.get(mimeBytes)
                val dataLen = buf.int
                val chunkData = ByteArray(dataLen)
                buf.get(chunkData)
                ControlFrame.FileChunkFrame(
                    transferId = transferId,
                    chunkIndex = chunkIdx,
                    totalChunks = totalChunks,
                    fileName = String(nameBytes, Charsets.UTF_8),
                    mimeType = String(mimeBytes, Charsets.UTF_8),
                    chunkData = chunkData
                )
            }

            TcpFrameType.VAULT_PIPE_AUTOTYPE -> {
                val appendEnter = buf.get() == 1.toByte()
                val delayMs = buf.int
                val len = buf.int
                val secretBytes = ByteArray(len)
                buf.get(secretBytes)
                ControlFrame.VaultPipeAutoTypeFrame(
                    secretPayload = String(secretBytes, Charsets.UTF_8),
                    appendEnterKey = appendEnter,
                    interKeyDelayMs = delayMs
                )
            }

            TcpFrameType.WINDOW_ORCHESTRATOR_CMD -> ControlFrame.WindowOrchestratorCmdFrame(
                commandId = buf.int,
                targetDisplayId = buf.int,
                normalizedBoundsLeft = buf.float,
                normalizedBoundsTop = buf.float,
                normalizedBoundsRight = buf.float,
                normalizedBoundsBottom = buf.float
            )

            TcpFrameType.CREATIVE_DIAL_CMD -> ControlFrame.CreativeDialCmdFrame(
                toolMode = buf.int,
                stepDelta = buf.int,
                precisionTier = buf.int,
                argbColor = buf.int,
                targetAppPresetId = buf.int
            )

            TcpFrameType.PRESENTATION_OVERLAY_CMD -> ControlFrame.PresentationOverlayCmdFrame(
                mode = buf.int,
                normalizedX = buf.float,
                normalizedY = buf.float,
                radiusDp = buf.float,
                zoomFactor = buf.float
            )

            else -> null
        }
    }

    fun encodeSpatialEvent(event: SpatialEvent): Pair<Byte, ByteArray> {
        return when (event) {
            is SpatialEvent.PointerDelta -> {
                val buf = ByteBuffer.allocate(24).order(ByteOrder.BIG_ENDIAN)
                buf.putFloat(event.dx)
                buf.putFloat(event.dy)
                buf.putInt(event.buttonMask)
                buf.putInt(event.fingerCount)
                buf.putLong(event.timestampNanos)
                UdpDatagramType.POINTER_DELTA to buf.array()
            }

            is SpatialEvent.ScrollDelta -> {
                val buf = ByteBuffer.allocate(9).order(ByteOrder.BIG_ENDIAN)
                buf.putFloat(event.horizontalScroll)
                buf.putFloat(event.verticalScroll)
                buf.put(if (event.isFlingMomentum) 1.toByte() else 0.toByte())
                UdpDatagramType.SCROLL_DELTA to buf.array()
            }

            is SpatialEvent.PinchZoom -> {
                val buf = ByteBuffer.allocate(16).order(ByteOrder.BIG_ENDIAN)
                buf.putFloat(event.scaleFactorDelta)
                buf.putFloat(event.focusNormalizedX)
                buf.putFloat(event.focusNormalizedY)
                buf.putFloat(event.rotationDeltaRad)
                UdpDatagramType.PINCH_ZOOM to buf.array()
            }

            is SpatialEvent.GyroAirMouse -> {
                val buf = ByteBuffer.allocate(13).order(ByteOrder.BIG_ENDIAN)
                buf.putFloat(event.yawDeltaDeg)
                buf.putFloat(event.pitchDeltaDeg)
                buf.putFloat(event.rollAngleDeg)
                buf.put(if (event.laserTriggerHeld) 1.toByte() else 0.toByte())
                UdpDatagramType.GYRO_AIR_MOUSE to buf.array()
            }
        }
    }

    fun decodeSpatialEvent(packetType: Byte, bytes: ByteArray): SpatialEvent? {
        val buf = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN)
        return when (packetType) {
            UdpDatagramType.POINTER_DELTA -> SpatialEvent.PointerDelta(
                dx = buf.float,
                dy = buf.float,
                buttonMask = buf.int,
                fingerCount = buf.int,
                timestampNanos = buf.long
            )

            UdpDatagramType.SCROLL_DELTA -> SpatialEvent.ScrollDelta(
                horizontalScroll = buf.float,
                verticalScroll = buf.float,
                isFlingMomentum = buf.get() == 1.toByte()
            )

            UdpDatagramType.PINCH_ZOOM -> SpatialEvent.PinchZoom(
                scaleFactorDelta = buf.float,
                focusNormalizedX = buf.float,
                focusNormalizedY = buf.float,
                rotationDeltaRad = buf.float
            )

            UdpDatagramType.GYRO_AIR_MOUSE -> SpatialEvent.GyroAirMouse(
                yawDeltaDeg = buf.float,
                pitchDeltaDeg = buf.float,
                rollAngleDeg = buf.float,
                laserTriggerHeld = buf.get() == 1.toByte()
            )

            else -> null
        }
    }
}

class DualChannelSocketTransport(
    private val cryptoEngine: ZeroTrustCryptoEngine,
    val cursorIntegrator: SpatialCursorIntegrator = SpatialCursorIntegrator()
) {
    private val transportScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val tcpWriteMutex = Mutex()

    private var tcpServerSocket: ServerSocket? = null
    private var activeTcpSocket: Socket? = null
    private var tcpOutputStream: DataOutputStream? = null
    private var tcpInputStream: DataInputStream? = null

    private var udpSocket: DatagramSocket? = null
    @Volatile
    private var remoteUdpAddress: InetSocketAddress? = null

    private var tcpReaderJob: Job? = null
    private var heartbeatJob: Job? = null
    private var udpReceiverJob: Job? = null

    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()

    private val _rttMicroseconds = MutableStateFlow(0L)
    val rttMicroseconds: StateFlow<Long> = _rttMicroseconds.asStateFlow()

    private val _incomingControlFrames = MutableSharedFlow<ControlFrame>(
        replay = 0,
        extraBufferCapacity = 256,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val incomingControlFrames: SharedFlow<ControlFrame> = _incomingControlFrames.asSharedFlow()

    private val _incomingSpatialEvents = MutableSharedFlow<SpatialEvent>(
        replay = 0,
        extraBufferCapacity = 512,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val incomingSpatialEvents: SharedFlow<SpatialEvent> = _incomingSpatialEvents.asSharedFlow()

    companion object {
        const val DEFAULT_TCP_PORT = 43821
        const val DEFAULT_UDP_PORT = 43822
        const val HEARTBEAT_INTERVAL_MS = 5_000L
    }

    suspend fun startReceiverServer(
        tcpPort: Int = DEFAULT_TCP_PORT,
        udpPort: Int = DEFAULT_UDP_PORT
    ) = withContext(Dispatchers.IO) {
        stopAll()

        val server = ServerSocket()
        server.reuseAddress = true
        server.bind(InetSocketAddress(tcpPort))
        tcpServerSocket = server

        val datagram = DatagramSocket(null)
        datagram.reuseAddress = true
        datagram.trafficClass = 0x28
        datagram.bind(InetSocketAddress(udpPort))
        udpSocket = datagram

        startUdpReceiveLoop(datagram)

        transportScope.launch {
            while (isActive && !server.isClosed) {
                try {
                    val clientSocket = server.accept()
                    configureLowLatencyTcpSocket(clientSocket)
                    handleIncomingReceiverHandshake(clientSocket)
                } catch (e: Exception) {
                    if (!server.isClosed) {
                        delay(100L)
                    }
                }
            }
        }
    }

    suspend fun connectAsTransmitter(
        hostAddress: String,
        tcpPort: Int = DEFAULT_TCP_PORT,
        udpPort: Int = DEFAULT_UDP_PORT,
        remotePublicKeyBase64: String,
        pin6Digit: String,
        connectTimeoutMs: Int = 150
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            val socket = Socket()
            configureLowLatencyTcpSocket(socket)
            socket.connect(InetSocketAddress(hostAddress, tcpPort), connectTimeoutMs)

            val dataIn = DataInputStream(socket.getInputStream())
            val dataOut = DataOutputStream(socket.getOutputStream())

            val localPubBytes = cryptoEngine.getLocalPublicKeyBase64().toByteArray(Charsets.UTF_8)
            dataOut.writeByte(TcpFrameType.ECDH_HANDSHAKE_INIT.toInt())
            dataOut.writeInt(localPubBytes.size)
            dataOut.write(localPubBytes)
            dataOut.flush()

            cryptoEngine.establishZeroTrustSession(
                remotePublicKeyBase64 = remotePublicKeyBase64,
                pin6Digit = pin6Digit,
                isInitiator = true
            )

            socket.soTimeout = 2_500
            val ackType = dataIn.readByte()
            val ackLen = dataIn.readInt()
            if (ackType != TcpFrameType.ECDH_HANDSHAKE_ACK || ackLen <= 0 || ackLen > 4096) {
                socket.close()
                return@withContext false
            }
            val ackEncrypted = ByteArray(ackLen)
            dataIn.readFully(ackEncrypted)
            val ackPlain = cryptoEngine.decryptTcpFrame(TcpFrameType.ECDH_HANDSHAKE_ACK, ackEncrypted)
            val ackString = String(ackPlain, Charsets.UTF_8)
            if (ackString != "OMNIPAD_ACK_OK") {
                socket.close()
                return@withContext false
            }

            socket.soTimeout = 0
            activeTcpSocket = socket
            tcpInputStream = dataIn
            tcpOutputStream = dataOut

            val datagram = DatagramSocket()
            datagram.trafficClass = 0x28
            udpSocket = datagram
            remoteUdpAddress = InetSocketAddress(InetAddress.getByName(hostAddress), udpPort)

            _isConnected.value = true
            startTcpReaderLoop(socket, dataIn)
            startHeartbeatLoop()
            startUdpReceiveLoop(datagram)
            true
        } catch (e: Exception) {
            false
        }
    }

    private suspend fun handleIncomingReceiverHandshake(socket: Socket) {
        try {
            socket.soTimeout = 2_500
            val dataIn = DataInputStream(socket.getInputStream())
            val dataOut = DataOutputStream(socket.getOutputStream())

            val frameType = dataIn.readByte()
            val payloadLen = dataIn.readInt()
            if (frameType != TcpFrameType.ECDH_HANDSHAKE_INIT || payloadLen <= 0 || payloadLen > 4096) {
                socket.close()
                return
            }
            val remotePubKeyBytes = ByteArray(payloadLen)
            dataIn.readFully(remotePubKeyBytes)
            val remotePubKeyBase64 = String(remotePubKeyBytes, Charsets.UTF_8)

            cryptoEngine.establishZeroTrustSession(
                remotePublicKeyBase64 = remotePubKeyBase64,
                pin6Digit = cryptoEngine.getActivePin6Digit(),
                isInitiator = false
            )

            val ackBytes = "OMNIPAD_ACK_OK".toByteArray(Charsets.UTF_8)
            val encryptedAck = cryptoEngine.encryptTcpFrame(TcpFrameType.ECDH_HANDSHAKE_ACK, ackBytes)
            tcpWriteMutex.withLock {
                dataOut.writeByte(TcpFrameType.ECDH_HANDSHAKE_ACK.toInt())
                dataOut.writeInt(encryptedAck.size)
                dataOut.write(encryptedAck)
                dataOut.flush()
            }

            socket.soTimeout = 0
            activeTcpSocket?.close()
            activeTcpSocket = socket
            tcpInputStream = dataIn
            tcpOutputStream = dataOut
            remoteUdpAddress = InetSocketAddress(socket.inetAddress, DEFAULT_UDP_PORT)

            _isConnected.value = true
            startTcpReaderLoop(socket, dataIn)
            startHeartbeatLoop()
        } catch (e: Exception) {
            socket.close()
        }
    }

    private fun configureLowLatencyTcpSocket(socket: Socket) {
        socket.tcpNoDelay = true
        socket.keepAlive = true
        socket.trafficClass = 0x10
        socket.sendBufferSize = 65536
        socket.receiveBufferSize = 65536
    }

    suspend fun sendControlFrame(frame: ControlFrame): Boolean = withContext(Dispatchers.IO) {
        if (!_isConnected.value || !cryptoEngine.isSessionEstablished()) return@withContext false
        val out = tcpOutputStream ?: return@withContext false

        return@withContext try {
            val (frameType, rawPayload) = BinaryPacketCodec.encodeControlFrame(frame)
            val encryptedPayload = cryptoEngine.encryptTcpFrame(frameType, rawPayload)

            tcpWriteMutex.withLock {
                out.writeByte(frameType.toInt())
                out.writeInt(encryptedPayload.size)
                out.write(encryptedPayload)
                out.flush()
            }
            true
        } catch (e: Exception) {
            handleDisconnect()
            false
        }
    }

    fun sendSpatialEventFast(event: SpatialEvent) {
        if (!_isConnected.value || !cryptoEngine.isSessionEstablished()) return
        val socket = udpSocket ?: return
        val target = remoteUdpAddress ?: return

        transportScope.launch {
            try {
                val (packetType, rawBytes) = BinaryPacketCodec.encodeSpatialEvent(event)
                val datagramBytes = cryptoEngine.encryptUdpDatagram(packetType, rawBytes)
                val packet = DatagramPacket(datagramBytes, datagramBytes.size, target)
                socket.send(packet)
            } catch (_: Exception) {
            }
        }
    }

    private fun startTcpReaderLoop(socket: Socket, dataIn: DataInputStream) {
        tcpReaderJob?.cancel()
        tcpReaderJob = transportScope.launch {
            try {
                while (isActive && !socket.isClosed) {
                    val frameType = dataIn.readByte()
                    val length = dataIn.readInt()
                    if (length <= 0 || length > 2 * 1024 * 1024) {
                        throw SecurityException("Invalid TCP frame length: $length")
                    }
                    val encryptedBytes = ByteArray(length)
                    dataIn.readFully(encryptedBytes)

                    val plaintext = cryptoEngine.decryptTcpFrame(frameType, encryptedBytes)

                    when (frameType) {
                        TcpFrameType.HEARTBEAT_PING -> {
                            sendRawEncryptedFrame(TcpFrameType.HEARTBEAT_PONG, plaintext)
                        }

                        TcpFrameType.HEARTBEAT_PONG -> {
                            if (plaintext.size >= 8) {
                                val sentNanos = ByteBuffer.wrap(plaintext)
                                    .order(ByteOrder.BIG_ENDIAN)
                                    .long
                                val rttUs = (System.nanoTime() - sentNanos) / 1_000L
                                _rttMicroseconds.value = rttUs.coerceAtLeast(1L)
                            }
                        }

                        else -> {
                            BinaryPacketCodec.decodeControlFrame(frameType, plaintext)?.let { decoded ->
                                _incomingControlFrames.tryEmit(decoded)
                            }
                        }
                    }
                }
            } catch (_: EOFException) {
                handleDisconnect()
            } catch (_: Exception) {
                handleDisconnect()
            }
        }
    }

    private fun startHeartbeatLoop() {
        heartbeatJob?.cancel()
        heartbeatJob = transportScope.launch {
            while (isActive && _isConnected.value) {
                delay(HEARTBEAT_INTERVAL_MS)
                val pingPayload = ByteBuffer.allocate(8)
                    .order(ByteOrder.BIG_ENDIAN)
                    .putLong(System.nanoTime())
                    .array()
                val ok = sendRawEncryptedFrame(TcpFrameType.HEARTBEAT_PING, pingPayload)
                if (!ok) {
                    handleDisconnect()
                    break
                }
            }
        }
    }

    private fun startUdpReceiveLoop(datagramSocket: DatagramSocket) {
        udpReceiverJob?.cancel()
        udpReceiverJob = transportScope.launch {
            val receiveBuffer = ByteArray(512)
            while (isActive && !datagramSocket.isClosed) {
                try {
                    val packet = DatagramPacket(receiveBuffer, receiveBuffer.size)
                    datagramSocket.receive(packet)

                    val decrypted = cryptoEngine.decryptUdpDatagram(packet.data, packet.length)
                        ?: continue

                    if (remoteUdpAddress == null || remoteUdpAddress?.address != packet.address) {
                        remoteUdpAddress = InetSocketAddress(packet.address, packet.port)
                    }

                    val (packetType, plaintext) = decrypted
                    val spatialEvent = BinaryPacketCodec.decodeSpatialEvent(packetType, plaintext)
                        ?: continue

                    when (spatialEvent) {
                        is SpatialEvent.PointerDelta -> {
                            cursorIntegrator.integrateDelta(
                                spatialEvent.dx,
                                spatialEvent.dy,
                                spatialEvent.timestampNanos
                            )
                        }
                        is SpatialEvent.GyroAirMouse -> {
                            cursorIntegrator.integrateAirMouseGyro(
                                spatialEvent.yawDeltaDeg,
                                spatialEvent.pitchDeltaDeg
                            )
                        }
                        else -> Unit
                    }

                    _incomingSpatialEvents.tryEmit(spatialEvent)
                } catch (_: Exception) {
                    if (datagramSocket.isClosed) break
                }
            }
        }
    }

    private suspend fun sendRawEncryptedFrame(frameType: Byte, plaintext: ByteArray): Boolean {
        val out = tcpOutputStream ?: return false
        return try {
            val encrypted = cryptoEngine.encryptTcpFrame(frameType, plaintext)
            tcpWriteMutex.withLock {
                out.writeByte(frameType.toInt())
                out.writeInt(encrypted.size)
                out.write(encrypted)
                out.flush()
            }
            true
        } catch (_: Exception) {
            false
        }
    }

    private fun handleDisconnect() {
        _isConnected.value = false
        try {
            activeTcpSocket?.close()
        } catch (_: Exception) {
        }
        activeTcpSocket = null
        tcpInputStream = null
        tcpOutputStream = null
    }

    suspend fun stopAll() {
        _isConnected.value = false
        heartbeatJob?.cancelAndJoin()
        tcpReaderJob?.cancelAndJoin()
        udpReceiverJob?.cancelAndJoin()
        try {
            activeTcpSocket?.close()
            tcpServerSocket?.close()
            udpSocket?.close()
        } catch (_: Exception) {
        }
        activeTcpSocket = null
        tcpServerSocket = null
        udpSocket = null
    }
}
""",

    "app/src/main/java/com/omnipad/deck/core/mesh/TriModalMeshCoordinator.kt": """package com.omnipad.deck.core.mesh

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothHidDevice
import android.bluetooth.BluetoothHidDeviceAppQosSettings
import android.bluetooth.BluetoothHidDeviceAppSdpSettings
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothProfile
import android.content.Context
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import android.net.wifi.p2p.WifiP2pConfig
import android.net.wifi.p2p.WifiP2pGroup
import android.net.wifi.p2p.WifiP2pInfo
import android.net.wifi.p2p.WifiP2pManager
import android.os.Build
import android.os.Looper
import android.view.KeyEvent
import com.omnipad.deck.core.crypto.MultiPathPairingPayload
import com.omnipad.deck.core.crypto.ZeroTrustCryptoEngine
import com.omnipad.deck.core.haptics.AdaptiveHapticEngine
import com.omnipad.deck.core.network.ControlFrame
import com.omnipad.deck.core.network.DualChannelSocketTransport
import com.omnipad.deck.core.network.SpatialEvent
import com.omnipad.deck.core.permissions.RuntimePermissionOrchestrator
import com.omnipad.deck.receiver.ShizukuPointerAndKeyInjector
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import java.net.Inet4Address
import java.net.NetworkInterface
import java.util.Collections
import java.util.concurrent.Executors
import kotlin.coroutines.resume
import kotlin.math.roundToInt

object OmniPadRuntimeRegistry {
    val cryptoEngine = ZeroTrustCryptoEngine()
    val socketTransport = DualChannelSocketTransport(cryptoEngine)
    val shizukuInjector = ShizukuPointerAndKeyInjector()

    @Volatile
    private var hapticEngineInstance: AdaptiveHapticEngine? = null

    @Volatile
    private var meshCoordinatorInstance: TriModalMeshCoordinator? = null

    fun getHapticEngine(context: Context): AdaptiveHapticEngine {
        return hapticEngineInstance ?: synchronized(this) {
            hapticEngineInstance ?: AdaptiveHapticEngine(context.applicationContext).also {
                hapticEngineInstance = it
            }
        }
    }

    fun getMeshCoordinator(context: Context): TriModalMeshCoordinator {
        return meshCoordinatorInstance ?: synchronized(this) {
            meshCoordinatorInstance ?: TriModalMeshCoordinator(
                context = context.applicationContext,
                cryptoEngine = cryptoEngine,
                transport = socketTransport
            ).also {
                meshCoordinatorInstance = it
            }
        }
    }
}

enum class TransportPathMode {
    DISCONNECTED,
    LAN_WIFI_TCP_UDP,
    HOTSPOT_LOOPBACK_TCP_UDP,
    WIFI_DIRECT_P2P_TCP_UDP,
    BLUETOOTH_HID_SERVERLESS
}

enum class ReceiverTierMode {
    TIER_1_IME_ONLY,
    TIER_2_SHIZUKU_PRIVILEGED,
    TIER_3_BLUETOOTH_OR_ACCESSIBILITY
}

@SuppressLint("MissingPermission")
class TriModalMeshCoordinator(
    private val context: Context,
    private val cryptoEngine: ZeroTrustCryptoEngine,
    val transport: DualChannelSocketTransport
) {
    private val meshScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val hidExecutor = Executors.newSingleThreadExecutor()

    private val _activeTransportPath = MutableStateFlow(TransportPathMode.DISCONNECTED)
    val activeTransportPath: StateFlow<TransportPathMode> = _activeTransportPath.asStateFlow()

    private val _receiverTierMode = MutableStateFlow(ReceiverTierMode.TIER_1_IME_ONLY)
    val receiverTierMode: StateFlow<ReceiverTierMode> = _receiverTierMode.asStateFlow()

    private val _lastFailoverLatencyMs = MutableStateFlow(0L)
    val lastFailoverLatencyMs: StateFlow<Long> = _lastFailoverLatencyMs.asStateFlow()

    private val _discoveredLanPeers = MutableStateFlow<List<NsdServiceInfo>>(emptyList())
    val discoveredLanPeers: StateFlow<List<NsdServiceInfo>> = _discoveredLanPeers.asStateFlow()

    private var lastPairingPayload: MultiPathPairingPayload? = null

    private val nsdManager: NsdManager by lazy {
        context.getSystemService(Context.NSD_SERVICE) as NsdManager
    }
    private var nsdRegistrationListener: NsdManager.RegistrationListener? = null
    private var nsdDiscoveryListener: NsdManager.DiscoveryListener? = null

    private val wifiP2pManager: WifiP2pManager? by lazy {
        context.getSystemService(Context.WIFI_P2P_SERVICE) as? WifiP2pManager
    }
    private var wifiP2pChannel: WifiP2pManager.Channel? = null
    private var wifiP2pGroupOwnerIp: String = "192.168.49.1"
    private var localWifiDirectIdentifier: String = Build.MODEL

    private val bluetoothManager: BluetoothManager? by lazy {
        context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
    }
    private val bluetoothAdapter: BluetoothAdapter? by lazy {
        bluetoothManager?.adapter
    }
    private var bluetoothHidDevice: BluetoothHidDevice? = null
    private var connectedBluetoothHost: BluetoothDevice? = null
    private var currentHidModifierByte: Byte = 0
    private val activeHidKeys = LinkedHashSet<Byte>()

    companion object {
        const val NSD_SERVICE_TYPE = "_omnipad._tcp."
        const val NSD_SERVICE_NAME_PREFIX = "OmniPadDeck-"
        const val CLIENT_ISOLATION_SYN_TIMEOUT_MS = 150

        const val REPORT_ID_KEYBOARD: Int = 1
        const val REPORT_ID_MOUSE: Int = 2

        val HID_COMBO_KEYBOARD_MOUSE_DESCRIPTOR: ByteArray = byteArrayOf(
            0x05.toByte(), 0x01.toByte(),
            0x09.toByte(), 0x06.toByte(),
            0xA1.toByte(), 0x01.toByte(),
            0x85.toByte(), 0x01.toByte(),
            0x05.toByte(), 0x07.toByte(),
            0x19.toByte(), 0xE0.toByte(),
            0x29.toByte(), 0xE7.toByte(),
            0x15.toByte(), 0x00.toByte(),
            0x25.toByte(), 0x01.toByte(),
            0x75.toByte(), 0x01.toByte(),
            0x95.toByte(), 0x08.toByte(),
            0x81.toByte(), 0x02.toByte(),
            0x95.toByte(), 0x01.toByte(),
            0x75.toByte(), 0x08.toByte(),
            0x81.toByte(), 0x01.toByte(),
            0x95.toByte(), 0x06.toByte(),
            0x75.toByte(), 0x08.toByte(),
            0x15.toByte(), 0x00.toByte(),
            0x25.toByte(), 0x65.toByte(),
            0x05.toByte(), 0x07.toByte(),
            0x19.toByte(), 0x00.toByte(),
            0x29.toByte(), 0x65.toByte(),
            0x81.toByte(), 0x00.toByte(),
            0xC0.toByte(),

            0x05.toByte(), 0x01.toByte(),
            0x09.toByte(), 0x02.toByte(),
            0xA1.toByte(), 0x01.toByte(),
            0x85.toByte(), 0x02.toByte(),
            0x09.toByte(), 0x01.toByte(),
            0xA1.toByte(), 0x00.toByte(),
            0x05.toByte(), 0x09.toByte(),
            0x19.toByte(), 0x01.toByte(),
            0x29.toByte(), 0x03.toByte(),
            0x15.toByte(), 0x00.toByte(),
            0x25.toByte(), 0x01.toByte(),
            0x95.toByte(), 0x03.toByte(),
            0x75.toByte(), 0x01.toByte(),
            0x81.toByte(), 0x02.toByte(),
            0x95.toByte(), 0x01.toByte(),
            0x75.toByte(), 0x05.toByte(),
            0x81.toByte(), 0x01.toByte(),
            0x05.toByte(), 0x01.toByte(),
            0x09.toByte(), 0x30.toByte(),
            0x09.toByte(), 0x31.toByte(),
            0x09.toByte(), 0x38.toByte(),
            0x15.toByte(), 0x81.toByte(),
            0x25.toByte(), 0x7F.toByte(),
            0x75.toByte(), 0x08.toByte(),
            0x95.toByte(), 0x03.toByte(),
            0x81.toByte(), 0x06.toByte(),
            0xC0.toByte(),
            0xC0.toByte()
        )
    }

    init {
        wifiP2pChannel = wifiP2pManager?.initialize(context, Looper.getMainLooper(), null)

        meshScope.launch {
            transport.isConnected.collect { connected ->
                if (!connected && _activeTransportPath.value != TransportPathMode.DISCONNECTED &&
                    _activeTransportPath.value != TransportPathMode.BLUETOOTH_HID_SERVERLESS
                ) {
                    val savedPayload = lastPairingPayload
                    if (savedPayload != null) {
                        triggerAutomaticSub200msFailover(savedPayload)
                    } else {
                        _activeTransportPath.value = TransportPathMode.DISCONNECTED
                    }
                }
            }
        }
    }

    fun refreshReceiverTierCapability() {
        _receiverTierMode.value = when {
            OmniPadRuntimeRegistry.shizukuInjector.isShizukuReady() -> {
                ReceiverTierMode.TIER_2_SHIZUKU_PRIVILEGED
            }
            connectedBluetoothHost != null -> {
                ReceiverTierMode.TIER_3_BLUETOOTH_OR_ACCESSIBILITY
            }
            else -> {
                ReceiverTierMode.TIER_1_IME_ONLY
            }
        }
    }

    suspend fun startTabletReceiverMesh(
        tcpPort: Int = DualChannelSocketTransport.DEFAULT_TCP_PORT,
        udpPort: Int = DualChannelSocketTransport.DEFAULT_UDP_PORT
    ): MultiPathPairingPayload = withContext(Dispatchers.IO) {
        val (pubKeyBase64, pin6Digit) = cryptoEngine.rotateEphemeralIdentity()
        transport.startReceiverServer(tcpPort, udpPort)

        registerNsdService(tcpPort)
        createAutonomousWifiDirectGroup()

        val lanIps = enumerateAllLocalIpAddresses()
        val btMac = getLocalBluetoothAddressSafe()

        MultiPathPairingPayload(
            deviceName = "${Build.MANUFACTURER} ${Build.MODEL}",
            lanAddresses = lanIps,
            tcpControlPort = tcpPort,
            udpSpatialPort = udpPort,
            wifiDirectDeviceName = Build.MODEL,
            wifiDirectMacOrPeerId = localWifiDirectIdentifier,
            bluetoothHidMac = btMac,
            ecdhPublicKeyBase64 = pubKeyBase64,
            pin6Digit = pin6Digit
        ).also {
            lastPairingPayload = it
        }
    }

    suspend fun connectFromTransmitterWithFailover(
        payload: MultiPathPairingPayload
    ): TransportPathMode = withContext(Dispatchers.IO) {
        lastPairingPayload = payload
        val startTimeMs = System.currentTimeMillis()

        val candidateIps = payload.lanAddresses.distinct()
        if (candidateIps.isNotEmpty()) {
            val winningIp = raceLanTcpSynProbes(
                ips = candidateIps,
                tcpPort = payload.tcpControlPort,
                udpPort = payload.udpSpatialPort,
                remotePubKeyBase64 = payload.ecdhPublicKeyBase64,
                pin6Digit = payload.pin6Digit,
                timeoutMs = CLIENT_ISOLATION_SYN_TIMEOUT_MS
            )
            if (winningIp != null) {
                val pathMode = if (winningIp.startsWith("192.168.43.") ||
                    winningIp.startsWith("192.168.137.")
                ) {
                    TransportPathMode.HOTSPOT_LOOPBACK_TCP_UDP
                } else {
                    TransportPathMode.LAN_WIFI_TCP_UDP
                }
                _activeTransportPath.value = pathMode
                _lastFailoverLatencyMs.value = System.currentTimeMillis() - startTimeMs
                return@withContext pathMode
            }
        }

        return@withContext triggerAutomaticSub200msFailover(payload, startTimeMs)
    }

    private suspend fun triggerAutomaticSub200msFailover(
        payload: MultiPathPairingPayload,
        failoverStartEpochMs: Long = System.currentTimeMillis()
    ): TransportPathMode = withContext(Dispatchers.IO) {
        val p2pSuccess = transport.connectAsTransmitter(
            hostAddress = wifiP2pGroupOwnerIp,
            tcpPort = payload.tcpControlPort,
            udpPort = payload.udpSpatialPort,
            remotePublicKeyBase64 = payload.ecdhPublicKeyBase64,
            pin6Digit = payload.pin6Digit,
            connectTimeoutMs = 120
        )
        if (p2pSuccess) {
            _activeTransportPath.value = TransportPathMode.WIFI_DIRECT_P2P_TCP_UDP
            _lastFailoverLatencyMs.value = System.currentTimeMillis() - failoverStartEpochMs
            return@withContext TransportPathMode.WIFI_DIRECT_P2P_TCP_UDP
        }

        if (payload.wifiDirectMacOrPeerId.isNotBlank()) {
            connectWifiDirectPeer(payload.wifiDirectMacOrPeerId)
        }

        val btReady = activateBluetoothHidFallback(payload.bluetoothHidMac)
        if (btReady) {
            _activeTransportPath.value = TransportPathMode.BLUETOOTH_HID_SERVERLESS
            _lastFailoverLatencyMs.value = System.currentTimeMillis() - failoverStartEpochMs
            return@withContext TransportPathMode.BLUETOOTH_HID_SERVERLESS
        }

        _activeTransportPath.value = TransportPathMode.DISCONNECTED
        TransportPathMode.DISCONNECTED
    }

    private suspend fun raceLanTcpSynProbes(
        ips: List<String>,
        tcpPort: Int,
        udpPort: Int,
        remotePubKeyBase64: String,
        pin6Digit: String,
        timeoutMs: Int
    ): String? = coroutineScope {
        for (ip in ips) {
            val connected = transport.connectAsTransmitter(
                hostAddress = ip,
                tcpPort = tcpPort,
                udpPort = udpPort,
                remotePublicKeyBase64 = remotePubKeyBase64,
                pin6Digit = pin6Digit,
                connectTimeoutMs = timeoutMs
            )
            if (connected) return@coroutineScope ip
        }
        null
    }

    suspend fun dispatchKeyEvent(
        keyCode: Int,
        action: Int,
        metaState: Int,
        scanCode: Int = 0
    ) {
        if (_activeTransportPath.value == TransportPathMode.BLUETOOTH_HID_SERVERLESS) {
            sendBluetoothHidKeyEvent(keyCode, action, metaState)
        } else {
            transport.sendControlFrame(
                ControlFrame.KeyEventFrame(
                    keyCode = keyCode,
                    action = action,
                    metaState = metaState,
                    scanCode = scanCode
                )
            )
        }
    }

    fun dispatchPointerDelta(
        dx: Float,
        dy: Float,
        buttonMask: Int,
        fingerCount: Int,
        timestampNanos: Long = System.nanoTime()
    ) {
        if (_activeTransportPath.value == TransportPathMode.BLUETOOTH_HID_SERVERLESS) {
            sendBluetoothHidMouseReport(
                dx = dx.roundToInt().coerceIn(-127, 127),
                dy = dy.roundToInt().coerceIn(-127, 127),
                wheel = 0,
                buttonMask = buttonMask
            )
        } else {
            transport.sendSpatialEventFast(
                SpatialEvent.PointerDelta(
                    dx = dx,
                    dy = dy,
                    buttonMask = buttonMask,
                    fingerCount = fingerCount,
                    timestampNanos = timestampNanos
                )
            )
        }
    }

    private fun registerNsdService(port: Int) {
        unregisterNsdService()
        val serviceInfo = NsdServiceInfo().apply {
            serviceName = "$NSD_SERVICE_NAME_PREFIX${Build.MODEL.replace(" ", "")}"
            serviceType = NSD_SERVICE_TYPE
            setPort(port)
        }
        val listener = object : NsdManager.RegistrationListener {
            override fun onServiceRegistered(info: NsdServiceInfo) {}
            override fun onRegistrationFailed(info: NsdServiceInfo, errorCode: Int) {}
            override fun onServiceUnregistered(info: NsdServiceInfo) {}
            override fun onUnregistrationFailed(info: NsdServiceInfo, errorCode: Int) {}
        }
        nsdRegistrationListener = listener
        try {
            nsdManager.registerService(serviceInfo, NsdManager.PROTOCOL_DNS_SD, listener)
        } catch (_: Exception) {
        }
    }

    fun startNsdDiscovery() {
        stopNsdDiscovery()
        val listener = object : NsdManager.DiscoveryListener {
            override fun onDiscoveryStarted(regType: String) {}
            override fun onServiceFound(service: NsdServiceInfo) {
                if (service.serviceType.contains("_omnipad")) {
                    resolveNsdService(service)
                }
            }
            override fun onServiceLost(service: NsdServiceInfo) {
                _discoveredLanPeers.value = _discoveredLanPeers.value.filterNot {
                    it.serviceName == service.serviceName
                }
            }
            override fun onDiscoveryStopped(serviceType: String) {}
            override fun onStartDiscoveryFailed(serviceType: String, errorCode: Int) {}
            override fun onStopDiscoveryFailed(serviceType: String, errorCode: Int) {}
        }
        nsdDiscoveryListener = listener
        try {
            nsdManager.discoverServices(NSD_SERVICE_TYPE, NsdManager.PROTOCOL_DNS_SD, listener)
        } catch (_: Exception) {
        }
    }

    private fun resolveNsdService(service: NsdServiceInfo) {
        try {
            @Suppress("DEPRECATION")
            nsdManager.resolveService(service, object : NsdManager.ResolveListener {
                override fun onResolveFailed(serviceInfo: NsdServiceInfo, errorCode: Int) {}
                override fun onServiceResolved(resolvedInfo: NsdServiceInfo) {
                    val updated = (_discoveredLanPeers.value + resolvedInfo)
                        .distinctBy { it.serviceName }
                    _discoveredLanPeers.value = updated
                }
            })
        } catch (_: Exception) {
        }
    }

    private fun unregisterNsdService() {
        nsdRegistrationListener?.let {
            try {
                nsdManager.unregisterService(it)
            } catch (_: Exception) {
            }
        }
        nsdRegistrationListener = null
    }

    fun stopNsdDiscovery() {
        nsdDiscoveryListener?.let {
            try {
                nsdManager.stopServiceDiscovery(it)
            } catch (_: Exception) {
            }
        }
        nsdDiscoveryListener = null
    }

    private fun createAutonomousWifiDirectGroup() {
        if (!RuntimePermissionOrchestrator.hasWifiP2pPermissions(context)) return
        val manager = wifiP2pManager ?: return
        val channel = wifiP2pChannel ?: return

        try {
            manager.createGroup(channel, object : WifiP2pManager.ActionListener {
                override fun onSuccess() {
                    manager.requestGroupInfo(channel) { group: WifiP2pGroup? ->
                        localWifiDirectIdentifier = group?.owner?.deviceAddress ?: Build.MODEL
                    }
                }
                override fun onFailure(reason: Int) {}
            })
        } catch (_: SecurityException) {
        }
    }

    private suspend fun connectWifiDirectPeer(deviceAddress: String): Boolean {
        if (!RuntimePermissionOrchestrator.hasWifiP2pPermissions(context)) return false
        val manager = wifiP2pManager ?: return false
        val channel = wifiP2pChannel ?: return false

        return withTimeoutOrNull(180L) {
            suspendCancellableCoroutine { cont ->
                try {
                    val config = WifiP2pConfig().apply {
                        this.deviceAddress = deviceAddress
                    }
                    manager.connect(channel, config, object : WifiP2pManager.ActionListener {
                        override fun onSuccess() {
                            manager.requestConnectionInfo(channel) { info: WifiP2pInfo? ->
                                info?.groupOwnerAddress?.hostAddress?.let { ip ->
                                    wifiP2pGroupOwnerIp = ip
                                }
                                if (cont.isActive) cont.resume(true)
                            }
                        }
                        override fun onFailure(reason: Int) {
                            if (cont.isActive) cont.resume(false)
                        }
                    })
                } catch (_: SecurityException) {
                    if (cont.isActive) cont.resume(false)
                }
            }
        } ?: false
    }

    fun initializeBluetoothHidPeripheral() {
        if (!RuntimePermissionOrchestrator.hasBluetoothPermissions(context)) return
        val adapter = bluetoothAdapter ?: return
        if (!adapter.isEnabled) return

        adapter.getProfileProxy(
            context,
            object : BluetoothProfile.ServiceListener {
                override fun onServiceConnected(profile: Int, proxy: BluetoothProfile) {
                    if (profile == BluetoothProfile.HID_DEVICE) {
                        val hidDevice = proxy as BluetoothHidDevice
                        bluetoothHidDevice = hidDevice
                        registerHidAppDescriptor(hidDevice)
                    }
                }

                override fun onServiceDisconnected(profile: Int) {
                    if (profile == BluetoothProfile.HID_DEVICE) {
                        bluetoothHidDevice = null
                        connectedBluetoothHost = null
                    }
                }
            },
            BluetoothProfile.HID_DEVICE
        )
    }

    private fun registerHidAppDescriptor(hidDevice: BluetoothHidDevice) {
        if (!RuntimePermissionOrchestrator.hasBluetoothPermissions(context)) return

        val sdpSettings = BluetoothHidDeviceAppSdpSettings(
            "OmniPad Deck Combo",
            "Wi-Fi + Bluetooth HID Keyboard & Trackpad",
            "OmniPad",
            BluetoothHidDevice.SUBCLASS1_COMBO,
            HID_COMBO_KEYBOARD_MOUSE_DESCRIPTOR
        )

        val qosSettings = BluetoothHidDeviceAppQosSettings(
            BluetoothHidDeviceAppQosSettings.SERVICE_BEST_EFFORT,
            800,
            9,
            0,
            11250,
            BluetoothHidDeviceAppQosSettings.MAX
        )

        hidDevice.registerApp(
            sdpSettings,
            null,
            qosSettings,
            hidExecutor,
            object : BluetoothHidDevice.Callback() {
                override fun onConnectionStateChanged(device: BluetoothDevice, state: Int) {
                    if (state == BluetoothProfile.STATE_CONNECTED) {
                        connectedBluetoothHost = device
                        refreshReceiverTierCapability()
                    } else if (state == BluetoothProfile.STATE_DISCONNECTED) {
                        if (connectedBluetoothHost == device) {
                            connectedBluetoothHost = null
                        }
                        refreshReceiverTierCapability()
                    }
                }
            }
        )
    }

    private fun activateBluetoothHidFallback(targetBtMac: String): Boolean {
        if (!RuntimePermissionOrchestrator.hasBluetoothPermissions(context)) return false
        val hid = bluetoothHidDevice ?: run {
            initializeBluetoothHidPeripheral()
            return false
        }
        val existingHost = connectedBluetoothHost
        if (existingHost != null) return true

        val bondedTarget = bluetoothAdapter?.bondedDevices?.firstOrNull {
            targetBtMac.isNotBlank() && it.address.equals(targetBtMac, ignoreCase = true)
        } ?: bluetoothAdapter?.bondedDevices?.firstOrNull()

        return if (bondedTarget != null) {
            val initiated = hid.connect(bondedTarget)
            if (initiated) {
                connectedBluetoothHost = bondedTarget
            }
            initiated
        } else {
            false
        }
    }

    private fun sendBluetoothHidKeyEvent(keyCode: Int, action: Int, metaState: Int) {
        if (!RuntimePermissionOrchestrator.hasBluetoothPermissions(context)) return
        val hid = bluetoothHidDevice ?: return
        val host = connectedBluetoothHost ?: return

        var modByte = 0
        if ((metaState and KeyEvent.META_CTRL_ON) != 0 || keyCode == KeyEvent.KEYCODE_CTRL_LEFT) {
            modByte = modByte or 0x01
        }
        if ((metaState and KeyEvent.META_SHIFT_ON) != 0 || keyCode == KeyEvent.KEYCODE_SHIFT_LEFT) {
            modByte = modByte or 0x02
        }
        if ((metaState and KeyEvent.META_ALT_ON) != 0 || keyCode == KeyEvent.KEYCODE_ALT_LEFT) {
            modByte = modByte or 0x04
        }
        if ((metaState and KeyEvent.META_META_ON) != 0 || keyCode == KeyEvent.KEYCODE_META_LEFT) {
            modByte = modByte or 0x08
        }
        currentHidModifierByte = modByte.toByte()

        val usageId = androidKeyCodeToUsbHidUsage(keyCode)
        if (usageId != 0.toByte()) {
            if (action == KeyEvent.ACTION_DOWN) {
                if (activeHidKeys.size < 6) activeHidKeys.add(usageId)
            } else if (action == KeyEvent.ACTION_UP) {
                activeHidKeys.remove(usageId)
            }
        }

        val report = ByteArray(8)
        report[0] = if (action == KeyEvent.ACTION_UP && activeHidKeys.isEmpty()) 0 else currentHidModifierByte
        report[1] = 0
        var index = 2
        for (k in activeHidKeys) {
            if (index < 8) {
                report[index++] = k
            }
        }
        hid.sendReport(host, REPORT_ID_KEYBOARD, report)
    }

    fun sendBluetoothHidMouseReport(dx: Int, dy: Int, wheel: Int, buttonMask: Int) {
        if (!RuntimePermissionOrchestrator.hasBluetoothPermissions(context)) return
        val hid = bluetoothHidDevice ?: return
        val host = connectedBluetoothHost ?: return

        val report = byteArrayOf(
            (buttonMask and 0x07).toByte(),
            dx.coerceIn(-127, 127).toByte(),
            dy.coerceIn(-127, 127).toByte(),
            wheel.coerceIn(-127, 127).toByte()
        )
        hid.sendReport(host, REPORT_ID_MOUSE, report)
    }

    private fun androidKeyCodeToUsbHidUsage(keyCode: Int): Byte {
        val code: Int = when (keyCode) {
            in KeyEvent.KEYCODE_A..KeyEvent.KEYCODE_Z -> 0x04 + (keyCode - KeyEvent.KEYCODE_A)
            in KeyEvent.KEYCODE_1..KeyEvent.KEYCODE_9 -> 0x1E + (keyCode - KeyEvent.KEYCODE_1)
            KeyEvent.KEYCODE_0 -> 0x27
            KeyEvent.KEYCODE_ENTER, KeyEvent.KEYCODE_NUMPAD_ENTER -> 0x28
            KeyEvent.KEYCODE_ESCAPE -> 0x29
            KeyEvent.KEYCODE_DEL -> 0x2A
            KeyEvent.KEYCODE_TAB -> 0x2B
            KeyEvent.KEYCODE_SPACE -> 0x2C
            KeyEvent.KEYCODE_MINUS -> 0x2D
            KeyEvent.KEYCODE_EQUALS -> 0x2E
            KeyEvent.KEYCODE_LEFT_BRACKET -> 0x2F
            KeyEvent.KEYCODE_RIGHT_BRACKET -> 0x30
            KeyEvent.KEYCODE_BACKSLASH -> 0x31
            KeyEvent.KEYCODE_SEMICOLON -> 0x33
            KeyEvent.KEYCODE_APOSTROPHE -> 0x34
            KeyEvent.KEYCODE_GRAVE -> 0x35
            KeyEvent.KEYCODE_COMMA -> 0x36
            KeyEvent.KEYCODE_PERIOD -> 0x37
            KeyEvent.KEYCODE_SLASH -> 0x38
            KeyEvent.KEYCODE_CAPS_LOCK -> 0x39
            in KeyEvent.KEYCODE_F1..KeyEvent.KEYCODE_F12 -> 0x3A + (keyCode - KeyEvent.KEYCODE_F1)
            KeyEvent.KEYCODE_INSERT -> 0x49
            KeyEvent.KEYCODE_HOME -> 0x4A
            KeyEvent.KEYCODE_PAGE_UP -> 0x4B
            KeyEvent.KEYCODE_FORWARD_DEL -> 0x4C
            KeyEvent.KEYCODE_END -> 0x4D
            KeyEvent.KEYCODE_PAGE_DOWN -> 0x4E
            KeyEvent.KEYCODE_DPAD_RIGHT -> 0x4F
            KeyEvent.KEYCODE_DPAD_LEFT -> 0x50
            KeyEvent.KEYCODE_DPAD_DOWN -> 0x51
            KeyEvent.KEYCODE_DPAD_UP -> 0x52
            else -> 0x00
        }
        return code.toByte()
    }

    private fun enumerateAllLocalIpAddresses(): List<String> {
        val result = mutableListOf<String>()
        try {
            val interfaces = Collections.list(NetworkInterface.getNetworkInterfaces())
            for (nif in interfaces) {
                if (!nif.isUp || nif.isLoopback) continue
                for (addr in Collections.list(nif.inetAddresses)) {
                    if (addr is Inet4Address && !addr.isLoopbackAddress) {
                        addr.hostAddress?.let { result.add(it) }
                    }
                }
            }
        } catch (_: Exception) {
        }
        return result.distinct()
    }

    private fun getLocalBluetoothAddressSafe(): String {
        return try {
            if (RuntimePermissionOrchestrator.hasBluetoothPermissions(context)) {
                bluetoothAdapter?.address?.takeIf { it != "02:00:00:00:00:00" } ?: ""
            } else {
                ""
            }
        } catch (_: Exception) {
            ""
        }
    }

    suspend fun shutdownMesh() {
        stopNsdDiscovery()
        unregisterNsdService()
        transport.stopAll()
        _activeTransportPath.value = TransportPathMode.DISCONNECTED
    }
}
""",

    "app/src/main/java/com/omnipad/deck/receiver/WifiZeroHeightImeService.kt": """package com.omnipad.deck.receiver

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.Color
import android.graphics.Rect
import android.graphics.Region
import android.graphics.drawable.GradientDrawable
import android.inputmethodservice.InputMethodService
import android.os.SystemClock
import android.util.TypedValue
import android.view.Gravity
import android.view.KeyCharacterMap
import android.view.KeyEvent
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.ExtractedTextRequest
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView
import com.omnipad.deck.core.mesh.OmniPadRuntimeRegistry
import com.omnipad.deck.core.network.ControlFrame
import com.omnipad.deck.core.network.ModifierBits
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

class WifiZeroHeightImeService : InputMethodService() {

    private val imeScope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private var controlFrameJob: Job? = null
    private var extractedText120HzJob: Job? = null

    private lateinit var rootFrame: FrameLayout
    private lateinit var floatingEdgeMicroPill: TextView
    private lateinit var fallbackKeyboardContainer: LinearLayout

    private var isFallbackKeyboardExpanded: Boolean = false
    private val pillTouchableRect = Rect()

    private var activeModifierMetaState: Int = 0
    private var lastSyncedText: String = ""
    private var lastSyncedSelStart: Int = -1
    private var lastSyncedSelEnd: Int = -1

    override fun onCreate() {
        super.onCreate()
        startControlFrameListener()
    }

    override fun onEvaluateFullscreenMode(): Boolean = false

    override fun onCreateInputView(): View {
        val density = resources.displayMetrics.density

        rootFrame = FrameLayout(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.TRANSPARENT)
        }

        floatingEdgeMicroPill = TextView(this).apply {
            text = "⌨ OmniPad 0px"
            setTextColor(Color.WHITE)
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 11f)
            gravity = Gravity.CENTER
            val padH = (12 * density).toInt()
            val padV = (6 * density).toInt()
            setPadding(padH, padV, padH, padV)
            background = GradientDrawable().apply {
                shape = GradientDrawable.RECTANGLE
                cornerRadius = 24f * density
                setColor(Color.parseColor("#DD1E293B"))
                setStroke((1.5f * density).toInt(), Color.parseColor("#38BDF8"))
            }
            elevation = 8f * density
        }

        val pillParams = FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.WRAP_CONTENT,
            FrameLayout.LayoutParams.WRAP_CONTENT,
            Gravity.BOTTOM or Gravity.END
        ).apply {
            rightMargin = (12 * density).toInt()
            bottomMargin = (28 * density).toInt()
        }
        rootFrame.addView(floatingEdgeMicroPill, pillParams)

        setupDraggableEdgePill(floatingEdgeMicroPill)

        fallbackKeyboardContainer = buildEmergencyFallbackKeyboard(density)
        fallbackKeyboardContainer.visibility = View.GONE
        val fallbackParams = FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.WRAP_CONTENT,
            Gravity.BOTTOM
        )
        rootFrame.addView(fallbackKeyboardContainer, fallbackParams)

        return rootFrame
    }

    override fun onComputeInsets(outInsets: Insets?) {
        super.onComputeInsets(outInsets)
        if (outInsets == null) return

        val decorView = window?.window?.decorView ?: return
        val totalHeight = decorView.height

        if (!isFallbackKeyboardExpanded && ::floatingEdgeMicroPill.isInitialized) {
            outInsets.contentTopInsets = totalHeight
            outInsets.visibleTopInsets = totalHeight
            outInsets.touchableInsets = Insets.TOUCHABLE_INSETS_REGION

            val loc = IntArray(2)
            floatingEdgeMicroPill.getLocationInWindow(loc)
            pillTouchableRect.set(
                loc[0],
                loc[1],
                loc[0] + floatingEdgeMicroPill.width,
                loc[1] + floatingEdgeMicroPill.height
            )
            outInsets.touchableRegion.set(Region(pillTouchableRect))
        } else if (::fallbackKeyboardContainer.isInitialized) {
            val kbTop = totalHeight - fallbackKeyboardContainer.height
            outInsets.contentTopInsets = kbTop
            outInsets.visibleTopInsets = kbTop
            outInsets.touchableInsets = Insets.TOUCHABLE_INSETS_CONTENT
            outInsets.touchableRegion.setEmpty()
        }
    }

    override fun onStartInputView(info: EditorInfo?, restarting: Boolean) {
        super.onStartInputView(info, restarting)
        updatePillConnectionBadge(OmniPadRuntimeRegistry.socketTransport.isConnected.value)
        start120HzExtractedTextStreamer(info)
    }

    override fun onFinishInputView(finishingInput: Boolean) {
        super.onFinishInputView(finishingInput)
        extractedText120HzJob?.cancel()
    }

    private fun startControlFrameListener() {
        controlFrameJob?.cancel()
        controlFrameJob = imeScope.launch {
            launch {
                OmniPadRuntimeRegistry.socketTransport.isConnected.collect { connected ->
                    updatePillConnectionBadge(connected)
                }
            }

            OmniPadRuntimeRegistry.socketTransport.incomingControlFrames.collect { frame ->
                when (frame) {
                    is ControlFrame.KeyEventFrame -> handleIncomingKeyEvent(frame)
                    is ControlFrame.ModifierBitmaskFrame -> {
                        activeModifierMetaState = translateModifierBitmaskToAndroidMeta(
                            frame.activeBitmask or frame.latchedBitmask
                        )
                    }
                    is ControlFrame.PrecomposeCommitFrame -> handlePrecomposeBatchCommit(frame)
                    is ControlFrame.ClipboardSyncFrame -> handleIncomingClipboardSync(frame)
                    is ControlFrame.VaultPipeAutoTypeFrame -> {
                        dispatchVaultPipeSyntheticKeys(
                            secret = frame.secretPayload,
                            appendEnter = frame.appendEnterKey,
                            interKeyDelayMs = frame.interKeyDelayMs
                        )
                    }
                    is ControlFrame.CreativeDialCmdFrame -> handleCreativeDialShortcutInIme(frame)
                    else -> Unit
                }
            }
        }
    }

    private fun handleIncomingKeyEvent(frame: ControlFrame.KeyEventFrame) {
        val ic = currentInputConnection ?: return
        val now = SystemClock.uptimeMillis()
        val combinedMeta = frame.metaState or activeModifierMetaState

        val event = KeyEvent(
            now,
            now,
            frame.action,
            frame.keyCode,
            frame.repeatCount,
            combinedMeta,
            KeyCharacterMap.VIRTUAL_KEYBOARD,
            frame.scanCode,
            KeyEvent.FLAG_SOFT_KEYBOARD or KeyEvent.FLAG_KEEP_TOUCH_MODE
        )
        ic.sendKeyEvent(event)
    }

    private fun handlePrecomposeBatchCommit(frame: ControlFrame.PrecomposeCommitFrame) {
        val ic = currentInputConnection ?: return
        ic.beginBatchEdit()
        if (frame.replaceBeforeCount > 0) {
            ic.deleteSurroundingText(frame.replaceBeforeCount, 0)
        }
        ic.commitText(frame.committedUtf8, frame.newCursorOffset)
        ic.endBatchEdit()
    }

    private fun handleIncomingClipboardSync(frame: ControlFrame.ClipboardSyncFrame) {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("OmniPad Sync", frame.utf8Content)
        clipboard.setPrimaryClip(clip)
    }

    private fun dispatchVaultPipeSyntheticKeys(
        secret: String,
        appendEnter: Boolean,
        interKeyDelayMs: Int
    ) {
        val ic = currentInputConnection ?: return
        imeScope.launch {
            val kcm = KeyCharacterMap.load(KeyCharacterMap.VIRTUAL_KEYBOARD)
            val events: Array<KeyEvent>? = kcm.getEvents(secret.toCharArray())

            if (events != null) {
                for (ev in events) {
                    val now = SystemClock.uptimeMillis()
                    val timedEvent = KeyEvent(
                        now,
                        now,
                        ev.action,
                        ev.keyCode,
                        ev.repeatCount,
                        ev.metaState,
                        KeyCharacterMap.VIRTUAL_KEYBOARD,
                        ev.scanCode,
                        KeyEvent.FLAG_SOFT_KEYBOARD or KeyEvent.FLAG_KEEP_TOUCH_MODE
                    )
                    ic.sendKeyEvent(timedEvent)
                    if (ev.action == KeyEvent.ACTION_UP && interKeyDelayMs > 0) {
                        delay(interKeyDelayMs.toLong())
                    }
                }
            } else {
                ic.commitText(secret, 1)
            }

            if (appendEnter) {
                val now = SystemClock.uptimeMillis()
                ic.sendKeyEvent(KeyEvent(now, now, KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_ENTER, 0))
                ic.sendKeyEvent(KeyEvent(now, now, KeyEvent.ACTION_UP, KeyEvent.KEYCODE_ENTER, 0))
            }
        }
    }

    private fun handleCreativeDialShortcutInIme(frame: ControlFrame.CreativeDialCmdFrame) {
        if (OmniPadRuntimeRegistry.shizukuInjector.isShizukuReady()) return
        val ic = currentInputConnection ?: return
        val now = SystemClock.uptimeMillis()

        if (frame.toolMode == 1) {
            val bracketKey = if (frame.stepDelta >= 0) {
                KeyEvent.KEYCODE_RIGHT_BRACKET
            } else {
                KeyEvent.KEYCODE_LEFT_BRACKET
            }
            val meta = when (frame.precisionTier)
