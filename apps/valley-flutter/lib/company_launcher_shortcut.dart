import 'dart:convert';
import 'dart:ui' as ui;

import 'package:flutter/services.dart';

/// Variantes visuais oficiais que podem envolver a logomarca empresarial.
enum ValleyBrandVariant { consumer, rider }

/// Resultado normalizado da solicitação feita ao launcher Android.
class CompanyShortcutResult {
  const CompanyShortcutResult({required this.supported, required this.requested});

  final bool supported;
  final bool requested;
}

/// Compõe o ícone localmente e delega somente a fixação ao Android.
///
/// O ícone principal do APK nunca é alterado. Em aparelhos incompatíveis, o
/// aplicativo continua disponível pelo ícone padrão.
class CompanyLauncherShortcut {
  CompanyLauncherShortcut({MethodChannel? channel})
      : _channel = channel ?? const MethodChannel(_channelName);

  static const _channelName = 'com.allinone.valley/company_shortcut';
  static const int _iconSize = 512;
  static const int _maxCompanyLogoBytes = 4 * 1024 * 1024;

  final MethodChannel _channel;

  Future<bool> isSupported() async =>
      await _channel.invokeMethod<bool>('isSupported') ?? false;

  Future<CompanyShortcutResult> pin({
    required String companyId,
    required String companyName,
    required Uint8List companyLogo,
    required ValleyBrandVariant variant,
  }) async {
    final normalizedCompanyId = companyId.trim();
    final normalizedCompanyName = companyName.trim();
    if (normalizedCompanyId.isEmpty || normalizedCompanyName.isEmpty) {
      throw ArgumentError('Empresa inválida para criação do atalho.');
    }
    if (companyLogo.isEmpty || companyLogo.lengthInBytes > _maxCompanyLogoBytes) {
      throw ArgumentError('Logomarca inválida ou acima do limite de 4 MiB.');
    }

    final supported = await isSupported();
    if (!supported) {
      return const CompanyShortcutResult(supported: false, requested: false);
    }

    final frameAsset = variant == ValleyBrandVariant.rider
        ? 'assets/brand/valley-rider-shortcut-frame.png'
        : 'assets/brand/valley-shortcut-frame.png';
    final icon = await _composeIcon(companyLogo, frameAsset);
    final requested = await _channel.invokeMethod<bool>('pin', {
          'companyId': normalizedCompanyId,
          'companyName': normalizedCompanyName,
          'variant': variant.name,
          'iconBase64': base64Encode(icon),
        }) ??
        false;
    return CompanyShortcutResult(supported: true, requested: requested);
  }

  Future<String?> initialCompanyId() =>
      _channel.invokeMethod<String>('initialCompanyId');

  Future<Uint8List> _composeIcon(Uint8List logoBytes, String frameAsset) async {
    final logo = await _decode(logoBytes);
    final frameData = await rootBundle.load(frameAsset);
    final frame = await _decode(frameData.buffer.asUint8List());
    final recorder = ui.PictureRecorder();
    final canvas = ui.Canvas(recorder);

    final logoBounds = ui.Rect.fromLTWH(
      _iconSize * .22,
      _iconSize * .20,
      _iconSize * .56,
      _iconSize * .52,
    );
    final fitted = _fitCenter(
      ui.Size(logo.width.toDouble(), logo.height.toDouble()),
      logoBounds,
    );
    canvas.drawImageRect(
      logo,
      ui.Rect.fromLTWH(0, 0, logo.width.toDouble(), logo.height.toDouble()),
      fitted,
      ui.Paint()..filterQuality = ui.FilterQuality.high,
    );
    canvas.drawImageRect(
      frame,
      ui.Rect.fromLTWH(0, 0, frame.width.toDouble(), frame.height.toDouble()),
      ui.Rect.fromLTWH(0, 0, _iconSize.toDouble(), _iconSize.toDouble()),
      ui.Paint()..filterQuality = ui.FilterQuality.high,
    );
    final image = await recorder.endRecording().toImage(_iconSize, _iconSize);
    final png = await image.toByteData(format: ui.ImageByteFormat.png);
    if (png == null) {
      throw StateError('Falha ao gerar o ícone personalizado.');
    }
    return png.buffer.asUint8List();
  }

  Future<ui.Image> _decode(Uint8List bytes) async {
    try {
      final codec = await ui.instantiateImageCodec(bytes);
      return (await codec.getNextFrame()).image;
    } on Exception catch (error) {
      throw FormatException('Imagem inválida para composição do ícone.', error);
    }
  }

  ui.Rect _fitCenter(ui.Size source, ui.Rect bounds) {
    final scale = source.width / source.height > bounds.width / bounds.height
        ? bounds.width / source.width
        : bounds.height / source.height;
    final width = source.width * scale;
    final height = source.height * scale;
    return ui.Rect.fromLTWH(
      bounds.center.dx - width / 2,
      bounds.center.dy - height / 2,
      width,
      height,
    );
  }
}
