# Regras de endurecimento do Valley Android.
# Mantém apenas os metadados necessários para serialização e diagnóstico controlado.
-keepattributes Signature,InnerClasses,EnclosingMethod
-keepattributes RuntimeVisibleAnnotations,RuntimeInvisibleAnnotations,AnnotationDefault

# Never emit source paths or line tables in the distributed release artifact.
-renamesourcefileattribute SourceFile
-keepattributes !SourceFile,!LineNumberTable

# Enable stronger shrinking/optimization while preserving runtime compatibility.
-allowaccessmodification
-repackageclasses
-adaptclassstrings

# Remove chamadas de log da bytecode de produção.
-assumenosideeffects class android.util.Log {
    public static boolean isLoggable(...);
    public static int v(...);
    public static int i(...);
    public static int d(...);
    public static int w(...);
    public static int e(...);
    public static int println(...);
}

# Kotlin serialization depende dos serializers gerados em tempo de compilação.
-if @kotlinx.serialization.Serializable class **
-keepclassmembers class <1> {
    static <1>$Companion Companion;
}
-if @kotlinx.serialization.Serializable class ** {
    static **$Companion Companion;
}
-keepclasseswithmembers class **$Companion {
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class **$$serializer { *; }
-keepclassmembers class ** {
    *** Companion;
}

# Preserva o contrato de transferência da API, quando presente.
-keep class com.example.valley.api.dto.** { *; }
-keepclassmembers class ** {
    @kotlinx.serialization.SerialName <fields>;
}
