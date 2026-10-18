[app]
title = Range Pinger
package.name = rangepinger
package.domain = org.pinger
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy

orientation = portrait
fullscreen = 0

# Android permissions
android.permissions = INTERNET

# Android SDK / NDK configuration
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1