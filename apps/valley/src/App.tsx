import { type FormEvent, useCallback, useEffect, useState } from 'react';
import { AccountView, SettingsView } from './views/AccountSettings';
import { ConsumerHome } from './views/ConsumerHome';
import { MarketplaceView, StockView } from './views/ProductViews';
import { FinanceView, HealthView, LegalView, PropertyView } from './views/IntentViews';
import { JobsView } from './views/JobsView';
import { DeliveryView, LifeView, MobilityView, ServicesView } from './views/OperationalViews';
import {
  ValleyAvatarPicker,
  ValleyProfileAvatar,
  loadProfileAvatar,
  saveProfileAvatar,
} from './components/ValleyProfileAvatar';
import {
  deviceFingerprint,
  errorMessage,
  loadSession,
  request,
  saveSession,
  type JourneyHint,
  type JsonRecord,
  type Session,
  type ViewKey,
} from './lib/api';
import './functional.css';

type RouteState = { view: ViewKey; hint?: JourneyHint };

function App() {
  const [session, setSession] = useState<Session | null>(() => loadSession());
  const [route, setRoute] = useState<RouteState>({ view: 'home' });
  const [history, setHistory] = useState<RouteState[]>([]);
  const [notice, setNotice] = useState('');
  const [avatarDataUrl, setAvatarDataUrl] = useState('');

  const updateSession = useCallback((next: Session | null) => {
    saveSession(next);
    setSession(next);
  }, []);

  const navigate = useCallback((view: ViewKey, hint?: JourneyHint) => {
    setHistory(current => [...current.slice(-19), route]);
    setRoute({ view, hint });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [route]);

  const goHome = useCallback(() => {
    setHistory([]);
    setRoute({ view: 'home' });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const goBack = useCallback(() => {
    setHistory(current => {
      const previous = current.at(-1) ?? { view: 'home' as ViewKey };
      setRoute(previous);
      return current.slice(0, -1);
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const refreshSession = useCallback(async () => {
    if (!session) return;
    const data = await request<JsonRecord>('/auth/refresh', 'POST', {
      refresh_token: session.refreshToken,
      device_fingerprint: deviceFingerprint(),
    });
    updateSession({
      ...session,
      accessToken: String(data.access_token),
      refreshToken: String(data.refresh_token),
      sessionId: String(data.session_id),
      expiresAt: String(data.expires_at),
      refreshExpiresAt: String(data.refresh_expires_at),
    });
  }, [session, updateSession]);

  useEffect(() => {
    if (!session) {
      setAvatarDataUrl('');
      return;
    }
    setAvatarDataUrl(loadProfileAvatar(session.userId));
    const listener = (event: Event) => {
      const detail = (event as CustomEvent<{ userId: string; dataUrl: string }>).detail;
      if (detail?.userId === session.userId) setAvatarDataUrl(detail.dataUrl);
    };
    window.addEventListener('valley-profile-avatar-changed', listener);
    return () => window.removeEventListener('valley-profile-avatar-changed', listener);
  }, [session]);

  useEffect(() => {
    if (!session) return;
    const timer = window.setInterval(() => {
      if (Date.parse(session.expiresAt) - Date.now() < 90000) {
        refreshSession().catch(() => {
          updateSession(null);
          setNotice('Sua sessão expirou. Entre novamente.');
        });
      }
    }, 30000);
    return () => window.clearInterval(timer);
  }, [refreshSession, session, updateSession]);

  const logout = useCallback(async () => {
    if (session) {
      await request('/auth/logout', 'POST', {
        refresh_token: session.refreshToken,
        device_fingerprint: deviceFingerprint(),
      }).catch(() => undefined);
    }
    updateSession(null);
    setHistory([]);
    setRoute({ view: 'home' });
  }, [session, updateSession]);

  const authenticated = useCallback((next: Session, pendingAvatar: string) => {
    updateSession(next);
    if (pendingAvatar) saveProfileAvatar(next.userId, pendingAvatar);
    setHistory([]);
    setRoute({ view: 'home' });
  }, [updateSession]);

  if (!session) return <AuthScreen notice={notice} onAuthenticated={authenticated} />;

  const props = { session, setNotice };
  const view = route.view;
  const immersiveFeed = (view === 'marketplace' && (route.hint?.mode ?? 'feed') === 'feed') || view === 'stock';
  const feedNavigation = {
    avatarDataUrl,
    onHome: goHome,
    onBack: goBack,
    onProfile: () => navigate('account'),
  };

  return <div className={`app-shell ${immersiveFeed ? 'immersive-shell' : ''}`}>
    {!immersiveFeed && <header className='topbar'>
      <button className='brand-button' type='button' onClick={goHome} aria-label='Ir para o início'>
        <img src='/assets/brand/valley-logo-official.png' alt='Valley' />
      </button>
      <div className='topbar-actions'>
        <div className='connection-pill'><span className='status-dot' />Sincronizado</div>
        <button className='profile-shortcut' type='button' onClick={() => navigate('account')} aria-label='Abrir perfil'>
          <ValleyProfileAvatar src={avatarDataUrl} size='small' />
        </button>
      </div>
    </header>}

    {notice && <button className='global-notice' type='button' onClick={() => setNotice('')}>{notice}<span> ×</span></button>}

    <main className={`app-content ${immersiveFeed ? 'immersive-content' : ''}`}>
      {view === 'home' && <ConsumerHome onNavigate={navigate} />}
      {view === 'marketplace' && <MarketplaceView {...props} hint={route.hint} {...feedNavigation} />}
      {view === 'stock' && <StockView {...props} hint={route.hint} {...feedNavigation} />}
      {view === 'finance' && <FinanceView {...props} hint={route.hint} />}
      {view === 'jobs' && <JobsView {...props} hint={route.hint} />}
      {view === 'services' && <ServicesView {...props} hint={route.hint} />}
      {view === 'legal' && <LegalView {...props} hint={route.hint} />}
      {view === 'health' && <HealthView {...props} hint={route.hint} />}
      {view === 'property' && <PropertyView {...props} hint={route.hint} />}
      {view === 'delivery' && <DeliveryView {...props} />}
      {view === 'mobility' && <MobilityView {...props} />}
      {view === 'life' && <LifeView {...props} />}
      {view === 'account' && <AccountView {...props} avatarDataUrl={avatarDataUrl} onAvatarChange={value => saveProfileAvatar(session.userId, value)} onSessionChange={updateSession} />}
      {view === 'settings' && <SettingsView {...props} onRefreshSession={refreshSession} onLogout={logout} />}
    </main>

    {!immersiveFeed && <BottomNav route={route} navigate={navigate} />}
  </div>;
}

function AuthScreen({ notice, onAuthenticated }: { notice: string; onAuthenticated: (session: Session, avatarDataUrl: string) => void }) {
  const [registering, setRegistering] = useState(false);
  const [fullName, setFullName] = useState('');
  const [cpf, setCpf] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [accepted, setAccepted] = useState(false);
  const [avatarDataUrl, setAvatarDataUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (registering) {
        if (!accepted) throw new Error('Aceite os termos e a privacidade.');
        const now = new Date().toISOString();
        await request('/registrations', 'POST', {
          full_name: fullName.trim(),
          email: email.trim().toLowerCase(),
          password_hash: password,
          document_cpf: cpf.replace(/\D/g, ''),
          terms_accepted_at: now,
          lgpd_consent_at: now,
          profile_avatar_mode: avatarDataUrl ? 'personalized_valley_frame' : 'official_default',
        });
      }

      const data = await request<JsonRecord>('/auth/login', 'POST', {
        email: email.trim().toLowerCase(),
        password,
      });
      onAuthenticated({
        accessToken: String(data.access_token),
        refreshToken: String(data.refresh_token),
        userId: String(data.user_id),
        sessionId: String(data.session_id),
        email: email.trim().toLowerCase(),
        expiresAt: String(data.expires_at),
        refreshExpiresAt: String(data.refresh_expires_at),
      }, avatarDataUrl);
    } catch (err) {
      const message = errorMessage(err);
      if (!registering && /credenciais|cadastro|conta/i.test(message)) {
        setRegistering(true);
        setError('Não foi possível validar um cadastro ativo. Conclua o cadastro ou volte para corrigir seus dados de acesso.');
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  return <main className='auth-page'>
    <section className='auth-card'>
      <img className='auth-logo' src='/assets/brand/valley-logo-official.png' alt='Valley' />
      <h1>{registering ? 'Crie sua conta Valley' : 'Entre no Valley'}</h1>
      <p>{registering ? 'Conclua seu cadastro para acessar a Home.' : 'Somente usuários autenticados entram no aplicativo.'}</p>
      {notice && <div className='notice warning'>{notice}</div>}
      <form onSubmit={submit}>
        {registering && <>
          <label>Nome completo<input value={fullName} onChange={event => setFullName(event.target.value)} required /></label>
          <label>CPF<input inputMode='numeric' value={cpf} onChange={event => setCpf(event.target.value)} required minLength={11} /></label>
          <ValleyAvatarPicker value={avatarDataUrl} onChange={setAvatarDataUrl} onError={setError} />
        </>}
        <label>E-mail<input type='email' value={email} onChange={event => setEmail(event.target.value)} required /></label>
        <label>Senha<input type='password' value={password} onChange={event => setPassword(event.target.value)} required minLength={6} /></label>
        {registering && <label className='checkbox-row'><input type='checkbox' checked={accepted} onChange={event => setAccepted(event.target.checked)} />Aceito os termos e o tratamento necessário dos dados.</label>}
        {error && <div className='notice error'>{error}</div>}
        <button className='primary' type='submit' disabled={loading}>{loading ? 'Conectando...' : registering ? 'Cadastrar e entrar' : 'Entrar'}</button>
        <button className='text-button' type='button' onClick={() => { setRegistering(value => !value); setError(''); }}>{registering ? 'Já tenho cadastro ativo' : 'Ainda não tenho cadastro'}</button>
      </form>
    </section>
  </main>;
}

function BottomNav({ route, navigate }: { route: RouteState; navigate: (view: ViewKey, hint?: JourneyHint) => void }) {
  const items: Array<{ key: ViewKey; label: string; icon: string; hint?: JourneyHint; active: ViewKey[] }> = [
    { key: 'home', label: 'Início', icon: '⌂', active: ['home', 'delivery', 'mobility', 'life', 'legal', 'health', 'property', 'services'] },
    { key: 'marketplace', label: 'Comprar', icon: '▦', hint: { intent: 'comprar', mode: 'feed' }, active: ['marketplace', 'stock'] },
    { key: 'finance', label: 'Financeiro', icon: '◈', active: ['finance'] },
    { key: 'jobs', label: 'Trabalhar', icon: '✦', hint: { intent: 'trabalhar', mode: 'seek' }, active: ['jobs'] },
    { key: 'account', label: 'Conta', icon: '●', active: ['account', 'settings'] },
  ];
  return <nav className='bottom-nav' aria-label='Navegação principal'>
    {items.map(item => <button key={item.key} type='button' className={item.active.includes(route.view) ? 'active' : ''} onClick={() => navigate(item.key, item.hint)}><span>{item.icon}</span><small>{item.label}</small></button>)}
  </nav>;
}

export default App;
