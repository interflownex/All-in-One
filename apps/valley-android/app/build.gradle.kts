import java.util.Properties

plugins {
  alias(libs.plugins.android.application)
  alias(libs.plugins.compose.compiler)
  alias(libs.plugins.kotlin.serialization)
  alias(libs.plugins.google.services)
  alias(libs.plugins.firebase.crashlytics)
}

val releaseSigningProperties = Properties()
val playIntegrityCloudProjectNumber =
  providers.environmentVariable("VALLEY_PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER").orElse("0").get()
val releaseCertificateSha256 =
  providers.environmentVariable("VALLEY_PLAY_APP_SIGNING_CERT_SHA256").orElse("").get().replace(":", "").lowercase()
require(playIntegrityCloudProjectNumber.matches(Regex("[0-9]+"))) {
  "VALLEY_PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER deve conter apenas digitos."
}
val releaseSigningPropertiesFile =
  file(
    System.getenv("VALLEY_RELEASE_SIGNING_PROPERTIES")
      ?: "${System.getProperty("user.home")}/.config/all-in-one/valley-release.properties",
  )
if (releaseSigningPropertiesFile.isFile) {
  releaseSigningPropertiesFile.inputStream().use(releaseSigningProperties::load)
}

val releaseRequested =
  gradle.startParameter.taskNames.any { taskName ->
    taskName.contains("release", ignoreCase = true) &&
      (taskName.contains("assemble", ignoreCase = true) ||
        taskName.contains("bundle", ignoreCase = true) ||
        taskName.contains("package", ignoreCase = true))
  }
if (releaseRequested && !releaseSigningPropertiesFile.isFile) {
  throw GradleException(
    "Build release bloqueado: configure VALLEY_RELEASE_SIGNING_PROPERTIES " +
      "ou ~/.config/all-in-one/valley-release.properties. Assinatura debug nunca e aceita.",
  )
}
if (releaseRequested && playIntegrityCloudProjectNumber == "0") {
  throw GradleException(
    "Build release bloqueado: configure VALLEY_PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER para a Play Integrity API.",
  )
}
if (releaseRequested && !releaseCertificateSha256.matches(Regex("(?i)[0-9a-f]{64}"))) {
  throw GradleException(
    "Build release bloqueado: configure VALLEY_PLAY_APP_SIGNING_CERT_SHA256 com o SHA-256 do certificado Play App Signing.",
  )
}

android {
    namespace = "com.example.valley"
    compileSdk = 36
    buildToolsVersion = "36.1.0"
    defaultConfig {
        applicationId = "com.example.valley"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
        buildConfigField("long", "PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER", "${playIntegrityCloudProjectNumber}L")
        buildConfigField("String", "PLAY_APP_SIGNING_CERT_SHA256", "\"${releaseCertificateSha256.lowercase()}\"")
    }

    signingConfigs {
      if (releaseSigningPropertiesFile.isFile) {
        create("release") {
          storeFile = file(releaseSigningProperties.getProperty("storeFile"))
          storePassword = releaseSigningProperties.getProperty("storePassword")
          keyAlias = releaseSigningProperties.getProperty("keyAlias")
          keyPassword = releaseSigningProperties.getProperty("keyPassword")
        }
      }
    }

    buildTypes {
        debug {
            versionNameSuffix = "-debug"
        }
        create("staging") {
            initWith(getByName("debug"))
            versionNameSuffix = "-staging"
            matchingFallbacks += listOf("debug")
        }
        release {
            isDebuggable = false
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.findByName("release")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    buildFeatures {
      compose = true
      aidl = false
      buildConfig = true
      shaders = false
    }

    packaging {
      resources {
        excludes += setOf(
          "/META-INF/{AL2.0,LGPL2.1}",
          "**/README*",
          "**/CHANGELOG*",
          "**/docs/**",
          "**/runbooks/**",
          "**/roadmap/**",
          "**/*.sql",
        )
      }
    }
}

androidComponents {
  onVariants(selector().withBuildType("debug")) { variant ->
    variant.packaging.jniLibs.keepDebugSymbols.add("**/*.so")
  }
  onVariants(selector().withBuildType("staging")) { variant ->
    variant.packaging.jniLibs.keepDebugSymbols.add("**/*.so")
  }
}

kotlin {
    jvmToolchain(17)
}

dependencies {
  val composeBom = platform(libs.androidx.compose.bom)
  implementation(composeBom)
  androidTestImplementation(composeBom)

  // Core Android dependencies
  implementation(libs.androidx.core.ktx)
  implementation(libs.androidx.lifecycle.runtime.ktx)
  implementation(libs.androidx.activity.compose)
  implementation(libs.androidx.credentials)
  implementation(libs.androidx.credentials.play.services.auth)

  // Arch Components
  implementation(libs.androidx.lifecycle.runtime.compose)
  implementation(libs.androidx.lifecycle.viewmodel.compose)

  // Compose
  implementation(libs.androidx.compose.ui)
  implementation(libs.androidx.compose.ui.tooling.preview)
  implementation(libs.androidx.compose.material3)
  implementation(platform(libs.firebase.bom))
  implementation(libs.firebase.auth)
  implementation(libs.firebase.analytics)
  implementation(libs.firebase.crashlytics)
  implementation(libs.googleid)
  implementation(libs.kotlinx.coroutines.play.services)
  implementation(libs.play.integrity)
  // Tooling
  debugImplementation(libs.androidx.compose.ui.tooling)
  // Instrumented tests
  androidTestImplementation(libs.androidx.compose.ui.test.junit4)
  debugImplementation(libs.androidx.compose.ui.test.manifest)

  // Local tests: jUnit, coroutines, Android runner
  testImplementation(libs.junit)
  testImplementation(libs.kotlinx.coroutines.test)

  // Instrumented tests: jUnit rules and runners
  androidTestImplementation(libs.androidx.test.core)
  androidTestImplementation(libs.androidx.test.ext.junit)
  androidTestImplementation(libs.androidx.test.runner)
  androidTestImplementation(libs.androidx.test.espresso.core)

  // Navigation
  implementation(libs.androidx.navigation3.ui)
  implementation(libs.androidx.navigation3.runtime)
  implementation(libs.androidx.lifecycle.viewmodel.navigation3)
}
