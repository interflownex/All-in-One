package com.example.valley.ui.main

import android.content.Context
import android.provider.Settings
import android.webkit.WebChromeClient
import android.webkit.WebStorage
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.compose.BackHandler
import androidx.credentials.ClearCredentialStateRequest
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import androidx.credentials.exceptions.GetCredentialCancellationException
import androidx.credentials.exceptions.NoCredentialException
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.example.valley.R
import com.example.valley.observability.ValleyObservability
import com.example.valley.security.PlayIntegrityAttestor
import com.example.valley.security.SecureSessionStore
import com.example.valley.security.StoredSession
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.GoogleAuthProvider
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.security.MessageDigest
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale
import java.util.UUID

private const val VALLEY_WEB_URL = "file:///android_asset/valley/index.html"
private const val API_HUB_URL = "https://all-in-one-api-hub.web.app"
private data class ValleySession(
  val token: String,
  val refreshToken: String,
  val sessionId: String,
  val userId: String,
  val email: String,
  val source: String,
  val expiresAt: String,
  val refreshExpiresAt: String,
)

private data class FirebaseGoogleIdentity(
  val email: String,
  val uid: String,
)

fun valleyDisplayName(email: String): String {
  val localPart = email.substringBefore("@").replace(Regex("[._-]+"), " ")
  return localPart.trim().ifBlank { "Valley User" }
}

fun valleyCpfForEmail(email: String): String = "CPF-" + valleyHash(email).take(12).uppercase(Locale.US)

fun valleyGooglePasswordFor(email: String): String = "valley-" + valleyHash(email.lowercase(Locale.US)).take(16)

private fun loadValleySession(context: Context): ValleySession? {
  val stored = SecureSessionStore(context).load() ?: return null
  return ValleySession(
    stored.token,
    stored.refreshToken,
    stored.sessionId,
    stored.userId,
    stored.email,
    stored.source,
    stored.expiresAt,
    stored.refreshExpiresAt,
  )
}

private fun saveValleySession(context: Context, session: ValleySession) {
  SecureSessionStore(context).save(
    StoredSession(
      session.token,
      session.refreshToken,
      session.sessionId,
      session.userId,
      session.email,
      session.source,
      session.expiresAt,
      session.refreshExpiresAt,
    ),
  )
}

private fun clearValleySession(context: Context) {
  SecureSessionStore(context).clear()
}

private fun sessionInjectionScript(session: ValleySession): String {
  return """
    (() => {
      sessionStorage.setItem('valley.session.token', ${JSONObject.quote(session.token)});
      sessionStorage.setItem('valley.session.user-id', ${JSONObject.quote(session.userId)});
      sessionStorage.setItem('valley.session.email', ${JSONObject.quote(session.email)});
      sessionStorage.setItem('valley.session.source', ${JSONObject.quote(session.source)});
      window.dispatchEvent(new Event('storage'));
    })();
  """.trimIndent()
}

