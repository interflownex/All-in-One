package br.com.allinone.valley.universal;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThrows;

import org.junit.Test;

public final class UniversalUrlPolicyTest {
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
        UniversalUrlPolicy policy = UniversalUrlPolicy.from(
            "https://84e9680fcfa2a84551.v2.appdeploy.ai/"
        );
        assertTrue(policy.isInternal(
            "https://84e9680fcfa2a84551.v2.appdeploy.ai/#/rider"
        ));
        assertFalse(policy.isInternal("https://example.com/"));
        assertFalse(policy.isInternal(
            "http://84e9680fcfa2a84551.v2.appdeploy.ai/"
        ));
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
    }
}
