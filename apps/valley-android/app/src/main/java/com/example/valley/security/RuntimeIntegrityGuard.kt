package com.example.valley.security

import android.content.Context
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.os.Build
import android.os.Debug
import com.example.valley.BuildConfig
import java.io.File
import java.security.MessageDigest

data class RuntimeIntegrityAssessment(
  val trusted: Boolean,
  val signals: Set<String>,
)

/** Defesa em profundidade. A decisao autoritativa continua no backend via Play Integrity. */
object RuntimeIntegrityGuard {
  private val rootArtifacts =
    listOf(
      "/system/bin/su",
      "/system/xbin/su",
      "/sbin/su",
      "/data/adb/magisk",
      "/data/local/su",
    )
  private val instrumentationMarkers = listOf("frida", "xposed", "substrate", "zygisk")

  fun assess(context: Context): RuntimeIntegrityAssessment {
    if (BuildConfig.DEBUG) return RuntimeIntegrityAssessment(trusted = true, signals = emptySet())
    val signals = linkedSetOf<String>()
    if (isDebuggable(context) || Debug.isDebuggerConnected() || Debug.waitingForDebugger()) signals += "debugger"
    if (hasTracer()) signals += "tracer"
    if (isProbablyEmulator()) signals += "emulator"
    if (Build.TAGS?.contains("test-keys", ignoreCase = true) == true || rootArtifacts.any { File(it).exists() }) {
      signals += "root"
    }
    if (hasInstrumentation()) signals += "instrumentation"
    if (!hasExpectedSigningCertificate(context)) signals += "signature"
    return RuntimeIntegrityAssessment(trusted = signals.isEmpty(), signals = signals)
  }

  private fun isDebuggable(context: Context): Boolean =
    context.applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE != 0

  private fun hasTracer(): Boolean =
    runCatching {
      File("/proc/self/status").useLines { lines ->
        lines.firstOrNull { it.startsWith("TracerPid:") }
          ?.substringAfter(':')
          ?.trim()
          ?.toIntOrNull()
          ?.let { it > 0 } == true
      }
    }.getOrDefault(false)

  private fun hasInstrumentation(): Boolean =
    runCatching {
      File("/proc/self/maps").useLines { lines ->
        lines.any { line -> instrumentationMarkers.any { marker -> line.contains(marker, ignoreCase = true) } }
      }
    }.getOrDefault(false)

  private fun isProbablyEmulator(): Boolean {
    val fingerprint = Build.FINGERPRINT.orEmpty()
    val model = Build.MODEL.orEmpty()
    val brand = Build.BRAND.orEmpty()
    val device = Build.DEVICE.orEmpty()
    val product = Build.PRODUCT.orEmpty()
    val hardware = Build.HARDWARE.orEmpty()
    val manufacturer = Build.MANUFACTURER.orEmpty()
    return fingerprint.startsWith("generic", ignoreCase = true) ||
      fingerprint.contains("emulator", ignoreCase = true) ||
      fingerprint.contains("vbox", ignoreCase = true) ||
      model.contains("google_sdk", ignoreCase = true) ||
      model.contains("emulator", ignoreCase = true) ||
      model.contains("android sdk built for x86", ignoreCase = true) ||
      manufacturer.contains("Genymotion", ignoreCase = true) ||
      (brand.startsWith("generic", ignoreCase = true) && device.startsWith("generic", ignoreCase = true)) ||
      hardware.contains("goldfish", ignoreCase = true) ||
      hardware.contains("ranchu", ignoreCase = true) ||
      product.contains("sdk", ignoreCase = true) ||
      product.contains("emulator", ignoreCase = true) ||
      product.contains("simulator", ignoreCase = true)
  }

  @Suppress("DEPRECATION")
  private fun hasExpectedSigningCertificate(context: Context): Boolean {
    val expected = normalizeCertificateHash(BuildConfig.PLAY_APP_SIGNING_CERT_SHA256)
    if (expected.length != 64) return false
    val expectedBytes = expected.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
      return context.packageManager.hasSigningCertificate(
        context.packageName,
        expectedBytes,
        PackageManager.CERT_INPUT_SHA256,
      )
    }
    val packageInfo = context.packageManager.getPackageInfo(context.packageName, PackageManager.GET_SIGNATURES)
    return packageInfo.signatures.orEmpty().any { signature ->
      MessageDigest.getInstance("SHA-256").digest(signature.toByteArray()).contentEquals(expectedBytes)
    }
  }
}

fun normalizeCertificateHash(value: String): String =
  value.filter { it.isLetterOrDigit() }.lowercase()
