import 'dart:async';

import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:webview_flutter/webview_flutter.dart';

import 'api_bridge.dart';

const _valleyPurple = Color(0xFF5D2CE6);
const _valleyBackground = Color(0xFFF6F2FF);
const _localEntryPoint = 'assets/valley/index.html';

void main() { WidgetsFlutterBinding.ensureInitialized(); runApp(const ValleyApp()); }

class ValleyApp extends StatelessWidget {
  const ValleyApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(title: 'Valley', debugShowCheckedModeBanner: false, theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: _valleyPurple, surface: _valleyBackground), useMaterial3: true), home: const ValleyShell());
}

class ValleyShell extends StatefulWidget {
  const ValleyShell({super.key});
  @override
  State<ValleyShell> createState() => _ValleyShellState();
}

class _ValleyShellState extends State<ValleyShell> {
  late final WebViewController _controller;
  late final ValleyApiBridge _apiBridge;
  bool _contentReady = false;
  String? _loadError;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController();
    _apiBridge = ValleyApiBridge(_controller);
    _controller
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(_valleyBackground)
      ..addJavaScriptChannel('ValleyNative', onMessageReceived: (message) => unawaited(_apiBridge.handle(message.message)))
      ..setNavigationDelegate(NavigationDelegate(onPageFinished: (_) => unawaited(_verifyRenderedContent()), onWebResourceError: (error) { if (error.isForMainFrame == true && mounted) setState(() { _contentReady = false; _loadError = error.description; }); }, onNavigationRequest: _handleNavigation))
      ..loadFlutterAsset(_localEntryPoint);
  }

  Future<void> _verifyRenderedContent() async {
    for (var attempt = 0; attempt < 20; attempt += 1) {
      if (!mounted) return;
      try {
        final result = await _controller.runJavaScriptReturningResult("""(() => { const root = document.getElementById('root'); return Boolean(root && root.childElementCount > 0 && root.innerText.trim().length > 20); })();""");
        if (result == true || result.toString().toLowerCase() == 'true') { if (mounted) setState(() { _contentReady = true; _loadError = null; }); return; }
      } catch (_) {}
      await Future<void>.delayed(const Duration(milliseconds: 500));
    }
    if (mounted) setState(() { _contentReady = false; _loadError = 'A interface não foi carregada por completo. Reinstale a versão corrigida.'; });
  }

  Future<NavigationDecision> _handleNavigation(NavigationRequest request) async {
    final uri = Uri.tryParse(request.url); if (uri == null) return NavigationDecision.prevent;
    if (uri.scheme == 'file' || uri.scheme == 'about' || uri.scheme == 'data') return NavigationDecision.navigate;
    if (uri.scheme == 'https' && uri.host == 'all-in-one-api-hub.web.app') return NavigationDecision.navigate;
    if (uri.scheme == 'mailto' || uri.scheme == 'tel') await launchUrl(uri, mode: LaunchMode.externalApplication);
    return NavigationDecision.prevent;
  }
  Future<void> _reload() async { setState(() { _contentReady = false; _loadError = null; }); await _controller.loadFlutterAsset(_localEntryPoint); }

  @override
  Widget build(BuildContext context) => Scaffold(backgroundColor: _valleyBackground, body: SafeArea(child: Stack(children: [WebViewWidget(key: const Key('valley-webview'), controller: _controller), if (!_contentReady && _loadError == null) const _LoadingSurface(), if (_contentReady) Semantics(label: 'Valley interface carregada', child: const SizedBox.shrink()), if (_loadError != null) _LoadFailure(message: _loadError!, onRetry: _reload)])));
}

class _LoadingSurface extends StatelessWidget {
  const _LoadingSurface();
  @override
  Widget build(BuildContext context) => const ColoredBox(color: _valleyBackground, child: Center(child: Padding(padding: EdgeInsets.all(32), child: Column(mainAxisSize: MainAxisSize.min, children: [Image(image: AssetImage('assets/brand/valley-logo-official.png'), width: 160), SizedBox(height: 24), SizedBox(width: 180, child: LinearProgressIndicator(color: _valleyPurple)), SizedBox(height: 12), Text('Carregando o Valley...')]))));
}

class _LoadFailure extends StatelessWidget {
  const _LoadFailure({required this.message, required this.onRetry});
  final String message; final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => ColoredBox(color: _valleyBackground, child: Center(child: Padding(padding: const EdgeInsets.all(32), child: Column(mainAxisSize: MainAxisSize.min, children: [const Image(image: AssetImage('assets/brand/valley-logo-official.png'), width: 160), const SizedBox(height: 24), const Text('Não foi possível abrir o Valley.', textAlign: TextAlign.center, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)), const SizedBox(height: 8), Text(message, textAlign: TextAlign.center, maxLines: 4, overflow: TextOverflow.ellipsis), const SizedBox(height: 24), FilledButton.icon(onPressed: onRetry, icon: const Icon(Icons.refresh), label: const Text('Tentar novamente'))]))));
}
