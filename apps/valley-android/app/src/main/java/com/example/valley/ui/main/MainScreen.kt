package com.example.valley.ui.main

import android.accounts.AccountManager
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.ActivityResult
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
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
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
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
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

private const val VALLEY_WEB_URL = "https://valley-all-in-one.web.app"
private const val API_HUB_URL = "https://all-in-one-api-hub.web.app"

@Composable
fun MainScreen(modifier: Modifier = Modifier) {
  val context = LocalContext.current
  val scope = rememberCoroutineScope()
  var session by remember { mutableStateOf(loadValleySession(context)) }
  var authInProgress by rememberSaveable { mutableStateOf(false) }
  var authError by rememberSaveable { mutableStateOf<String?>(null) }

  val activeSession = session

  if (activeSession == null) {
    LoginScreen(
      modifier = modifier,
      loading = authInProgress,
      error = authError,
      onGooglePick = { selectedEmail ->
        scope.launch {
          authInProgress = true
          authError = null
          runCatching {
            authenticateWithValley(
              context = context,
              email = selectedEmail,
              password = valleyGooglePasswordFor(selectedEmail),
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
      onLogout = {
        clearValleySession(context)
        session = null
      },
    )
  }
}

@Composable
private fun LoginScreen(
  modifier: Modifier = Modifier,
  loading: Boolean,
  error: String?,
  onGooglePick: (String) -> Unit,
  onEmailSubmit: (String, String, Boolean) -> Unit,
) {
  val context = LocalContext.current
  var email by rememberSaveable { mutableStateOf("") }
  var password by rememberSaveable { mutableStateOf("") }
  var createAccount by rememberSaveable { mutableStateOf(false) }

  val googleLauncher = rememberLauncherForActivityResult(StartActivityForResult()) { result: ActivityResult ->
    if (result.resultCode != Activity.RESULT_OK) {
      return@rememberLauncherForActivityResult
    }
    val pickedEmail = result.data?.getStringExtra(AccountManager.KEY_ACCOUNT_NAME)?.trim().orEmpty()
    if (pickedEmail.isBlank()) {
      authFallback(email, password, createAccount, onEmailSubmit)
    } else {
      onGooglePick(pickedEmail)
    }
  }

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
            onClick = { googleLauncher.launch(createGoogleAccountChooserIntent(context)) },
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
          OutlinedButton(onClick = onLogout) {
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

private fun authFallback(
  email: String,
  password: String,
  createAccount: Boolean,
  onEmailSubmit: (String, String, Boolean) -> Unit,
) {
  if (email.isNotBlank()) {
    onEmailSubmit(email, password, createAccount)
  }
}

private fun createGoogleAccountChooserIntent(context: Context): Intent {
  return AccountManager.newChooseAccountIntent(
    null,
    null,
    arrayOf("com.google"),
    false,
    null,
    null,
    null,
    null,
  )
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
    runCatching { postJson("$API_HUB_URL/registrations", registration) }
      .onFailure { error ->
        if (error !is ValleyHttpException || error.statusCode != 409) {
          throw error
        }
      }
  }

  val loginBody = JSONObject().put("email", normalizedEmail).put("password", password)
  val loginResult = postJson("$API_HUB_URL/auth/login", loginBody)
  val token = loginResult.optString("access_token")
  val userId = loginResult.optString("user_id")
  require(token.isNotBlank() && userId.isNotBlank()) { "Falha ao obter sessão autenticada." }
  return ValleySession(token = token, userId = userId, email = normalizedEmail, source = source)
}

private data class ValleyHttpException(val statusCode: Int, override val message: String) : IllegalStateException(message)

private suspend fun postJson(url: String, body: JSONObject): JSONObject = withContext(Dispatchers.IO) {
  val connection = (URL(url).openConnection() as HttpURLConnection).apply {
    requestMethod = "POST"
    connectTimeout = 15_000
    readTimeout = 20_000
    doOutput = true
    setRequestProperty("Content-Type", "application/json")
    setRequestProperty("Accept", "application/json")
  }

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

  connection.disconnect()

  if (responseCode !in 200..299) {
    val detail =
      runCatching { JSONObject(responseText).optString("detail") }
        .getOrDefault("")
        .ifBlank { "Falha HTTP $responseCode" }
    throw ValleyHttpException(responseCode, detail)
  }

  if (responseText.isBlank()) return@withContext JSONObject()
  return@withContext JSONObject(responseText)
}

private fun nowIso8601(): String {
  val formatter = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
  formatter.timeZone = java.util.TimeZone.getTimeZone("UTC")
  return formatter.format(java.util.Date())
}
