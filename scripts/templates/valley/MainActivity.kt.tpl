package __PACKAGE__

import android.app.PendingIntent
import android.content.Intent
import android.content.pm.ShortcutInfo
import android.content.pm.ShortcutManager
import android.graphics.BitmapFactory
import android.graphics.drawable.Icon
import android.os.Build
import android.os.Bundle
import android.util.Base64
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val channelName = "com.allinone.valley/company_shortcut"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            channelName,
        ).setMethodCallHandler { call, result ->
            when (call.method) {
                "isSupported" -> result.success(isSupported())
                "initialCompanyId" -> result.success(intent?.getStringExtra("companyId"))
                "pin" -> {
                    val companyId = call.argument<String>("companyId")
                    val companyName = call.argument<String>("companyName")
                    val variant = call.argument<String>("variant") ?: "consumer"
                    val iconBase64 = call.argument<String>("iconBase64")
                    if (companyId.isNullOrBlank() || companyName.isNullOrBlank() || iconBase64.isNullOrBlank()) {
                        result.error("invalid_arguments", "Dados obrigatórios ausentes.", null)
                    } else {
                        result.success(pin(companyId, companyName, variant, iconBase64))
                    }
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun isSupported(): Boolean =
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.O &&
            getSystemService(ShortcutManager::class.java)?.isRequestPinShortcutSupported == true

    private fun pin(
        companyId: String,
        companyName: String,
        variant: String,
        iconBase64: String,
    ): Boolean {
        if (!isSupported() || Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return false
        val bytes = try {
            Base64.decode(iconBase64, Base64.DEFAULT)
        } catch (_: IllegalArgumentException) {
            return false
        }
        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size) ?: return false
        val shortcutManager = getSystemService(ShortcutManager::class.java) ?: return false
        val shortcutId = "valley-$variant-company-$companyId"
        val launchIntent = Intent(this, MainActivity::class.java).apply {
            action = Intent.ACTION_VIEW
            putExtra("companyId", companyId)
            putExtra("shortcutSource", "company_launcher_shortcut")
            flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
        }
        val shortcut = ShortcutInfo.Builder(this, shortcutId)
            .setShortLabel(if (variant == "rider") "Valley Rider" else "Valley")
            .setLongLabel("${if (variant == "rider") "Valley Rider" else "Valley"} · $companyName")
            .setIcon(Icon.createWithAdaptiveBitmap(bitmap))
            .setIntent(launchIntent)
            .build()

        val callback = PendingIntent.getBroadcast(
            this,
            shortcutId.hashCode(),
            Intent("$packageName.COMPANY_SHORTCUT_PINNED").setPackage(packageName),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        return shortcutManager.requestPinShortcut(shortcut, callback.intentSender)
    }

    override fun onNewIntent(newIntent: Intent) {
        super.onNewIntent(newIntent)
        intent = newIntent
    }
}