@Composable
fun MainScreen(modifier: Modifier = Modifier) {
  val context = LocalContext.current
  val scope = rememberCoroutineScope()
  var session by remember { mutableStateOf(loadValleySession(context)) }
  var authInProgress by rememberSaveable { mutableStateOf(false) }
  var authError by rememberSaveable { mutableStateOf<String?>(null) }
  var telemetryConsent by remember { mutableStateOf(ValleyObservability.readConsent(context)) }
  var showPrivacyControls by rememberSaveable { mutableStateOf(!telemetryConsent.decided) }

  LaunchedEffect(Unit) {
    probeApiAvailability(context)
    session?.let { current ->
      runCatching { refreshValleySession(context, current) }
        .onSuccess { refreshed ->
          saveValleySession(context, refreshed)
          session = refreshed
        }
        .onFailure {
          clearValleySession(context)
          session = null
          authError = "Sua sessao expirou. Entre novamente."
        }
    }
  }

  val activeSession = session

  if (activeSession == null) {
    LoginScreen(
      modifier = modifier,
      loading = authInProgress,
      error = authError,
      onPrivacy = { showPrivacyControls = true },
      onGoogleSignIn = {
        scope.launch {
          authInProgress = true
          authError = null
          runCatching {
            val identity = authenticateWithFirebaseGoogle(context)
            authenticateWithValley(
              context = context,
              email = identity.email,
              password = valleyGooglePasswordFor(identity.uid),
              source = "google",
              createAccount = true,
            )
          }.onSuccess { newSession ->
            saveValleySession(context, newSession)
            session = newSession
          }.onFailure { throwable ->
            authError = throwable.message ?: "Nao foi possivel autenticar agora."
          }
          authInProgress = false
        }
      },
      onEmailSubmit = { email, password, createAccount ->
        scope.launch {
          authInProgress = true
          authError = null
          runCatching {
            authenticateWithValley(
              context = context,
              email = email,
              password = password,
              source = "email",
              createAccount = createAccount,
            )
          }.onSuccess { newSession ->
            saveValleySession(context, newSession)
            session = newSession
          }.onFailure { throwable ->
            authError = throwable.message ?: "Nao foi possivel autenticar agora."
          }
          authInProgress = false
        }
      },
    )
  } else {
    ConsumerShell(
      modifier = modifier,
      session = activeSession,
      onPrivacy = { showPrivacyControls = true },
      onLogout = {
        scope.launch {
          runCatching {
            postJson(
              context,
              "$API_HUB_URL/auth/logout",
              JSONObject()
                .put("refresh_token", activeSession.refreshToken)
                .put("device_fingerprint", valleyDeviceFingerprint(context)),
            )
          }
        }
        clearValleySession(context)
        FirebaseAuth.getInstance().signOut()
        scope.launch {
          runCatching {
            CredentialManager.create(context).clearCredentialState(ClearCredentialStateRequest())
          }
        }
        session = null
      },
    )
  }

  if (showPrivacyControls) {
    PrivacyConsentDialog(
      initialAnalytics = telemetryConsent.analytics,
      initialCrashReports = telemetryConsent.crashReports,
      canDismiss = telemetryConsent.decided,
      onDismiss = { showPrivacyControls = false },
      onSave = { analytics, crashReports ->
        ValleyObservability.saveConsent(context, analytics, crashReports)
        telemetryConsent = ValleyObservability.readConsent(context)
        showPrivacyControls = false
      },
    )
  }
}

private suspend fun probeApiAvailability(context: Context) = withContext(Dispatchers.IO) {
  val correlationId = UUID.randomUUID().toString()
  val startedAt = android.os.SystemClock.elapsedRealtime()
  val connection = (URL("$API_HUB_URL/health").openConnection() as HttpURLConnection).apply {
    requestMethod = "GET"
    connectTimeout = 8_000
    readTimeout = 8_000
    setRequestProperty("Accept", "application/json")
    setRequestProperty("X-Valley-Api-Version", "1")
    setRequestProperty("X-Correlation-Id", correlationId)
  }
  try {
    val statusCode = connection.responseCode
    ValleyObservability.recordHttpResult(
      correlationId = correlationId,
      route = "/health",
      statusCode = statusCode,
      durationMs = android.os.SystemClock.elapsedRealtime() - startedAt,
    )
  } catch (throwable: Throwable) {
    ValleyObservability.recordHttpResult(
      correlationId = correlationId,
      route = "/health",
      statusCode = 0,
      durationMs = android.os.SystemClock.elapsedRealtime() - startedAt,
      failure = throwable,
    )
  } finally {
    connection.disconnect()
  }
}

