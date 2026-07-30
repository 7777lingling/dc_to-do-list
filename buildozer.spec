[app]
title = Schedule
package.name = schedule
package.domain = org.example
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = .git,.vs,__pycache__,build,dist,tests,output,.pytest_cache
version = 0.1.0
requirements = python3,kivy,requests,plyer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,POST_NOTIFICATIONS
android.api = 35
android.minapi = 23
android.archs = arm64-v8a,armeabi-v7a
android.private_storage = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
