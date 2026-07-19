package com.example.valley.security

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import org.json.JSONObject
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

data class StoredSession(
  val token: String,
  val refreshToken: String,
  val sessionId: String,
  val userId: String,
  val email: String,
  val source: String,
  val expiresAt: String,
  val refreshExpiresAt: String,
)

/** Persiste a sessao cifrada com uma chave AES-GCM nao exportavel do Android Keystore. */
class SecureSessionStore(private val context: Context) {
  private val preferences = context.getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE)

  fun load(): StoredSession? {
    val encoded = preferences.getString(ENCRYPTED_SESSION, null) ?: return null
    return runCatching {
      val envelope = JSONObject(String(Base64.decode(encoded, Base64.NO_WRAP), Charsets.UTF_8))
      val cipher = Cipher.getInstance(TRANSFORMATION)
      cipher.init(
        Cipher.DECRYPT_MODE,
        getOrCreateKey(),
        GCMParameterSpec(TAG_LENGTH_BITS, Base64.decode(envelope.getString("iv"), Base64.NO_WRAP)),
      )
      val cleartext = cipher.doFinal(Base64.decode(envelope.getString("ciphertext"), Base64.NO_WRAP))
      val session = JSONObject(String(cleartext, Charsets.UTF_8))
      StoredSession(
        token = session.getString("token"),
        refreshToken = session.getString("refresh_token"),
        sessionId = session.getString("session_id"),
        userId = session.getString("user_id"),
        email = session.getString("email"),
        source = session.optString("source", "email"),
        expiresAt = session.getString("expires_at"),
        refreshExpiresAt = session.getString("refresh_expires_at"),
      )
    }.getOrElse {
      clear()
      null
    }
  }

  fun save(session: StoredSession) {
    val cleartext =
      JSONObject()
        .put("token", session.token)
        .put("refresh_token", session.refreshToken)
        .put("session_id", session.sessionId)
        .put("user_id", session.userId)
        .put("email", session.email)
        .put("source", session.source)
        .put("expires_at", session.expiresAt)
        .put("refresh_expires_at", session.refreshExpiresAt)
        .toString()
        .toByteArray(Charsets.UTF_8)
    val cipher = Cipher.getInstance(TRANSFORMATION)
    cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
    val envelope =
      JSONObject()
        .put("iv", Base64.encodeToString(cipher.iv, Base64.NO_WRAP))
        .put("ciphertext", Base64.encodeToString(cipher.doFinal(cleartext), Base64.NO_WRAP))
        .toString()
        .toByteArray(Charsets.UTF_8)
    preferences.edit()
      .putString(ENCRYPTED_SESSION, Base64.encodeToString(envelope, Base64.NO_WRAP))
      .apply()
  }

  fun clear() {
    preferences.edit().remove(ENCRYPTED_SESSION).apply()
  }

  private fun getOrCreateKey(): SecretKey {
    val keyStore = KeyStore.getInstance(KEYSTORE).apply { load(null) }
    (keyStore.getKey(KEY_ALIAS, null) as? SecretKey)?.let { return it }
    return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, KEYSTORE).run {
      init(
        KeyGenParameterSpec.Builder(
          KEY_ALIAS,
          KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
        )
          .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
          .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
          .setKeySize(256)
          .build(),
      )
      generateKey()
    }
  }

  private companion object {
    const val PREFERENCES = "valley.secure.session.v1"
    const val ENCRYPTED_SESSION = "encrypted_session"
    const val KEYSTORE = "AndroidKeyStore"
    const val KEY_ALIAS = "valley_session_aes_gcm_v1"
    const val TRANSFORMATION = "AES/GCM/NoPadding"
    const val TAG_LENGTH_BITS = 128
  }
}
