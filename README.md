# Tears of a Father — Android app

A Trusted Web Activity: the app opens https://tearsofafather.com full-screen. Site changes reach the app without an app update.

* Package: `com.tearsofafather.app`
* GitHub Actions builds an **unsigned** release bundle on every push to this branch. It is signed afterwards with the upload key, which is never stored in this repository.
* The site proves it owns the app through `/.well-known/assetlinks.json` (upload key fingerprint, plus Google Play's app-signing fingerprint once Play issues it).
* To ship an update to the app shell (icon, name, colors): change it here, push, sign the new bundle, upload it to Play. Content updates need none of that.
