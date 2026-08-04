// Top-level build file where you can add configuration options common to all sub-projects/modules.
buildscript {
  val hardenedBuildDependencies = listOf(
    "io.netty:netty-buffer:4.1.136.Final",
    "io.netty:netty-codec:4.1.136.Final",
    "io.netty:netty-codec-http:4.1.136.Final",
    "io.netty:netty-codec-http2:4.1.136.Final",
    "io.netty:netty-common:4.1.136.Final",
    "io.netty:netty-handler:4.1.136.Final",
    "io.netty:netty-handler-proxy:4.1.136.Final",
    "io.netty:netty-resolver:4.1.136.Final",
    "io.netty:netty-transport:4.1.136.Final",
    "org.bouncycastle:bcpkix-jdk18on:1.84",
    "org.bouncycastle:bcprov-jdk18on:1.84",
    "org.bouncycastle:bcutil-jdk18on:1.84",
    "org.bitbucket.b_c:jose4j:0.9.6",
    "org.jdom:jdom2:2.0.6.1",
    "org.apache.commons:commons-lang3:3.18.0",
    "org.apache.httpcomponents:httpclient:4.5.14",
    "com.google.protobuf:protobuf-java:4.35.1",
    "com.google.protobuf:protobuf-java-util:4.35.1",
    "com.google.protobuf:protobuf-kotlin:4.35.1",
    "com.google.guava:guava:33.3.1-jre",
  )
  configurations.configureEach {
    resolutionStrategy.force(hardenedBuildDependencies)
  }
}

private val hardenedProjectDependencies = listOf(
  "io.netty:netty-buffer:4.1.136.Final",
  "io.netty:netty-codec:4.1.136.Final",
  "io.netty:netty-codec-http:4.1.136.Final",
  "io.netty:netty-codec-http2:4.1.136.Final",
  "io.netty:netty-common:4.1.136.Final",
  "io.netty:netty-handler:4.1.136.Final",
  "io.netty:netty-handler-proxy:4.1.136.Final",
  "io.netty:netty-resolver:4.1.136.Final",
  "io.netty:netty-transport:4.1.136.Final",
  "org.bouncycastle:bcpkix-jdk18on:1.84",
  "org.bouncycastle:bcprov-jdk18on:1.84",
  "org.bouncycastle:bcutil-jdk18on:1.84",
  "org.bitbucket.b_c:jose4j:0.9.6",
  "org.jdom:jdom2:2.0.6.1",
  "org.apache.commons:commons-lang3:3.18.0",
  "org.apache.httpcomponents:httpclient:4.5.14",
  "com.google.protobuf:protobuf-java:4.35.1",
  "com.google.protobuf:protobuf-java-util:4.35.1",
  "com.google.protobuf:protobuf-kotlin:4.35.1",
  "com.google.guava:guava:33.3.1-jre",
)

subprojects {
  configurations.configureEach {
    resolutionStrategy.force(hardenedProjectDependencies)
  }
}

plugins {
  alias(libs.plugins.android.application) apply false
  alias(libs.plugins.compose.compiler) apply false
  alias(libs.plugins.kotlin.serialization) apply false
  alias(libs.plugins.google.services) apply false
  alias(libs.plugins.firebase.crashlytics) apply false
}
