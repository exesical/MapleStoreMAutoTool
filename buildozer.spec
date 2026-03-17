[app]

# (str) Title of your application
title = 冒险岛M自动助手

# (str) Package name
package.name = maplestoremauto

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,json

# (list) List of inclusions using pattern matching
source.include_patterns = Data/*,*.json,*.png

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,opencv,numpy,pillow,plyer,android

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (list) Android application meta-data to set (key=value format)
android.meta_data = 

# (list) Android library project to add (will be added in the libs dir)
android.library_references = 

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for tags specified in
# android.logcat_filters, if False it display all tags, default True
android.logcat.only_specified_tags = False

# (str) Path to a custom whitelist file
android.whitelist = 

# (list) Pattern to whitelist for the whole project
#android.whitelist_src = 

# (str) Path to a custom blacklist file
android.blacklist = 

# (list) List of Java .jar files to add to the libs so they can be imported.
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src = 

# (list) Android AAR archives to add
#android.add_aars = 

# (list) Put these files or directories in the apk assets directory.
# Either form may be used, and assets need not be in 'source.include_exts'.
android.add_assets = 

# (list) Put these files or directories in the apk res directory.
# The option may be used in three ways, the value may contain one or zero ':'
# Some examples:
# 1) android.add_resources = file1.png:drawable/icon.png
# 2) android.add_resources = path/to/*.png:drawable
# 3) android.add_resources = path/to/picture.png
#android.add_resources = 

# (list) Gradle dependencies to add
#android.gradle_dependencies = 

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
android.enable_androidx = True

# (list) add java compile options
# this can for example be necessary when importing certain java libraries using the 'android.gradle_dependencies' option
# see https://developer.android.com/studio/write/java8-support for further information
# android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (list) Gradle repositories to add {can be necessary for some android.gradle_dependencies}
# please enclose in double quotes 
# e.g. android.gradle_repositories = "google()", "jcenter()", "maven { url 'https://kotlin.bintray.com/kotlinx' }"
#android.gradle_repositories = 

# (list) packaging options to add 
# see https://google.github.io/android-gradle-dsl/current/com.android.build.gradle.internal.dsl.PackagingOptions.html
# can be necessary to solve conflicts in gradle_dependencies
# please enclose in double quotes 
# e.g. android.add_packaging_options = "pickFirst '**/libc++_shared.so'", "exclude 'META-INF/DEPENDENCIES'"
#android.add_packaging_options = 

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filter in your app
#android.manifest.intent_filters = 

# (str) launchMode to set for the main activity
#android.manifest.launch_mode = 

# (list) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
android.wakelock = True

# (list) Android application permissions
# Access to the following permissions needs to be requested at runtime too
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA,SYSTEM_ALERT_WINDOW,ACCESSIBILITY_SERVICE,WAKE_LOCK

# (list) Android bootup permissions
#android.bootup_permissions = 

# (int) Target Android API, should be as high as possible.
#android.api = 33

# (int) Minimum API your APK will support.
#android.minapi = 21

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Python Service
# use that parameter together with android.add_src
#android.service = 

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
#android.whitelist_src = 
#android.whitelist = 

# (str) Path to a custom whitelist file
#android.whitelist_src = 

# (str) Path to a custom blacklist file
#android.blacklist_src = 

# (list) List of Java .jar files to add to the libs so they can be imported.
#android.add_jars = 

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src = 

# (list) Android AAR archives to add (currently works only with sdl2_gradle
# bootstrap)
#android.add_aars = 

# (list) Gradle dependencies to add (currently works only with sdl2_gradle
# bootstrap)
#android.gradle_dependencies = 

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
# Depending on your requirements, you may set this to either True or False.
#android.enable_androidx = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Python Service
# use that parameter together with android.add_src
#android.service = 

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin