package com.example.valley

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.ui.Alignment
import androidx.compose.ui.unit.dp
import androidx.compose.ui.Modifier
import com.example.valley.theme.ValleyTheme
import com.example.valley.ui.main.MainScreen
import com.example.valley.observability.ValleyObservability
import com.example.valley.security.RuntimeIntegrityGuard

class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    ValleyObservability.initialize(applicationContext)
    val integrityAssessment = RuntimeIntegrityGuard.assess(applicationContext)

    enableEdgeToEdge()
    setContent {
      ValleyTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
          if (integrityAssessment.trusted) {
            MainScreen()
          } else {
            Box(
              modifier = Modifier.fillMaxSize().padding(32.dp),
              contentAlignment = Alignment.Center,
            ) {
              Text("Este ambiente não atende aos requisitos de segurança do Valley. Reinstale o app pela Google Play e revise a integridade do dispositivo.")
            }
          }
        }
      }
    }
  }
}
