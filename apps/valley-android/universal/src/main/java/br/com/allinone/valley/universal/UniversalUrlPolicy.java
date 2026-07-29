package br.com.allinone.valley.universal;

import java.net.URI;
import java.net.URISyntaxException;

final class UniversalUrlPolicy {
    private final URI baseUri;

    private UniversalUrlPolicy(URI baseUri) {
        this.baseUri = baseUri;
    }

    static UniversalUrlPolicy from(String configuredUrl) {
        if (configuredUrl == null || configuredUrl.isBlank()) {
            throw new IllegalArgumentException("VALLEY_URL is required");
        }
        try {
            URI parsed = new URI(configuredUrl.trim());
            if (!"https".equalsIgnoreCase(parsed.getScheme())) {
                throw new IllegalArgumentException("VALLEY_URL must use HTTPS");
            }
            if (parsed.getHost() == null || parsed.getHost().isBlank()) {
                throw new IllegalArgumentException("VALLEY_URL must have a valid host");
            }
            if (parsed.getUserInfo() != null) {
                throw new IllegalArgumentException("VALLEY_URL cannot contain credentials");
            }
            URI normalized = new URI(
                "https",
                null,
                parsed.getHost().toLowerCase(),
                parsed.getPort(),
                normalizePath(parsed.getPath()),
                null,
                null
            );
            return new UniversalUrlPolicy(normalized);
        } catch (URISyntaxException exception) {
            throw new IllegalArgumentException("VALLEY_URL is invalid", exception);
        }
    }

    String baseUrl() {
        return baseUri.toString();
    }

    boolean isInternal(String candidateUrl) {
        if (candidateUrl == null || candidateUrl.isBlank()) {
            return false;
        }
        try {
            URI candidate = new URI(candidateUrl);
            return "https".equalsIgnoreCase(candidate.getScheme())
                && baseUri.getHost().equalsIgnoreCase(candidate.getHost())
                && effectivePort(baseUri) == effectivePort(candidate);
        } catch (URISyntaxException exception) {
            return false;
        }
    }

    private static int effectivePort(URI uri) {
        return uri.getPort() == -1 ? 443 : uri.getPort();
    }

    private static String normalizePath(String path) {
        if (path == null || path.isBlank()) {
            return "/";
        }
        return path.endsWith("/") ? path : path + "/";
    }
}
