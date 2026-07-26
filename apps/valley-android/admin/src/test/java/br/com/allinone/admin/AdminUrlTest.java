package br.com.allinone.admin;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class AdminUrlTest {
    @Test
    public void adminUrlUsesHttpsAndDoesNotReferenceVision() {
        assertTrue(BuildConfig.ADMIN_URL.startsWith("https://"));
        assertFalse(BuildConfig.ADMIN_URL.toLowerCase().contains("vision"));
    }
}
