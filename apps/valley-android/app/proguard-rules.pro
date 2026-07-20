# Regras de endurecimento do Valley Android.
# Mantém apenas os metadados necessários para serialização e diagnóstico controlado.
-keepattributes Signature,InnerClasses,EnclosingMethod
-keepattributes RuntimeVisibleAnnotations,RuntimeInvisibleAnnotations,AnnotationDefault

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

# Remove chamadas de log verboso em produção sem afetar erros críticos.
-assumenosideeffects class android.util.Log {
    public static int v(...);
    public static int d(...);
}
