# Valley release: preserve only metadata required by Firebase/Credential Manager.
-keepattributes Signature,InnerClasses,EnclosingMethod
-keepattributes RuntimeVisibleAnnotations,RuntimeInvisibleAnnotations,AnnotationDefault

# Never emit source paths or line tables in the distributed release artifact.
-renamesourcefileattribute SourceFile
-keepattributes !SourceFile,!LineNumberTable
