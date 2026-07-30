package br.com.allinone.valley.universal;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class UniversalUrlPolicyTest {
    private static UniversalUrlPolicy policy() {
        return UniversalUrlPolicy.from(
            "https://84e9680fcfa2a84551.v2.appdeploy.ai/"
        );
    }

    @Test
    public void acceptsAndNormalizesSecureBaseUrl() {
        UniversalUrlPolicy policy = UniversalUrlPolicy.from(
            "https://84e9680fcfa2a84551.v2.appdeploy.ai"
        );
        assertEquals(
            "https://84e9680fcfa2a84551.v2.appdeploy.ai/",
            policy.baseUrl()
        );
    }

    @Test
    public void recognizesOnlySameSecureOriginAsInternal() {
        UniversalUrlPolicy policy = policy();
        assertTrue(policy.isInternal(
            "https://84e9680fcfa2a84551.v2.appdeploy.ai/#/rider"
        ));
        assertFalse(policy.isInternal("https://example.com/"));
        assertFalse(policy.isInternal(
            "http://84e9680fcfa2a84551.v2.appdeploy.ai/"
        ));
        assertFalse(policy.isInternal(
            "https://84e9680fcfa2a84551.v2.appdeploy.ai:444/"
        ));
    }

    @Test
    public void allowsOnlyValleyAndExactGoogleAccountOriginInsideAuthPopup() {
        UniversalUrlPolicy policy = policy();
        assertTrue(policy.isAllowedAuthNavigation(
            "https://84e9680fcfa2a84551.v2.appdeploy.ai/auth/callback"
        ));
        assertTrue(policy.isAllowedAuthNavigation(
            "https://accounts.google.com/o/oauth2/v2/auth"
        ));
        assertFalse(policy.isAllowedAuthNavigation(
            "https://accounts.google.com.evil.example/"
        ));
        assertFalse(policy.isAllowedAuthNavigation(
            "https://accounts.google.com:444/o/oauth2/v2/auth"
        ));
        assertFalse(policy.isAllowedAuthNavigation(
            "http://accounts.google.com/o/oauth2/v2/auth"
        ));
    }

    @Test
    public void acceptsOnlyCredentialFreeHttpsAsSafeExternalDestination() {
        UniversalUrlPolicy policy = policy();
        assertTrue(policy.isSafeExternal("https://example.com/terms"));
        assertFalse(policy.isSafeExternal("http://example.com/"));
        assertFalse(policy.isSafeExternal("javascript:alert(1)"));
        assertFalse(policy.isSafeExternal("intent://example.com/#Intent;scheme=https;end"));
        assertFalse(policy.isSafeExternal("https://user:secret@example.com/"));
        assertFalse(policy.isSafeExternal("https:///missing-host"));
    }

    @Test
    public void rejectsInsecureOrCredentialedConfiguration() {
        assertThrows(
            IllegalArgumentException.class,
            () -> UniversalUrlPolicy.from("http://example.com/")
        );
        assertThrows(
            IllegalArgumentException.class,
            () -> UniversalUrlPolicy.from("https://user:secret@example.com/")
        );
        assertThrows(
            IllegalArgumentException.class,
            () -> UniversalUrlPolicy.from("   ")
        );
    }
}