@Composable
private fun PrivacyConsentDialog(
  initialAnalytics: Boolean,
  initialCrashReports: Boolean,
  canDismiss: Boolean,
  onDismiss: () -> Unit,
  onSave: (Boolean, Boolean) -> Unit,
) {
  var analytics by remember(initialAnalytics) { mutableStateOf(initialAnalytics) }
  var crashReports by remember(initialCrashReports) { mutableStateOf(initialCrashReports) }
  AlertDialog(
    onDismissRequest = { if (canDismiss) onDismiss() },
    title = { Text("Privacidade e telemetria") },
    text = {
      Column {
        Text("Escolha separadamente o que deseja compartilhar. O app funciona normalmente se você recusar ambos.")
        Row(verticalAlignment = Alignment.CenterVertically) {
          Checkbox(checked = analytics, onCheckedChange = { analytics = it })
          Text("Métricas anônimas de uso e disponibilidade")
        }
        Row(verticalAlignment = Alignment.CenterVertically) {
          Checkbox(checked = crashReports, onCheckedChange = { crashReports = it })
          Text("Falhas e diagnósticos técnicos sem conteúdo ou credenciais")
        }
        Text("Publicidade personalizada e identificador de anúncios permanecem desativados.")
      }
    },
    confirmButton = { TextButton(onClick = { onSave(analytics, crashReports) }) { Text("Salvar escolhas") } },
    dismissButton = if (canDismiss) ({ TextButton(onClick = onDismiss) { Text("Cancelar") } }) else null,
  )
}

@Composable
private fun LoginScreen(
  modifier: Modifier = Modifier,
  loading: Boolean,
  error: String?,
  onPrivacy: () -> Unit,
  onGoogleSignIn: () -> Unit,
  onEmailSubmit: (String, String, Boolean) -> Unit,
) {
  var email by rememberSaveable { mutableStateOf("") }
  var password by rememberSaveable { mutableStateOf("") }
  var createAccount by rememberSaveable { mutableStateOf(false) }

  Box(
    modifier =
      modifier
        .fillMaxSize()
        .background(
          Brush.linearGradient(
            colors = listOf(Color(0xFF09061A), Color(0xFF171231), Color(0xFF0B1026)),
          ),
        ),
  ) {
    Column(
      modifier =
        Modifier
          .fillMaxSize()
          .verticalScroll(rememberScrollState())
          .padding(24.dp),
      verticalArrangement = Arrangement.Center,
      horizontalAlignment = Alignment.CenterHorizontally,
    ) {
      Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF111428).copy(alpha = 0.94f)),
        shape = RoundedCornerShape(28.dp),
      ) {
        Column(
          modifier = Modifier.padding(24.dp),
          horizontalAlignment = Alignment.CenterHorizontally,
        ) {
          Image(
            painter = painterResource(id = R.drawable.valley_logo),
            contentDescription = "Valley",
            modifier = Modifier.size(180.dp),
            contentScale = ContentScale.Fit,
          )
          Spacer(modifier = Modifier.height(12.dp))
          Text(
            text = "Valley Consumer",
            style = MaterialTheme.typography.headlineMedium,
            color = Color.White,
            fontWeight = FontWeight.Bold,
          )
          Text(
            text = "Catálogo, pedidos e jornadas do consumidor com login Google ou e-mail.",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFFCBD5E1),
            modifier = Modifier.padding(top = 8.dp),
          )

          Spacer(modifier = Modifier.height(20.dp))

          Button(
            onClick = onGoogleSignIn,
            modifier = Modifier.fillMaxWidth(),
            enabled = !loading,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF8B5CF6), contentColor = Color.White),
          ) {
            Text(if (loading) "Conectando..." else "Continuar com Google")
          }

          Spacer(modifier = Modifier.height(12.dp))

          OutlinedButton(
            onClick = { createAccount = !createAccount },
            modifier = Modifier.fillMaxWidth(),
            enabled = !loading,
          ) {
            Text(if (createAccount) "Já tenho conta" else "Criar conta com e-mail")
          }

          Spacer(modifier = Modifier.height(20.dp))
          OutlinedTextField(
            value = email,
            onValueChange = { email = it.trimStart() },
            modifier = Modifier.fillMaxWidth(),
            label = { Text("E-mail") },
            singleLine = true,
            enabled = !loading,
          )
          Spacer(modifier = Modifier.height(12.dp))
          OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Senha") },
            singleLine = true,
            enabled = !loading,
            visualTransformation = PasswordVisualTransformation(),
          )
          Spacer(modifier = Modifier.height(16.dp))
          Button(
            onClick = { onEmailSubmit(email, password, createAccount) },
            modifier = Modifier.fillMaxWidth(),
            enabled = !loading,
          ) {
            Text(if (createAccount) "Criar e entrar" else "Entrar")
          }

          if (error != null) {
            Spacer(modifier = Modifier.height(16.dp))
            Text(
              text = error,
              color = MaterialTheme.colorScheme.error,
              style = MaterialTheme.typography.bodyMedium,
            )
          }
          TextButton(onClick = onPrivacy, enabled = !loading) {
            Text("Preferências de privacidade")
          }
        }
      }
    }

    if (loading) {
      Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.BottomCenter,
      ) {
        Card(
          modifier = Modifier.padding(bottom = 24.dp),
          colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A).copy(alpha = 0.88f)),
          shape = RoundedCornerShape(999.dp),
        ) {
          Row(
            modifier = Modifier.padding(horizontal = 18.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
          ) {
            CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp)
            Text("Validando acesso seguro")
          }
        }
      }
    }
  }
}

