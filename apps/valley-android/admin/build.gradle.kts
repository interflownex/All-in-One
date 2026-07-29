plugins {
    alias(libs.plugins.android.application)
}

val adminUrlProvider = providers.gradleProperty("A1_ADMIN_URL")
    .orElse(providers.environmentVariable("A1_ADMIN_URL"))
    .orElse("https://9135635066da434181.v2.appdeploy.ai/")

val escapedAdminUrl = adminUrlProvider.get()
    .replace("\\", "\\\\")
    .replace("\"", "\\\"")

android {
    namespace = "br.com.allinone.admin"
    compileSdk = 36
    buildToolsVersion = "36.1.0"

    defaultConfig {
        applicationId = "br.com.allinone.admin"
        minSdk = 24
        targetSdk = 36
        versionCode = 2
        versionName = "1.1.0"
        buildConfigField(
            "String",
            "ADMIN_URL",
            "\"$escapedAdminUrl\"",
        )
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
            isDebuggable = true
        }
        release {
            isDebuggable = false
            isMinifyEnabled = true
            isShrinkResources = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    implementation("androidx.activity:activity:1.13.0")
    testImplementation(libs.junit)
}
