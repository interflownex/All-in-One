package com.example.valley.observability

import android.content.Context
import android.os.Bundle
import com.google.firebase.analytics.FirebaseAnalytics
import com.google.firebase.crashlytics.FirebaseCrashlytics
import java.security.MessageDigest

data class TelemetryConsent(
  val decided: Boolean,
  val analytics: Boolean,
  val crashReports: Boolean,
)

object ValleyObservability {
  private const val PREFS = "valley.telemetry.consent"
  private const val DECIDED = "decided"
  private const val ANALYTICS = "analytics"
  private const val CRASH_REPORTS = "crash_reports"
  private val allowedEventName = Regex("[a-z][a-z0-9_]{0,39}")
  private val allowedParameter = Regex("[a-z][a-z0-9_]{0,39}")
  private var appContext: Context? = null

  fun initialize(context: Context) {
    appContext = context.applicationContext
    applyConsent(readConsent(context))
  }

  fun readConsent(context: Context): TelemetryConsent {
    val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
    return TelemetryConsent(
      decided = prefs.getBoolean(DECIDED, false),
      analytics = prefs.getBoolean(ANALYTICS, false),
      crashReports = prefs.getBoolean(CRASH_REPORTS, false),
    )
  }

  fun saveConsent(context: Context, analytics: Boolean, crashReports: Boolean) {
    context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
      .putBoolean(DECIDED, true)
      .putBoolean(ANALYTICS, analytics)
      .putBoolean(CRASH_REPORTS, crashReports)
      .apply()
    applyConsent(TelemetryConsent(true, analytics, crashReports))
  }

  fun recordHttpResult(
    correlationId: String,
    route: String,
    statusCode: Int,
    durationMs: Long,
    failure: Throwable? = null,
  ) {
    val context = appContext ?: return
    val consent = readConsent(context)
    val safeRoute = route.take(80)
    if (consent.analytics) {
      FirebaseAnalytics.getInstance(context).logEvent(
        "api_request_completed",
        Bundle().apply {
          putString("route", safeRoute)
          putLong("status_code", statusCode.toLong())
          putLong("duration_ms", durationMs.coerceAtMost(120_000))
          putString("correlation_id", correlationId)
        },
      )
    }
    if (consent.crashReports) {
      FirebaseCrashlytics.getInstance().apply {
        setCustomKey("correlation_id", correlationId)
        setCustomKey("api_route", safeRoute)
        setCustomKey("api_status_code", statusCode)
        setCustomKey("api_duration_ms", durationMs)
        log("api_request_completed")
        if (failure != null && (statusCode == 0 || statusCode >= 500)) recordException(failure)
      }
    }
  }

  fun recordEvent(name: String, parameters: Map<String, String> = emptyMap()) {
    val context = appContext ?: return
    if (!readConsent(context).analytics || !allowedEventName.matches(name)) return
    FirebaseAnalytics.getInstance(context).logEvent(
      name,
      Bundle().apply {
        parameters.entries.take(10).forEach { (key, value) ->
          if (allowedParameter.matches(key)) putString(key, value.take(80))
        }
      },
    )
  }

  fun anonymizedUserId(value: String): String =
    MessageDigest.getInstance("SHA-256")
      .digest(value.toByteArray(Charsets.UTF_8))
      .joinToString("") { "%02x".format(it) }
      .take(24)

  private fun applyConsent(consent: TelemetryConsent) {
    val context = appContext ?: return
    FirebaseAnalytics.getInstance(context).apply {
      setUserProperty(FirebaseAnalytics.UserProperty.ALLOW_AD_PERSONALIZATION_SIGNALS, "false")
      setAnalyticsCollectionEnabled(consent.decided && consent.analytics)
      if (consent.decided && !consent.analytics) resetAnalyticsData()
    }
    FirebaseCrashlytics.getInstance().apply {
      setCrashlyticsCollectionEnabled(consent.decided && consent.crashReports)
      if (consent.decided && !consent.crashReports) deleteUnsentReports()
    }
  }
}
