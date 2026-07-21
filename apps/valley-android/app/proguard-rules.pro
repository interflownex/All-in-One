# Valley release: preserve only metadata required by Firebase/Credential Manager.
-keepattributes Signature,InnerClasses,EnclosingMethod
-keepattributes RuntimeVisibleAnnotations,RuntimeInvisibleAnnotations,AnnotationDefault

# Never emit source paths or line tables in the distributed release artifact.
-renamesourcefileattribute SourceFile
-keepattributes !SourceFile,!LineNumberTable

# Enable stronger shrinking/optimization while preserving runtime compatibility.
-allowaccessmodification
-repackageclasses
-adaptclassstrings

# Strip logging calls from release bytecode.
-assumenosideeffects class android.util.Log {
	public static boolean isLoggable(...);
	public static int v(...);
	public static int i(...);
	public static int d(...);
	public static int w(...);
	public static int e(...);
	public static int println(...);
}

# Keep only serialization/data-transfer contract required at runtime.
-keep class kotlinx.serialization.** { *; }
-keepclassmembers class ** {
	@kotlinx.serialization.SerialName <fields>;
}
-keep @kotlinx.serialization.Serializable class * { *; }

# Keep API response DTO package if present.
-keep class com.example.valley.api.dto.** { *; }
