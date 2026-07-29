package br.com.allinone.admin;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class AdminUrlPolicyTest {
    @Test
    public void acceptsSameHttpsOrigin() {
        AdminUrlPolicy policy = AdminUrlPolicy.from("https://admin.example.test/base/");

        assertTrue(policy.isInternal("https://admin.example.test/dashboard?mode=mobile"));
        assertTrue(policy.isInternal("https://admin.example.test:443/modules"));
    }

    @Test
    public void rejectsDifferentOrSpoofedOrigins() {
        AdminUrlPolicy policy = AdminUrlPolicy.from("https://admin.example.test/");

        assertFalse(policy.isInternal("https://evil.example.test/"));
        assertFalse(policy.isInternal("https://admin.example.test.evil.test/"));
        assertFalse(policy.isInternal("https://admin.example.test:8443/"));
        assertFalse(policy.isInternal("javascript:alert(1)"));
    }

    @Test
    public void rejectsInsecureOrCredentialedBaseUrls() {
        assertThrows(IllegalArgumentException.class, () -> AdminUrlPolicy.from("http://admin.example.test/"));
        assertThrows(IllegalArgumentException.class, () -> AdminUrlPolicy.from("https://user:pass@admin.example.test/"));
        assertThrows(IllegalArgumentException.class, () -> AdminUrlPolicy.from(" "));
    }
}
