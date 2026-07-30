import { type FormEvent, useCallback, useEffect, useState } from 'react';
import { AccountView, SettingsView } from './views/AccountSettings';
import { CommerceView } from './views/CommerceView';
import { HomeView } from './views/HomeView';
import { DeliveryView, LifeView, MobilityView, ServicesView } from './views/OperationalViews';
import { deviceFingerprint, errorMessage, loadSession, request, saveSession, type JsonRecord, type Session, type ViewKey } from './lib/api';
import './functional.css';

function App() {
  const [session, setSession] = useState<Session | null>(() => loadSession());
  const [view, setView] = useState<ViewKey>('home');
  const [notice, setNotice] = useState('');
  const updateSession = useCallback((next: Session | null) => { saveSession(next); setSession(next); }, []);
  const refreshSession = useCallback(async () => {
    if (!session) return;
    const data = await request<JsonRecord>('/auth/refresh', 'POST', { refresh_token: session.refreshToken, device_fingerprint: deviceFingerprint() });
    updateSession({ ...session, accessToken: String(data.access_token), refreshToken: String(data.refresh_token), sessionId: String(data.session_id), expiresAt: String(data.expires_at), refreshExpiresAt: String(data.refresh_expires_at) });
  }, [session, updateSession]);
  useEffect(() => {
    if (!session) return;
    const timer = window.setInterval(() => { if (Date.parse(session.expiresAt) - Date.now() < 90000) refreshSession().catch(() => { updateSession(null); setNotice('Sua sessão expirou. Entre novamente.'); }); }, 30000);
    return () => window.clearInterval(timer);
  }, [refreshSession, session, updateSession]);
  const logout = useCallback(async () => {
    if (session) await request('/auth/logout', 'POST', { refresh_token: session.refreshToken, device_fingerprint: deviceFingerprint() }).catch(() => undefined);
    updateSession(null); setView('home');
  }, [session, updateSession]);
  if (!session) return <AuthScreen notice={notice} onAuthenticated={updateSession} />;
  const props = { session, setNotice };
  return <div className='app-shell'>
    <header className='topbar'><button className='brand-button' type='button' onClick={() => setView('home')} aria-label='Ir para o início'><img src='/assets/brand/valley-logo-official.png' alt='Valley' /></button><div className='connection-pill'><span className='status-dot' />Servidor sincronizado</div></header>
    {notice && <button className='global-notice' type='button' onClick={() => setNotice('')}>{notice}<span> ×</span></button>}
    <main className='app-content'>
      {view === 'home' && <HomeView {...props} />}{view === 'commerce' && <CommerceView {...props} />}{view === 'services' && <ServicesView {...props} />}{view === 'delivery' && <DeliveryView {...props} />}{view === 'mobility' && <MobilityView {...props} />}{view === 'life' && <LifeView {...props} />}{view === 'account' && <AccountView {...props} onSessionChange={updateSession} />}{view === 'settings' && <SettingsView {...props} onRefreshSession={refreshSession} onLogout={logout} />}
    </main><BottomNav view={view} setView={setView} />
  </div>;
}

function AuthScreen({ notice, onAuthenticated }: { notice: string; onAuthenticated: (session: Session) => void }) {
  const [registering, setRegistering] = useState(false); const [fullName, setFullName] = useState(''); const [cpf, setCpf] = useState(''); const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [accepted, setAccepted] = useState(false); const [loading, setLoading] = useState(false); const [error, setError] = useState('');
  const submit = async (event: FormEvent) => { event.preventDefault(); setLoading(true); setError(''); try {
    if (registering) { if (!accepted) throw new Error('Aceite os termos e a privacidade.'); const now = new Date().toISOString(); await request('/registrations', 'POST', { full_name: fullName.trim(), email: email.trim().toLowerCase(), password_hash: password, document_cpf: cpf.replace(/\D/g, ''), terms_accepted_at: now, lgpd_consent_at: now }); }
    const data = await request<JsonRecord>('/auth/login', 'POST', { email: email.trim().toLowerCase(), password });
    onAuthenticated({ accessToken: String(data.access_token), refreshToken: String(data.refresh_token), userId: String(data.user_id), sessionId: String(data.session_id), email: email.trim().toLowerCase(), expiresAt: String(data.expires_at), refreshExpiresAt: String(data.refresh_expires_at) });
  } catch (err) { setError(errorMessage(err)); } finally { setLoading(false); } };
  return <main className='auth-page'><section className='auth-card'><img className='auth-logo' src='/assets/brand/valley-logo-official.png' alt='Valley' /><h1>{registering ? 'Crie sua conta Valley' : 'Entre no Valley'}</h1><p>Produtos, serviços, mobilidade, trabalho, saúde e documentos em um único acesso.</p>{notice && <div className='notice warning'>{notice}</div>}<form onSubmit={submit}>{registering && <><label>Nome completo<input value={fullName} onChange={e => setFullName(e.target.value)} required /></label><label>CPF<input inputMode='numeric' value={cpf} onChange={e => setCpf(e.target.value)} required minLength={11} /></label></>}<label>E-mail<input type='email' value={email} onChange={e => setEmail(e.target.value)} required /></label><label>Senha<input type='password' value={password} onChange={e => setPassword(e.target.value)} required minLength={6} /></label>{registering && <label className='checkbox-row'><input type='checkbox' checked={accepted} onChange={e => setAccepted(e.target.checked)} />Aceito os termos e o tratamento necessário dos dados.</label>}{error && <div className='notice error'>{error}</div>}<button className='primary' type='submit' disabled={loading}>{loading ? 'Conectando...' : registering ? 'Cadastrar e entrar' : 'Entrar'}</button><button className='text-button' type='button' onClick={() => setRegistering(value => !value)}>{registering ? 'Já tenho uma conta' : 'Criar uma conta'}</button></form></section></main>;
}
function BottomNav({ view, setView }: { view: ViewKey; setView: (view: ViewKey) => void }) {
  const items: [ViewKey, string, string][] = [['home','Início','⌂'],['commerce','Pedidos','▣'],['services','Serviços','◫'],['delivery','Entrega','➜'],['mobility','Mobilidade','◇'],['life','Vida','✦'],['account','Conta','●'],['settings','Ajustes','⚙']];
  return <nav className='bottom-nav' aria-label='Navegação principal'>{items.map(([key,label,icon]) => <button key={key} type='button' className={view === key ? 'active' : ''} onClick={() => setView(key)}><span>{icon}</span><small>{label}</small></button>)}</nav>;
}
export default App;