@Composable
private fun ConsumerShell(
  modifier: Modifier = Modifier,
  session: ValleySession,
  onPrivacy: () -> Unit,
  onLogout: () -> Unit,
) {
  val context = LocalContext.current
  var webView by remember { mutableStateOf<WebView?>(null) }
  var canGoBack by remember { mutableStateOf(false) }
  var needsReload by remember { mutableStateOf(true) }

  BackHandler(enabled = canGoBack) {
    webView?.goBack()
  }

  LaunchedEffect(session) {
    needsReload = true
    webView?.loadUrl(VALLEY_WEB_URL)
  }

  Scaffold(
    modifier = modifier.fillMaxSize(),
    topBar = {
      @OptIn(ExperimentalMaterial3Api::class)
      TopAppBar(
        title = {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Image(
              painter = painterResource(id = R.drawable.valley_logo),
              contentDescription = "Valley",
              modifier = Modifier.size(36.dp),
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column {
              Text("Valley", fontWeight = FontWeight.Bold)
              Text(
                text = session.email,
                style = MaterialTheme.typography.labelSmall,
                color = Color(0xFFCBD5E1),
              )
            }
          }
        },
        actions = {
          TextButton(onClick = onPrivacy) { Text("Privacidade") }
          OutlinedButton(
            onClick = {
              webView?.evaluateJavascript("sessionStorage.clear(); localStorage.clear();", null)
              WebStorage.getInstance().deleteAllData()
              webView?.clearCache(true)
              onLogout()
            },
          ) {
            Text("Sair")
          }
        },
        colors =
          TopAppBarDefaults.topAppBarColors(
            containerColor = Color(0xFF0A0F1E),
            titleContentColor = Color.White,
            actionIconContentColor = Color.White,
          ),
      )
    },
  ) { padding ->
    Box(
      modifier =
        Modifier
          .padding(padding)
          .fillMaxSize()
          .background(Color(0xFF0A0F1E)),
    ) {
      AndroidView(
        factory = { appContext ->
          WebView(appContext).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.mediaPlaybackRequiresUserGesture = false
            settings.allowContentAccess = false
            settings.setSupportMultipleWindows(false)
            webChromeClient = WebChromeClient()
            webViewClient =
              object : WebViewClient() {
                override fun onPageFinished(view: WebView, url: String?) {
                  canGoBack = view.canGoBack()
                  view.evaluateJavascript(sessionInjectionScript(session), null)
                  if (needsReload) {
                    needsReload = false
                    view.postDelayed({ view.loadUrl(VALLEY_WEB_URL) }, 120)
                  }
                }
              }
            loadUrl(VALLEY_WEB_URL)
          }.also { webView = it }
        },
        modifier = Modifier.fillMaxSize(),
        update = { view ->
          canGoBack = view.canGoBack()
          if (needsReload) {
            view.loadUrl(VALLEY_WEB_URL)
          } else {
            view.evaluateJavascript(sessionInjectionScript(session), null)
          }
        },
      )
    }
  }
}

