import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:webview_flutter/webview_flutter.dart';

const _apiHubOrigin = 'https://all-in-one-api-hub.web.app';
const _maxResponseBytes = 4 * 1024 * 1024;

class ValleyApiBridge {
  ValleyApiBridge(this.controller);

  final WebViewController controller;

  Future<void> handle(String rawMessage) async {
    var id = 'unknown';
    try {
      final decoded = jsonDecode(rawMessage);
      if (decoded is! Map<String, dynamic>) {
        throw const FormatException('Mensagem inválida.');
      }
      id = decoded['id']?.toString() ?? 'unknown';
      final path = decoded['path']?.toString() ?? '';
      final method = (decoded['method']?.toString() ?? 'GET').toUpperCase();
      final token = decoded['token']?.toString();
      final body = decoded['body']?.toString();
      final forwardedHeaders = decoded['headers'];
      if (!path.startsWith('/') || path.startsWith('//')) {
        throw const FormatException('Caminho inválido.');
      }
      if (!{'GET', 'POST', 'PUT', 'PATCH', 'DELETE'}.contains(method)) {
        throw const FormatException('Método não permitido.');
      }
      final uri = Uri.parse('$_apiHubOrigin$path');
      if (uri.scheme != 'https' || uri.host != Uri.parse(_apiHubOrigin).host) {
        throw const FormatException('Destino não permitido.');
      }
      final client = HttpClient()
        ..connectionTimeout = const Duration(seconds: 8);
      try {
        final request = await client
            .openUrl(method, uri)
            .timeout(const Duration(seconds: 12));
        request.headers.set(HttpHeaders.acceptHeader, 'application/json');
        request.headers.set('X-Valley-Api-Version', '1');
        if (token != null && token.isNotEmpty && token != 'null') {
          request.headers.set(HttpHeaders.authorizationHeader, 'Bearer $token');
        }
        if (forwardedHeaders is Map) {
          for (final entry in forwardedHeaders.entries) {
            final name = entry.key.toString();
            final value = entry.value?.toString() ?? '';
            if (_safeHeader(name) && value.isNotEmpty) {
              request.headers.set(name, value);
            }
          }
        }
        if (body != null && body.isNotEmpty && body != 'null') {
          request.headers.contentType = ContentType.json;
          request.write(body);
        }
        final response = await request.close().timeout(
          const Duration(seconds: 20),
        );
        final bytes = <int>[];
        await for (final chunk in response.timeout(
          const Duration(seconds: 20),
        )) {
          bytes.addAll(chunk);
          if (bytes.length > _maxResponseBytes) {
            throw const FormatException('Resposta acima do limite.');
          }
        }
        final text = utf8.decode(bytes, allowMalformed: false);
        Object responseBody = <String, Object?>{};
        if (text.trim().isNotEmpty) {
          responseBody = jsonDecode(text);
        }
        final headers = <String, String>{};
        response.headers.forEach(
          (name, values) => headers[name] = values.join(','),
        );
        await _resolve(id, {
          'id': id,
          'ok': response.statusCode >= 200 && response.statusCode < 300,
          'status': response.statusCode,
          'body': responseBody,
          'headers': headers,
        });
      } finally {
        client.close(force: true);
      }
    } catch (error) {
      await _resolve(id, {
        'id': id,
        'ok': false,
        'status': 0,
        'body': {'detail': 'Falha ao comunicar com o servidor Valley.'},
        'headers': <String, String>{},
        'error': error.toString(),
      });
    }
  }

  bool _safeHeader(String name) => {
    'content-type',
    'x-device-fingerprint',
    'x-play-integrity-token',
    'x-correlation-id',
    'x-idempotency-key',
  }.contains(name.toLowerCase());

  Future<void> _resolve(String id, Map<String, Object?> response) =>
      controller.runJavaScript(
        'window.__valleyNativeResolve && '
        'window.__valleyNativeResolve(${jsonEncode(id)}, '
        '${jsonEncode(response)});',
      );
}
