[app]

title = Efootball
package.name = efootball
package.domain = org.shipit

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,txt,json

source.exclude_exts = spec,pyc,pyo
source.exclude_dirs = tests,bin,venv,.venv,.git,.github,dist,build,__pycache__

version = 0.1.0

requirements = python3,kivy==2.3.0

orientation = landscape
fullscreen = 1

android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 0
