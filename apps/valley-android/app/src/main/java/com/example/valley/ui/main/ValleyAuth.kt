package com.example.valley.ui.main

import android.content.Context
import org.json.JSONObject
import java.security.MessageDigest
import java.util.Locale

private const val SESSION_PREFS = "valley.session"

data class ValleySession(
  val token: String,
  val userId: String,
  val email: String,
  val source: String,
)

fun valleyDisplayName(email: String): String {
  val localPart = email.substringBefore("@").replace(Regex("[._-]+"), " ")
  return localPart.trim().ifBlank { "Valley User" }
}

fun valleyCpfForEmail(email: String): String = "CPF-" + valleyHash(email).take(12).uppercase(Locale.US)

fun valleyGooglePasswordFor(email: String): String = "valley-" + valleyHash(email.lowercase(Locale.US)).take(16)

fun loadValleySession(context: Context): ValleySession? {
  val prefs = context.getSharedPreferences(SESSION_PREFS, Context.MODE_PRIVATE)
  val token = prefs.getString("token", null) ?: return null
  val userId = prefs.getString("user_id", null) ?: return null
  val email = prefs.getString("email", null) ?: return null
  val source = prefs.getString("source", "email") ?: "email"
  return ValleySession(token = token, userId = userId, email = email, source = source)
}

fun saveValleySession(context: Context, session: ValleySession) {
  context.getSharedPreferences(SESSION_PREFS, Context.MODE_PRIVATE).edit()
    .putString("token", session.token)
    .putString("user_id", session.userId)
    .putString("email", session.email)
    .putString("source", session.source)
    .apply()
}

fun clearValleySession(context: Context) {
  context.getSharedPreferences(SESSION_PREFS, Context.MODE_PRIVATE).edit().clear().apply()
}

fun sessionInjectionScript(session: ValleySession): String {
  return """
    (() => {
      localStorage.setItem('valley.session.token', ${JSONObject.quote(session.token)});
      localStorage.setItem('valley.session.user-id', ${JSONObject.quote(session.userId)});
      localStorage.setItem('valley.session.email', ${JSONObject.quote(session.email)});
      localStorage.setItem('valley.session.source', ${JSONObject.quote(session.source)});
      window.dispatchEvent(new Event('storage'));
    })();
  """.trimIndent()
}

private fun valleyHash(value: String): String {
  val digest = MessageDigest.getInstance("SHA-256").digest(value.toByteArray())
  return digest.joinToString(separator = "") { byte -> "%02x".format(byte) }
}
