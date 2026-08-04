import {
  type FormEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';
import { AccountView, SettingsView } from './views/AccountSettings';
import { ConsumerHome } from './views/ConsumerHome';
import { MarketplaceView, StockView } from './views/ProductViews';
import {
  FinanceView,
  HealthView,
  LegalView,
  PropertyView,
} from './views/IntentViews';
import { JobsView } from './views/JobsView';
import {
  DeliveryView,
  LifeView,
  MobilityView,
  ServicesView,
} from './views/OperationalViews';
import {
  ValleyAvatarPicker,
  ValleyProfileAvatar,
} from './components/ValleyProfileAvatar';
import {
  loadProfileAvatar,
  saveProfileAvatar,
} from './lib/profileAvatarStorage';
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
import './valley_experience.css';
import './product_feed.css';

type RouteState = { view: ViewKey; hint?: JourneyHint };
type AuthMode = 'welcome' | 'login' | 'register';

function App() {
  const [session, setSession] = useState<Session | null>(() => loadSession());
  const [route, setRoute] = useState<RouteState>({ view: 'home' });
  const [notice, setNotice] = useState('');
  const [avatarDataUrl, setAvatarDataUrl] = useState(() => {
    const active = loadSession();
    return active ? loadProfileAvatar(active.userId) : '';
  });
  const routeHistory = useRef<RouteState[]>([]);

  const updateSession = useCallback((next: Session | null) => {
    saveSession(next);
    setSession(next);
    setAvatarDataUrl(next ? loadProfileAvatar(next.userId) : '');
  }, []);

  const navigate = useCallback((view: ViewKey, hint?: JourneyHint) => {
    setRoute(current => {
      routeHistory.current = [...routeHistory.current.slice(-19), current];
      return { view, hint };
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const goHome = useCallback(() => {
    routeHistory.current = [];
    setRoute({ view: 'home' });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const goBack = useCallback(() => {
    const previous = routeHistory.current.pop() ?? { view: 'home' as ViewKey };
    setRoute(previous);
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
    if (!session) return;
    const userId = session.userId;
    const listener = (event: Event) => {
      const detail = (
        event as CustomEvent<{ userId: string; dataUrl: string }>
      ).detail;
      if (detail?.userId === userId) setAvatarDataUrl(detail.dataUrl);
    };
    window.addEventListener('valley-profile-avatar-changed', listener);
    return () => {
      window.removeEventListener('valley-profile-avatar-changed', listener);
    };
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
    routeHistory.current = [];
    setRoute({ view: 'home' });
  }, [session, updateSession]);

  const authenticated = useCallback((next: Session, pendingAvatar: string) => {
    updateSession(next);
    if (pendingAvatar) {
      saveProfileAvatar(next.userId, pendingAvatar);
      setAvatarDataUrl(pendingAvatar);
    }
    routeHistory.current = [];
    setRoute({ view: 'home' });
  }, [updateSession]);

  if (!session) {
    return <AuthScreen
      notice={notice}
      setNotice={setNotice}
      onAuthenticated={authenticated}
    />;
  }

  const props = { session, setNotice };
  const view = route.view;
  const immersiveFeed = (
    view === 'marketplace' && (route.hint?.mode ?? 'feed') === 'feed'
  ) || view === 'stock';
  const feedNavigation = {
    avatarDataUrl,
    onHome: goHome,
    onBack: goBack,
    onProfile: () => navigate('account'),
  };

  return <div className={`app-shell ${immersiveFeed ? 'immersive-shell' : ''}`}>
    {!immersiveFeed && <header className='topbar'>
      <button
        className='brand-button'
        type='button'
        onClick={goHome}
        aria-label='Ir para o início'
      >
        <img src='/assets/brand/valley-logo-official.png' alt='Valley' />
      </button>
      <div className='topbar-actions'>
        <div className='connection-pill'>
          <span className='status-dot' />Sincronizado
        </div>
        <button
          className='profile-shortcut'
          type='button'
          onClick={() => navigate('account')}
          aria-label='Abrir perfil'
        >
          <ValleyProfileAvatar src={avatarDataUrl} size='small' />
        </button>
      </div>
    </header>}

    {notice && <button
      className='global-notice'
      type='button'
      onClick={() => setNotice('')}
    >
      {notice}<span> ×</span>
    </button>}

    <main className={`app-content ${immersiveFeed ? 'immersive-content' : ''}`}>
      {view === 'home' && <ConsumerHome onNavigate={navigate} />}
      {view === 'marketplace' && <MarketplaceView
        {...props}
        hint={route.hint}
        {...feedNavigation}
      />}
      {view === 'stock' && <StockView
        {...props}
        hint={route.hint}
        {...feedNavigation}
      />}
      {view === 'finance' && <FinanceView {...props} hint={route.hint} />}
      {view === 'jobs' && <JobsView {...props} hint={route.hint} />}
      {view === 'services' && <ServicesView {...props} hint={route.hint} />}
      {view === 'legal' && <LegalView {...props} hint={route.hint} />}
      {view === 'health' && <HealthView {...props} hint={route.hint} />}
      {view === 'property' && <PropertyView {...props} hint={route.hint} />}
      {view === 'delivery' && <DeliveryView {...props} />}
      {view === 'mobility' && <MobilityView {...props} />}
      {view === 'life' && <LifeView {...props} />}
      {view === 'account' && <AccountView
        {...props}
        avatarDataUrl={avatarDataUrl}
        onAvatarChange={value => saveProfileAvatar(session.userId, value)}
        onSessionChange={updateSession}
      />}
      {view === 'settings' && <SettingsView
        {...props}
        onRefreshSession={refreshSession}
        onLogout={logout}
      />}
    </main>

    {!immersiveFeed && <BottomNav route={route} navigate={navigate} />}
  </div>;
}

function AuthScreen({
  notice,
  setNotice,
  onAuthenticated,
}: {
  notice: string;
  setNotice: (message: string) => void;
  onAuthenticated: (session: Session, avatarDataUrl: string) => void;
}) {
  const [mode, setMode] = useState<AuthMode>('welcome');
  const [fullName, setFullName] = useState('');
  const [cpf, setCpf] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [accepted, setAccepted] = useState(false);
  const [avatarDataUrl, setAvatarDataUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [loginAttempts, setLoginAttempts] = useState(0);
  const normalizedCpf = cpf.replace(/\D/g, '');

  const authenticate = async () => {
    const data = await request<JsonRecord>('/auth/login', 'POST', {
      email: authEmail(normalizedCpf),
      password,
    });
    onAuthenticated({
      accessToken: String(data.access_token),
      refreshToken: String(data.refresh_token),
      userId: String(data.user_id),
      sessionId: String(data.session_id),
      email: normalizedCpf,
      expiresAt: String(data.expires_at),
      refreshExpiresAt: String(data.refresh_expires_at),
    }, avatarDataUrl);
  };

  const submitLogin = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      validateCpf(normalizedCpf);
      await authenticate();
    } catch (caught) {
      setLoginAttempts(current => current + 1);
      setError(errorMessage(caught));
    } finally {
      setLoading(false);
    }
  };

  const submitRegistration = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      validateCpf(normalizedCpf);
      if (!accepted) {
        throw new Error('Aceite os termos e a política de privacidade.');
      }
      const now = new Date().toISOString();
      await request('/registrations', 'POST', {
        full_name: fullName.trim(),
        email: authEmail(normalizedCpf),
        contact_email: contactEmail.trim().toLowerCase() || null,
        phone_e164: normalizeBrazilPhone(phone),
        password_hash: password,
        document_cpf: normalizedCpf,
        cpf_document: normalizedCpf,
        terms_accepted_at: now,
        lgpd_consent_at: now,
        profile_avatar_mode: avatarDataUrl
          ? 'personalized_valley_frame'
          : 'official_default',
        launcher_icon_policy: 'official_valley_only',
      });
      await authenticate();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setLoading(false);
    }
  };

  const requestRecovery = async () => {
    setLoading(true);
    setError('');
    try {
      validateCpf(normalizedCpf);
      const response = await request<JsonRecord>(
        '/identity/valley/access-recovery',
        'POST',
        {
          cpf: normalizedCpf,
          device_fingerprint: deviceFingerprint(),
        },
      );
      setNotice(String(
        response.message
        ?? 'Se houver uma conta elegível, enviaremos instruções ao canal seguro.',
      ));
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setLoading(false);
    }
  };

  if (mode === 'welcome') {
    return <main className='valley-entry'>
      <section className='valley-entry-shell'>
        <img
          className='valley-entry-logo'
          src='/assets/brand/valley-logo-official.png'
          alt='VALLEY'
        />
        <div className='valley-entry-actions'>
          <button
            className='primary'
            type='button'
            onClick={() => setMode('login')}
          >
            Entrar
          </button>
          <button
            className='secondary'
            type='button'
            onClick={() => setMode('register')}
          >
            Cadastrar
          </button>
        </div>
        {notice && <div className='notice warning'>{notice}</div>}
      </section>
    </main>;
  }

  return <main className='valley-entry'>
    <section className='auth-flow-card'>
      <button
        className='auth-back'
        type='button'
        onClick={() => {
          setMode('welcome');
          setError('');
        }}
      >
        ‹ Voltar
      </button>
      <img
        className='auth-logo'
        src='/assets/brand/valley-logo-official.png'
        alt='VALLEY'
      />
      <h1>{mode === 'login' ? 'Entrar' : 'Cadastrar'}</h1>
      <p>
        {mode === 'login'
          ? 'Use seu CPF e sua senha.'
          : 'Crie seu cadastro para acessar a Home do VALLEY.'}
      </p>
      <form onSubmit={mode === 'login' ? submitLogin : submitRegistration}>
        {mode === 'register' && <label>
          Nome completo
          <input
            value={fullName}
            onChange={event => setFullName(event.target.value)}
            autoComplete='name'
            required
          />
        </label>}
        <label>
          CPF
          <input
            inputMode='numeric'
            autoComplete='username'
            value={cpf}
            onChange={event => setCpf(formatCpf(event.target.value))}
            placeholder='000.000.000-00'
            required
          />
        </label>
        {mode === 'register' && <>
          <label>
            E-mail de contato
            <input
              type='email'
              value={contactEmail}
              onChange={event => setContactEmail(event.target.value)}
              autoComplete='email'
            />
          </label>
          <label>
            Telefone
            <input
              inputMode='tel'
              value={phone}
              onChange={event => setPhone(event.target.value)}
              autoComplete='tel'
            />
          </label>
          <ValleyAvatarPicker
            value={avatarDataUrl}
            onChange={setAvatarDataUrl}
            onError={setError}
          />
        </>}
        <label>
          Senha
          <input
            type='password'
            value={password}
            onChange={event => setPassword(event.target.value)}
            autoComplete={mode === 'login'
              ? 'current-password'
              : 'new-password'}
            minLength={6}
            required
          />
        </label>
        {mode === 'register' && <label className='checkbox-row'>
          <input
            type='checkbox'
            checked={accepted}
            onChange={event => setAccepted(event.target.checked)}
          />
          Aceito os termos e o tratamento necessário dos dados.
        </label>}
        {error && <div className='notice error'>{error}</div>}
        <button className='primary' type='submit' disabled={loading}>
          {loading
            ? 'Processando...'
            : mode === 'login'
              ? 'Entrar'
              : 'Cadastrar e entrar'}
        </button>
        {mode === 'login' && loginAttempts > 0 && <button
          className='text-button'
          type='button'
          onClick={requestRecovery}
          disabled={loading}
        >
          Recuperar acesso
        </button>}
      </form>
    </section>
  </main>;
}

function BottomNav({
  route,
  navigate,
}: {
  route: RouteState;
  navigate: (view: ViewKey, hint?: JourneyHint) => void;
}) {
  const items: Array<{
    key: ViewKey;
    label: string;
    icon: string;
    hint?: JourneyHint;
    active: ViewKey[];
  }> = [
    {
      key: 'home',
      label: 'Início',
      icon: '⌂',
      active: [
        'home',
        'delivery',
        'mobility',
        'life',
        'legal',
        'health',
        'property',
        'services',
      ],
    },
    {
      key: 'marketplace',
      label: 'Comprar',
      icon: '▦',
      hint: { intent: 'comprar', mode: 'feed' },
      active: ['marketplace', 'stock'],
    },
    {
      key: 'finance',
      label: 'Financeiro',
      icon: '◈',
      active: ['finance'],
    },
    {
      key: 'jobs',
      label: 'Trabalhar',
      icon: '✦',
      hint: { intent: 'trabalhar', mode: 'seek' },
      active: ['jobs'],
    },
    {
      key: 'account',
      label: 'Conta',
      icon: '●',
      active: ['account', 'settings'],
    },
  ];
  return <nav className='bottom-nav' aria-label='Navegação principal'>
    {items.map(item => <button
      key={item.key}
      type='button'
      className={item.active.includes(route.view) ? 'active' : ''}
      onClick={() => navigate(item.key, item.hint)}
    >
      <span>{item.icon}</span><small>{item.label}</small>
    </button>)}
  </nav>;
}

function authEmail(cpf: string) {
  return `${cpf}@cpf.valley.local`;
}

function validateCpf(cpf: string) {
  if (!/^\d{11}$/.test(cpf)) {
    throw new Error('Informe um CPF válido com 11 números.');
  }
}

function formatCpf(value: string) {
  const digits = value.replace(/\D/g, '').slice(0, 11);
  return digits
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
}

function normalizeBrazilPhone(value: string) {
  const digits = value.replace(/\D/g, '');
  if (!digits) return undefined;
  return digits.startsWith('55') ? `+${digits}` : `+55${digits}`;
}

export default App;
