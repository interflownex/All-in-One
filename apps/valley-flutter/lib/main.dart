import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:webview_flutter/webview_flutter.dart';

const _valleyPurple = Color(0xFF5D2CE6);
const _valleyBackground = Color(0xFFF6F2FF);
const _localEntryPoint = 'assets/valley/index.html';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ValleyApp());
}

class ValleyApp extends StatelessWidget {
  const ValleyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Valley',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: _valleyPurple,
          surface: _valleyBackground,
        ),
        useMaterial3: true,
      ),
      home: const ValleyShell(),
    );
  }
}

class ValleyShell extends StatefulWidget {
  const ValleyShell({super.key});

  @override
  State<ValleyShell> createState() => _ValleyShellState();
}

class _ValleyShellState extends State<ValleyShell> {
  late final WebViewController _controller;
  int _progress = 0;
  String? _loadError;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(_valleyBackground)
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (progress) {
            if (mounted) {
              setState(() => _progress = progress);
            }
          },
          onPageFinished: (_) {
            if (mounted) {
              setState(() {
                _progress = 100;
                _loadError = null;
              });
            }
          },
          onWebResourceError: (error) {
            if (error.isForMainFrame == true && mounted) {
              setState(() => _loadError = error.description);
            }
          },
          onNavigationRequest: _handleNavigation,
        ),
      )
      ..loadFlutterAsset(_localEntryPoint);
  }

  Future<NavigationDecision> _handleNavigation(
    NavigationRequest request,
  ) async {
    final uri = Uri.tryParse(request.url);
    if (uri == null) {
      return NavigationDecision.prevent;
    }

    if (uri.scheme == 'file' ||
        uri.scheme == 'about' ||
        uri.scheme == 'data' ||
        uri.scheme == 'https') {
      return NavigationDecision.navigate;
    }

    if (uri.scheme == 'mailto' || uri.scheme == 'tel') {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
    return NavigationDecision.prevent;
  }

  Future<void> _reload() async {
    setState(() {
      _progress = 0;
      _loadError = null;
    });
    await _controller.loadFlutterAsset(_localEntryPoint);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _valleyBackground,
      body: SafeArea(
        child: Stack(
          children: [
            WebViewWidget(controller: _controller),
            if (_progress < 100 && _loadError == null)
              const LinearProgressIndicator(color: _valleyPurple),
            if (_loadError != null)
              _LoadFailure(message: _loadError!, onRetry: _reload),
          ],
        ),
      ),
    );
  }
}

class _LoadFailure extends StatelessWidget {
  const _LoadFailure({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: _valleyBackground,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Image.asset(
                'assets/brand/valley-logo-official.png',
                width: 160,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 24),
              const Text(
                'Não foi possível abrir o Valley.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 8),
              Text(
                message,
                textAlign: TextAlign.center,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('Tentar novamente'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
