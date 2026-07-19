package com.example.valley.security

import android.content.Context
import android.util.Base64
import com.example.valley.BuildConfig
import com.google.android.play.core.integrity.IntegrityManagerFactory
import com.google.android.play.core.integrity.StandardIntegrityManager
import kotlinx.coroutines.tasks.await
import java.security.MessageDigest

/** Gera tokens Standard Play Integrity vinculados ao corpo de cada operacao critica. */
class PlayIntegrityAttestor(context: Context) {
  private val applicationContext = context.applicationContext
  private var provider: StandardIntegrityManager.StandardIntegrityTokenProvider? = null

  suspend fun tokenFor(content: String): String? {
    val cloudProjectNumber = BuildConfig.PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER
    if (cloudProjectNumber == 0L) return null
    val tokenProvider = provider ?: prepare(cloudProjectNumber).also { provider = it }
    return tokenProvider
      .request(
        StandardIntegrityManager.StandardIntegrityTokenRequest.builder()
          .setRequestHash(requestHash(content))
          .build(),
      )
      .await()
      .token()
  }

  private suspend fun prepare(cloudProjectNumber: Long): StandardIntegrityManager.StandardIntegrityTokenProvider {
    return IntegrityManagerFactory.createStandard(applicationContext)
      .prepareIntegrityToken(
        StandardIntegrityManager.PrepareIntegrityTokenRequest.builder()
          .setCloudProjectNumber(cloudProjectNumber)
          .build(),
      )
      .await()
  }

  private fun requestHash(content: String): String {
    val digest = MessageDigest.getInstance("SHA-256").digest(content.toByteArray(Charsets.UTF_8))
    return Base64.encodeToString(digest, Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING)
  }
}
