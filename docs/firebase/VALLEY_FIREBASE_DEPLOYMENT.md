# Valley Firebase Deployment

## Classification

- Project: All in One + Valley
- Folder: Pendencias / Tecnico
- Audience: Equipe Tecnica
- Firebase project: Valley
- Firebase project ID: `valley-3b421`
- Google Cloud project number: `540882936740`
- GitHub service-account secret: `FIREBASE_SECRETS_VALLEY`

## Mandatory policy

1. Never commit Firebase service-account JSON files.
2. Never print `FIREBASE_SECRETS_VALLEY` in logs.
3. Production Hosting deploys only from `main` after protected merge.
4. Pull requests validate and build, but never publish to the live channel.
5. Android distribution requires `FIREBASE_APP_ID_VALLEY_ANDROID` with prefix `1:540882936740:android:`.
6. Configure either `FIREBASE_VALLEY_TESTERS` or `FIREBASE_VALLEY_TESTER_GROUPS` before App Distribution.
7. The service account must follow least privilege. Do not grant Owner or Editor merely to bypass a permission failure.
8. Prefer OIDC or Workload Identity Federation in a later hardening phase to remove persistent JSON keys.
9. Changes to these workflows must use a branch and pull request. Do not push directly to `main`.
10. Integration is allowed only with mandatory gates green on the current head SHA and by Squash and Merge with `expected_head_sha`.

## Implemented files

- `firebase.json`
- `.firebaserc`
- `.github/workflows/firebase-valley-hosting.yml`
- `.github/workflows/firebase-valley-app-distribution.yml`

## Required GitHub configuration

### Secret already expected

- `FIREBASE_SECRETS_VALLEY`

### Secret still required for Android distribution

- `FIREBASE_APP_ID_VALLEY_ANDROID`

### Optional repository variables

- `FIREBASE_VALLEY_TESTERS`
- `FIREBASE_VALLEY_TESTER_GROUPS`

### Environments

- `firebase-valley-production`
- `firebase-valley-testing`

## Operational boundary

Firebase Hosting publishes the web build generated from `apps/valley`. GitHub Actions compiles the Flutter project at `apps/valley-flutter` and uploads the APK to Firebase App Distribution. Firebase does not compile the APK directly from the repository.
