package br.com.allinone.admin;

import java.net.URI;
import java.net.URISyntaxException;

final class AdminUrlPolicy {
    private final URI baseUri;

    private AdminUrlPolicy(URI baseUri) {
        this.baseUri = baseUri;
    }

    static AdminUrlPolicy from(String rawUrl) {
        URI uri = parse(rawUrl);
        if (!"https".equalsIgnoreCase(uri.getScheme())) {
            throw new IllegalArgumentException("A1 Admin exige URL HTTPS.");
        }
        if (uri.getHost() == null || uri.getHost().isBlank()) {
            throw new IllegalArgumentException("A1 Admin exige host válido.");
        }
        if (uri.getUserInfo() != null) {
            throw new IllegalArgumentException("A1 Admin não aceita credenciais na URL.");
        }
        return new AdminUrlPolicy(uri.normalize());
    }

    String baseUrl() {
        return baseUri.toString();
    }

    boolean isInternal(String candidateUrl) {
        URI candidate;
        try {
            candidate = parse(candidateUrl).normalize();
        } catch (IllegalArgumentException ignored) {
            return false;
        }
        return "https".equalsIgnoreCase(candidate.getScheme())
            && baseUri.getHost().equalsIgnoreCase(candidate.getHost())
            && effectivePort(baseUri) == effectivePort(candidate);
    }

    private static URI parse(String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("URL do A1 Admin ausente.");
        }
        try {
            return new URI(value.trim());
        } catch (URISyntaxException exception) {
            throw new IllegalArgumentException("URL do A1 Admin inválida.", exception);
        }
    }

    private static int effectivePort(URI uri) {
        return uri.getPort() == -1 ? 443 : uri.getPort();
    }
}
