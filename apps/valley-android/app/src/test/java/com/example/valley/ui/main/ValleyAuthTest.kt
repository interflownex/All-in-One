package com.example.valley.ui.main

import junit.framework.TestCase.assertEquals
import junit.framework.TestCase.assertTrue
import org.junit.Test

class ValleyAuthTest {
  @Test
  fun valleyGooglePassword_isDeterministic() {
    val email = "usuario@exemplo.com"
    assertEquals(valleyGooglePasswordFor(email), valleyGooglePasswordFor(email))
  }

  @Test
  fun valleyDisplayName_formatsEmailLocalPart() {
    assertEquals("ana maria", valleyDisplayName("ana.maria@exemplo.com"))
  }

  @Test
  fun valleyCpfForEmail_hasExpectedPrefix() {
    val cpf = valleyCpfForEmail("teste@exemplo.com")
    assertTrue(cpf.startsWith("CPF-"))
    assertEquals(16, cpf.length)
  }
}