private suspend fun authenticateWithFirebaseGoogle(context: Context): FirebaseGoogleIdentity {
  val credentialManager = CredentialManager.create(context)

  suspend fun requestGoogleCredential(filterAuthorizedAccounts: Boolean) =
    credentialManager.getCredential(
      context = context,
      request =
        GetCredentialRequest.Builder()
          .addCredentialOption(
            GetGoogleIdOption.Builder()
              .setServerClientId(context.getString(R.string.default_web_client_id))
              .setFilterByAuthorizedAccounts(filterAuthorizedAccounts)
              .setAutoSelectEnabled(filterAuthorizedAccounts)
              .build(),
          )
          .build(),
    )

  val result =
    try {
      requestGoogleCredential(filterAuthorizedAccounts = true)
    } catch (_: NoCredentialException) {
      try {
        requestGoogleCredential(filterAuthorizedAccounts = false)
      } catch (_: NoCredentialException) {
        error("Nenhuma conta Google esta disponivel neste aparelho. Adicione uma conta e tente novamente.")
      }
    } catch (_: GetCredentialCancellationException) {
      error("A selecao da conta Google foi cancelada.")
    }
  val credential = result.credential
  require(
    credential is CustomCredential &&
      credential.type == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL,
  ) { "A credencial retornada nao e uma conta Google valida." }

  val googleCredential = GoogleIdTokenCredential.createFrom(credential.data)
  val firebaseCredential = GoogleAuthProvider.getCredential(googleCredential.idToken, null)
  val firebaseUser =
    FirebaseAuth.getInstance().signInWithCredential(firebaseCredential).await().user
      ?: error("O Firebase nao retornou o usuario autenticado.")
  val email = firebaseUser.email?.trim()?.lowercase(Locale.US)
  require(!email.isNullOrBlank()) { "A conta Google nao disponibilizou um e-mail." }
  return FirebaseGoogleIdentity(email = email, uid = firebaseUser.uid)
}

private suspend fun authenticateWithValley(
  context: Context,
  email: String,
  password: String,
  source: String,
  createAccount: Boolean,
): ValleySession {
  val normalizedEmail = email.trim().lowercase(Locale.US)
  require(normalizedEmail.contains("@")) { "Informe um e-mail valido." }
  require(password.length >= 6) { "A senha precisa ter ao menos 6 caracteres." }

  if (createAccount) {
    val now = nowIso8601()
    val registration =
      JSONObject()
        .put("full_name", valleyDisplayName(normalizedEmail))
        .put("email", normalizedEmail)
        .put("password_hash", password)
        .put("document_cpf", valleyCpfForEmail(normalizedEmail))
        .put("terms_accepted_at", now)
        .put("lgpd_consent_at", now)
    val registrationResult = runCatching { postJson(context, "$API_HUB_URL/registrations", registration) }
    registrationResult.exceptionOrNull()?.let { error ->
      if (error !is ValleyHttpException || error.statusCode != 409) {
        throw error
      }
    }
  }

  val loginBody = JSONObject().put("email", normalizedEmail).put("password", password)
  val loginResult =
    postJson(context, "$API_HUB_URL/auth/login", loginBody)
  val token = loginResult.optString("access_token")
  val refreshToken = loginResult.optString("refresh_token")
  val sessionId = loginResult.optString("session_id")
  val userId = loginResult.optString("user_id")
  val expiresAt = loginResult.optString("expires_at")
  val refreshExpiresAt = loginResult.optString("refresh_expires_at")
  if (
    token.isBlank() || refreshToken.isBlank() || sessionId.isBlank() || userId.isBlank() ||
      expiresAt.isBlank() || refreshExpiresAt.isBlank()
  ) {
    error("O backend nao retornou uma sessao Valley valida.")
  }
  return ValleySession(
    token,
    refreshToken,
    sessionId,
    userId,
    normalizedEmail,
    source,
    expiresAt,
    refreshExpiresAt,
  )
}

