plugins {
    alias(libs.plugins.android.application)
}

val valleyUrlProvider = providers.gradleProperty("VALLEY_UNIVERSAL_URL")
    .orElse(providers.environmentVariable("VALLEY_UNIVERSAL_URL"))
    .orElse("https://84e9680fcfa2a84551.v2.appdeploy.ai/")

val escapedValleyUrl = valleyUrlProvider.get()
    .replace("\\", "\\\\")
    .replace("\"", "\\\"")

val generatedBrandRes = layout.buildDirectory.dir("generated/res/valleyBrand")
val generateValleyBrandIcon by tasks.registering(Copy::class) {
    from(rootProject.file("../../assets/brand/valley-logo-official.png"))
    into(generatedBrandRes.map { it.dir("mipmap-xxxhdpi") })
    rename { "ic_launcher.png" }
}

android {
    namespace = "br.com.allinone.valley.universal"
    compileSdk = 36
    buildToolsVersion = "36.1.0"

    defaultConfig {
        applicationId = "br.com.allinone.valley"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0.0"
        buildConfigField(
            "String",
            "VALLEY_URL",
            "\"$escapedValleyUrl\"",
        )
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    sourceSets.getByName("main").res.srcDir(generatedBrandRes)

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

tasks.named("preBuild").configure {
    dependsOn(generateValleyBrandIcon)
}

dependencies {
    implementation("androidx.activity:activity:1.13.0")
    testImplementation(libs.junit)
}
