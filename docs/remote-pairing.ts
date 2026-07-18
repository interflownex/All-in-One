export interface PairingSession {
  deviceId: string;
  code: string;
  createdAt: number;
  expiresAt: number;
}

export class RemotePairingService {
  private readonly sessions = new Map<string, PairingSession>();

  constructor(private readonly ttlMs: number = 5 * 60 * 1000) {}

  generateCode(length: number = 6): string {
    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    let result = "";

    for (let i = 0; i < length; i += 1) {
      const index = Math.floor(Math.random() * chars.length);
      result += chars[index];
    }

    return result;
  }

  createSession(deviceId: string): PairingSession {
    const code = this.generateCode();
    const session: PairingSession = {
      deviceId,
      code,
      createdAt: Date.now(),
      expiresAt: Date.now() + this.ttlMs,
    };

    this.sessions.set(deviceId, session);
    return session;
  }

  validateCode(deviceId: string, inputCode: string): boolean {
    const session = this.sessions.get(deviceId);
    if (!session) {
      return false;
    }

    if (Date.now() > session.expiresAt) {
      this.sessions.delete(deviceId);
      return false;
    }

    return session.code.toUpperCase() === inputCode.trim().toUpperCase();
  }

  consumeCode(deviceId: string, inputCode: string): boolean {
    const isValid = this.validateCode(deviceId, inputCode);
    if (isValid) {
      this.sessions.delete(deviceId);
    }
    return isValid;
  }
}

export function exampleUsage() {
  const service = new RemotePairingService();
  const session = service.createSession("device-001");

  console.log(`Código de pareamento: ${session.code}`);
  console.log(`Valido: ${service.validateCode("device-001", session.code)}`);
}