private suspend fun refreshValleySession(context: Context, session: ValleySession): ValleySession {
  val response =
    postJson(
      context,
      "$API_HUB_URL/auth/refresh",
      JSONObject()
        .put("refresh_token", session.refreshToken)
        .put("device_fingerprint", valleyDeviceFingerprint(context)),
    )
  val token = response.optString("access_token")
  val refreshToken = response.optString("refresh_token")
  val sessionId = response.optString("session_id")
  val expiresAt = response.optString("expires_at")
  val refreshExpiresAt = response.optString("refresh_expires_at")
  require(token.isNotBlank() && refreshToken.isNotBlank() && sessionId.isNotBlank()) {
    "O backend nao renovou a sessao Valley."
  }
  return session.copy(
    token = token,
    refreshToken = refreshToken,
    sessionId = sessionId,
    expiresAt = expiresAt,
    refreshExpiresAt = refreshExpiresAt,
  )
}

private data class ValleyHttpException(val statusCode: Int, override val message: String) : IllegalStateException(message)

private suspend fun postJson(context: Context, url: String, body: JSONObject): JSONObject {
  val integrityToken = PlayIntegrityAttestor(context).tokenFor(body.toString())
  val correlationId = UUID.randomUUID().toString()
  val route = URL(url).path.ifBlank { "/" }
  val startedAt = android.os.SystemClock.elapsedRealtime()
  return withContext(Dispatchers.IO) {
    val connection = (URL(url).openConnection() as HttpURLConnection).apply {
      requestMethod = "POST"
      connectTimeout = 15_000
      readTimeout = 20_000
      doOutput = true
      setRequestProperty("Content-Type", "application/json")
      setRequestProperty("Accept", "application/json")
      setRequestProperty("X-Valley-Api-Version", "1")
      setRequestProperty("X-Device-Fingerprint", valleyDeviceFingerprint(context))
      setRequestProperty("X-Correlation-Id", correlationId)
      integrityToken?.let { setRequestProperty("X-Play-Integrity-Token", it) }
    }
    try {
      connection.outputStream.use { stream ->
        stream.write(body.toString().toByteArray(Charsets.UTF_8))
      }
      val responseCode = connection.responseCode
      val responseText =
        runCatching {
          (if (responseCode in 200..299) connection.inputStream else connection.errorStream)
            ?.bufferedReader()
            ?.use { it.readText() }
            .orEmpty()
        }.getOrDefault("")
      ValleyObservability.recordHttpResult(
        correlationId = correlationId,
        route = route,
        statusCode = responseCode,
        durationMs = android.os.SystemClock.elapsedRealtime() - startedAt,
      )
      if (responseCode !in 200..299) {
        val detail =
          runCatching { JSONObject(responseText).optString("detail") }
            .getOrDefault("")
            .ifBlank { "Falha HTTP $responseCode" }
        throw ValleyHttpException(responseCode, detail)
      }
      if (responseText.isBlank()) return@withContext JSONObject()
      return@withContext JSONObject(responseText)
    } catch (throwable: Throwable) {
      if (throwable !is ValleyHttpException) {
        ValleyObservability.recordHttpResult(
          correlationId = correlationId,
          route = route,
          statusCode = 0,
          durationMs = android.os.SystemClock.elapsedRealtime() - startedAt,
          failure = throwable,
        )
      }
      throw throwable
    } finally {
      connection.disconnect()
    }
  }
}

private fun valleyDeviceFingerprint(context: Context): String {
  val androidId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID).orEmpty()
  return "android-" + valleyHash("${context.packageName}:$androidId")
}

private fun nowIso8601(): String {
  val formatter = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
  formatter.timeZone = java.util.TimeZone.getTimeZone("UTC")
  return formatter.format(java.util.Date())
}

private fun valleyHash(value: String): String {
  val digest = MessageDigest.getInstance("SHA-256").digest(value.toByteArray())
  return digest.joinToString(separator = "") { byte -> "%02x".format(byte) }
}
