#!/usr/bin/env python3
"""Materializa a bridge Android para atalhos empresariais Valley."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLUTTER_APP = ROOT / "apps" / "valley-flutter"
KOTLIN_ROOT = FLUTTER_APP / "android" / "app" / "src" / "main" / "kotlin"
CHANNEL = "com.interflownex.valley/company_icon"

KOTLIN_BODY = r'''
package __PACKAGE__

import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.PorterDuff
import android.graphics.RectF
import android.net.Uri
import android.os.Bundle
import android.util.Base64
import androidx.core.content.pm.ShortcutInfoCompat
import androidx.core.content.pm.ShortcutManagerCompat
import androidx.core.graphics.drawable.IconCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val channelName = "com.interflownex.valley/company_icon"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channelName)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "isSupported" -> result.success(
                        ShortcutManagerCompat.isRequestPinShortcutSupported(this)
                    )
                    "pinShortcut" -> {
                        try {
                            result.success(pinShortcut(call.arguments as? Map<*, *> ?: emptyMap<Any, Any>()))
                        } catch (error: Exception) {
                            result.error("PIN_FAILED", "Não foi possível criar o atalho.", error.message)
                        }
                    }
                    "updateShortcut" -> {
                        try {
                            result.success(updateShortcut(call.arguments as? Map<*, *> ?: emptyMap<Any, Any>()))
                        } catch (error: Exception) {
                            result.error("UPDATE_FAILED", "Não foi possível atualizar o atalho.", error.message)
                        }
                    }
                    else -> result.notImplemented()
                }
            }
    }

    private fun pinShortcut(arguments: Map<*, *>): Boolean {
        if (!ShortcutManagerCompat.isRequestPinShortcutSupported(this)) return false
        val shortcut = buildShortcut(arguments)
        return ShortcutManagerCompat.requestPinShortcut(this, shortcut, null)
    }

    private fun updateShortcut(arguments: Map<*, *>): Boolean {
        val shortcut = buildShortcut(arguments)
        return ShortcutManagerCompat.updateShortcuts(this, listOf(shortcut))
    }

    private fun buildShortcut(arguments: Map<*, *>): ShortcutInfoCompat {
        val companyId = required(arguments, "companyId")
        val label = required(arguments, "label").take(30)
        val variant = (arguments["variant"]?.toString() ?: "consumer")
            .lowercase()
            .let { if (it == "rider") "rider" else "consumer" }
        val logoBase64 = required(arguments, "logoBase64")
        val logo = decodeLogo(logoBase64)
        val icon = composeIcon(logo)
        val shortcutId = "valley-$variant-company-$companyId"
        val intent = Intent(this, MainActivity::class.java).apply {
            action = Intent.ACTION_VIEW
            data = Uri.parse("valley://company/${Uri.encode(companyId)}/home?source=custom_launcher_shortcut&variant=$variant")
            putExtra("companyId", companyId)
            putExtra("brandVariant", variant)
        }
        return ShortcutInfoCompat.Builder(this, shortcutId)
            .setShortLabel(label)
            .setLongLabel(label)
            .setIcon(IconCompat.createWithAdaptiveBitmap(icon))
            .setIntent(intent)
            .build()
    }

    private fun decodeLogo(value: String): Bitmap {
        val payload = value.substringAfter("base64,", value)
        val bytes = Base64.decode(payload, Base64.DEFAULT)
        require(bytes.size <= 4 * 1024 * 1024) { "Logomarca acima do limite." }
        return requireNotNull(BitmapFactory.decodeByteArray(bytes, 0, bytes.size)) {
            "Logomarca inválida."
        }
    }

    private fun composeIcon(companyLogo: Bitmap): Bitmap {
        val size = 512
        val output = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(output)
        val paint = Paint(Paint.ANTI_ALIAS_FLAG or Paint.FILTER_BITMAP_FLAG)
        canvas.drawColor(android.graphics.Color.TRANSPARENT, PorterDuff.Mode.CLEAR)

        val background = BitmapFactory.decodeResource(resources, resources.getIdentifier("valley_logo", "drawable", packageName))
        if (background != null) {
            canvas.drawBitmap(background, null, RectF(0f, 0f, size.toFloat(), size.toFloat()), paint)
        }

        val bounds = RectF(size * 0.23f, size * 0.22f, size * 0.77f, size * 0.70f)
        val sourceRatio = companyLogo.width.toFloat() / companyLogo.height.toFloat()
        val boundsRatio = bounds.width() / bounds.height()
        val destination = if (sourceRatio > boundsRatio) {
            val targetHeight = bounds.width() / sourceRatio
            val top = bounds.centerY() - targetHeight / 2f
            RectF(bounds.left, top, bounds.right, top + targetHeight)
        } else {
            val targetWidth = bounds.height() * sourceRatio
            val left = bounds.centerX() - targetWidth / 2f
            RectF(left, bounds.top, left + targetWidth, bounds.bottom)
        }
        canvas.drawBitmap(companyLogo, null, destination, paint)
        return output
    }

    private fun required(arguments: Map<*, *>, key: String): String {
        return arguments[key]?.toString()?.trim()?.takeIf { it.isNotEmpty() }
            ?: throw IllegalArgumentException("Campo obrigatório ausente: $key")
    }
}
'''.strip() + "\n"


def _main_activity() -> Path:
    candidates = sorted(KOTLIN_ROOT.rglob("MainActivity.kt"))
    if len(candidates) != 1:
        raise RuntimeError(f"Esperado exatamente um MainActivity.kt, encontrados: {len(candidates)}")
    return candidates[0]


def materialize() -> Path:
    target = _main_activity()
    current = target.read_text(encoding="utf-8")
    package_match = re.search(r"^package\s+([\w.]+)", current, flags=re.MULTILINE)
    if package_match is None:
        raise RuntimeError("Package Kotlin não encontrado no MainActivity.")
    package_name = package_match.group(1)
    target.write_text(KOTLIN_BODY.replace("__PACKAGE__", package_name), encoding="utf-8")
    return target


def check() -> Path:
    target = _main_activity()
    content = target.read_text(encoding="utf-8")
    required = (
        CHANNEL,
        "ShortcutManagerCompat.requestPinShortcut",
        "ShortcutManagerCompat.updateShortcuts",
        "IconCompat.createWithAdaptiveBitmap",
        "valley://company/",
        "4 * 1024 * 1024",
    )
    missing = [marker for marker in required if marker not in content]
    if missing:
        raise SystemExit(f"Bridge de ícone empresarial incompleta: {', '.join(missing)}")
    return target


if __name__ == "__main__":
    print(materialize())
    print(check())
