package br.com.allinone.valley.universal;

import java.net.URI;
import java.net.URISyntaxException;

final class UniversalUrlPolicy {
    private static final String GOOGLE_AUTH_HOST = "accounts.google.com";

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
        URI candidate = parseSecureUri(candidateUrl);
        return candidate != null
            && baseUri.getHost().equalsIgnoreCase(candidate.getHost())
            && effectivePort(baseUri) == effectivePort(candidate);
    }

    boolean isAllowedAuthNavigation(String candidateUrl) {
        if (isInternal(candidateUrl)) {
            return true;
        }
        URI candidate = parseSecureUri(candidateUrl);
        return candidate != null
            && GOOGLE_AUTH_HOST.equalsIgnoreCase(candidate.getHost())
            && effectivePort(candidate) == 443;
    }

    boolean isSafeExternal(String candidateUrl) {
        return parseSecureUri(candidateUrl) != null;
    }

    private static URI parseSecureUri(String candidateUrl) {
        if (candidateUrl == null || candidateUrl.isBlank()) {
            return null;
        }
        try {
            URI candidate = new URI(candidateUrl);
            if (!"https".equalsIgnoreCase(candidate.getScheme())) {
                return null;
            }
            if (candidate.getHost() == null || candidate.getHost().isBlank()) {
                return null;
            }
            if (candidate.getUserInfo() != null) {
                return null;
            }
            return candidate;
        } catch (URISyntaxException exception) {
            return null;
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
