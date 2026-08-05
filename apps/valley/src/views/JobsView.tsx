import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import {
  errorMessage,
  formatMoney,
  itemSubtitle,
  itemTitle,
  request,
  uploadPdf,
  type ApiItem,
  type JourneyHint,
  type ViewProps,
} from '../lib/api';
import { SectionHeader, StateCard } from '../ui';

type JobMode = 'seek' | 'offer' | 'recruit';
type SearchPreferences = {
  query: string;
  region: string;
  minSalary: string;
  employmentType: string;
};

const employmentOptions = [
  'CLT',
  'Temporário',
  'Autônomo',
  'Comissionado',
  'Estágio',
  'Aprendiz',
  'Freelance',
];

const emptyPreferences: SearchPreferences = {
  query: '',
  region: '',
  minSalary: '',
  employmentType: '',
};

function modeFromHint(hint?: JourneyHint): JobMode {
  if (hint?.mode === 'recruit') return 'recruit';
  if (hint?.mode === 'offer') return 'offer';
  return 'seek';
}

function preferenceKey(userId: string) {
  return `valley.jobs.preferences.${userId}`;
}

function asText(value: unknown) {
  return value == null ? '' : String(value);
}

function asList(value: unknown) {
  if (Array.isArray(value)) return value.map(String);
  if (typeof value !== 'string') return [];
  return value.split(',').map(item => item.trim()).filter(Boolean);
}

function extractItems(value: unknown): ApiItem[] {
  if (Array.isArray(value)) return value as ApiItem[];
  if (!value || typeof value !== 'object') return [];
  const record = value as Record<string, unknown>;
  for (const key of ['data', 'items', 'vacancies', 'results']) {
    if (Array.isArray(record[key])) return record[key] as ApiItem[];
  }
  return [];
}

function readSavedPreferences(userId: string): SearchPreferences {
  try {
    const raw = window.localStorage.getItem(preferenceKey(userId));
    if (!raw) return emptyPreferences;
    const parsed = JSON.parse(raw) as Partial<SearchPreferences>;
    return {
      query: parsed.query ?? '',
      region: parsed.region ?? '',
      minSalary: parsed.minSalary ?? '',
      employmentType: parsed.employmentType ?? '',
    };
  } catch {
    return emptyPreferences;
  }
}

function PinIcon() {
  return <svg viewBox='0 0 24 24' aria-hidden='true'>
    <path d='M9 3h6l-1 6 3 3v2h-4v7l-2-2v-5H7v-2l3-3-1-6Z' />
  </svg>;
}

export function JobsView({
  session,
  setNotice,
  hint,
}: ViewProps & { hint?: JourneyHint }) {
  const [mode, setMode] = useState<JobMode>(() => modeFromHint(hint));
  const [resumes, setResumes] = useState<ApiItem[]>([]);
  const [vacancies, setVacancies] = useState<ApiItem[]>([]);
  const [applications, setApplications] = useState<ApiItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingResume, setEditingResume] = useState(false);
  const [preferencesPinned, setPreferencesPinned] = useState(false);
  const [preferences, setPreferences] = useState<SearchPreferences>(() => (
    readSavedPreferences(session.userId)
  ));

  const [headline, setHeadline] = useState('');
  const [summary, setSummary] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [desiredTitles, setDesiredTitles] = useState('');
  const [desiredRegions, setDesiredRegions] = useState('');
  const [desiredTypes, setDesiredTypes] = useState<string[]>([]);
  const [minimumSalary, setMinimumSalary] = useState('');
  const [ctpsFile, setCtpsFile] = useState<File | null>(null);
  const [savingResume, setSavingResume] = useState(false);

  const [applicationVacancyId, setApplicationVacancyId] = useState('');
  const [applicationNote, setApplicationNote] = useState('');

  const [specialty, setSpecialty] = useState('');
  const [serviceDescription, setServiceDescription] = useState('');
  const [serviceRegion, setServiceRegion] = useState('');

  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobRegion, setJobRegion] = useState('');
  const [jobType, setJobType] = useState('CLT');
  const [jobSalary, setJobSalary] = useState('');

  const currentResume = resumes[0] ?? null;

  const hydrateResume = useCallback((resume: ApiItem | null) => {
    const payload = resume?.payload ?? {};
    setHeadline(asText(payload.headline ?? payload.title));
    setSummary(asText(payload.summary ?? payload.description));
    setCity(asText(payload.city));
    setState(asText(payload.state));
    setDesiredTitles(asList(payload.desired_titles).join(', '));
    setDesiredRegions(asList(payload.desired_regions).join(', '));
    setDesiredTypes(asList(payload.employment_types));
    setMinimumSalary(asText(payload.minimum_salary_brl));

    const saved = payload.job_search_preferences;
    if (saved && typeof saved === 'object') {
      const record = saved as Record<string, unknown>;
      setPreferences({
        query: asText(record.query),
        region: asText(record.region),
        minSalary: asText(record.min_salary_brl),
        employmentType: asText(record.employment_type),
      });
      setPreferencesPinned(Boolean(record.pinned));
    }
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        request<ApiItem[]>('/jobs/resources/resumes', 'GET', undefined, session.accessToken),
        request<ApiItem[]>('/jobs/resources/applications', 'GET', undefined, session.accessToken),
        request<unknown>('/jobs/vacancies', 'GET', undefined, session.accessToken),
        request<ApiItem[]>('/jobs/resources/job_postings', 'GET', undefined, session.accessToken),
      ]);
      const nextResumes = results[0].status === 'fulfilled'
        ? extractItems(results[0].value)
        : [];
      const nextApplications = results[1].status === 'fulfilled'
        ? extractItems(results[1].value)
        : [];
      const publicVacancies = results[2].status === 'fulfilled'
        ? extractItems(results[2].value)
        : [];
      const resourceVacancies = results[3].status === 'fulfilled'
        ? extractItems(results[3].value)
        : [];
      const uniqueVacancies = new Map<string, ApiItem>();
      for (const vacancy of [...publicVacancies, ...resourceVacancies]) {
        uniqueVacancies.set(vacancy.id, vacancy);
      }
      setResumes(nextResumes);
      setApplications(nextApplications);
      setVacancies([...uniqueVacancies.values()]);
      hydrateResume(nextResumes[0] ?? null);
    } catch (err) {
      setNotice(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [hydrateResume, session.accessToken, setNotice]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void load(); }, 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const filteredVacancies = useMemo(() => {
    const query = preferences.query.trim().toLocaleLowerCase('pt-BR');
    const region = preferences.region.trim().toLocaleLowerCase('pt-BR');
    const minimum = Number(
      preferences.minSalary.replace(/[^0-9.,]/g, '').replace(',', '.'),
    ) || 0;
    const expectedType = preferences.employmentType.toLocaleLowerCase('pt-BR');

    return vacancies.filter(vacancy => {
      const payload = vacancy.payload ?? {};
      const haystack = (
        `${itemTitle(vacancy)} ${itemSubtitle(vacancy)} ${JSON.stringify(payload)}`
      ).toLocaleLowerCase('pt-BR');
      const vacancyRegion = asText(
        payload.region ?? payload.location ?? payload.city,
      ).toLocaleLowerCase('pt-BR');
      const vacancyType = asText(
        payload.employment_type ?? payload.contract_type ?? payload.type,
      ).toLocaleLowerCase('pt-BR');
      const salary = Number(
        asText(
          payload.salary_amount ?? payload.salary_brl ?? payload.remuneration,
        ).replace(/[^0-9.,]/g, '').replace(',', '.'),
      ) || 0;

      if (query && !haystack.includes(query)) return false;
      if (region && !vacancyRegion.includes(region) && !haystack.includes(region)) {
        return false;
      }
      if (expectedType && !vacancyType.includes(expectedType)) return false;
      if (minimum && salary && salary < minimum) return false;
      return true;
    });
  }, [preferences, vacancies]);

  function resumePayload(pinned = preferencesPinned) {
    return {
      headline,
      summary,
      city,
      state,
      desired_titles: desiredTitles
        .split(',')
        .map(item => item.trim())
        .filter(Boolean),
      desired_regions: desiredRegions
        .split(',')
        .map(item => item.trim())
        .filter(Boolean),
      employment_types: desiredTypes,
      minimum_salary_brl: minimumSalary || null,
      visibility: 'business_recruiters',
      job_search_preferences: {
        query: preferences.query,
        region: preferences.region,
        min_salary_brl: preferences.minSalary,
        employment_type: preferences.employmentType,
        pinned,
      },
    };
  }

  const saveResume = async (event: FormEvent) => {
    event.preventDefault();
    setSavingResume(true);
    try {
      let resumeId = currentResume?.id;
      if (currentResume) {
        await request(`/jobs/resources/resumes/${currentResume.id}`, 'PATCH', {
          payload: resumePayload(),
        }, session.accessToken);
      } else {
        const created = await request<ApiItem>('/jobs/resources/resumes', 'POST', {
          user_id: session.userId,
          status: 'active',
          payload: resumePayload(),
        }, session.accessToken);
        resumeId = created.id;
      }

      if (resumeId && ctpsFile) {
        await uploadPdf(
          `/jobs/resumes/${resumeId}/imports/ctps-digital`,
          ctpsFile,
          session.accessToken,
        );
        setCtpsFile(null);
      }

      setEditingResume(false);
      setNotice(
        currentResume
          ? 'Currículo atualizado.'
          : 'Currículo cadastrado. O feed de vagas foi liberado.',
      );
      await load();
    } catch (err) {
      setNotice(errorMessage(err));
    } finally {
      setSavingResume(false);
    }
  };

  const togglePinnedPreferences = async () => {
    const nextPinned = !preferencesPinned;
    setPreferencesPinned(nextPinned);
    window.localStorage.setItem(
      preferenceKey(session.userId),
      JSON.stringify(preferences),
    );

    if (!currentResume) return;
    try {
      await request(`/jobs/resources/resumes/${currentResume.id}`, 'PATCH', {
        payload: {
          ...currentResume.payload,
          ...resumePayload(nextPinned),
        },
      }, session.accessToken);
      setNotice(
        nextPinned
          ? 'Interesses fixados para priorizar vagas.'
          : 'Interesses desafixados.',
      );
    } catch (err) {
      setNotice(errorMessage(err));
    }
  };

  const apply = async (vacancy: ApiItem) => {
    try {
      await request('/jobs/resources/applications', 'POST', {
        user_id: session.userId,
        status: 'REQUESTED',
        payload: {
          vacancy_id: vacancy.id,
          resume_id: currentResume?.id,
          note: applicationNote || null,
        },
      }, session.accessToken);
      setApplicationVacancyId('');
      setApplicationNote('');
      setNotice('Candidatura enviada.');
      await load();
    } catch (err) {
      setNotice(errorMessage(err));
    }
  };

  const offerWork = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/services/resources/providers', 'POST', {
        user_id: session.userId,
        status: 'pending_review',
        payload: {
          specialty,
          description: serviceDescription,
          service_region: serviceRegion,
          source: 'valley_offer_work',
        },
      }, session.accessToken);
      setSpecialty('');
      setServiceDescription('');
      setServiceRegion('');
      setNotice('Cadastro profissional enviado para análise.');
    } catch (err) {
      setNotice(errorMessage(err));
    }
  };

  const recruit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/jobs/resources/job_postings', 'POST', {
        user_id: session.userId,
        status: 'draft',
        payload: {
          title: jobTitle,
          description: jobDescription,
          region: jobRegion,
          employment_type: jobType,
          salary_amount: jobSalary || null,
        },
      }, session.accessToken);
      setJobTitle('');
      setJobDescription('');
      setJobRegion('');
      setJobSalary('');
      setNotice('Vaga cadastrada para análise e publicação.');
      await load();
    } catch (err) {
      setNotice(errorMessage(err));
    }
  };

  const renderResumeForm = () => <form
    className='form-card resume-form'
    onSubmit={saveResume}
  >
    <div className='inline-heading'>
      <h2>{currentResume ? 'Editar currículo' : 'Cadastre seu currículo'}</h2>
      {currentResume && <button
        className='text-button'
        type='button'
        onClick={() => setEditingResume(false)}
      >Cancelar</button>}
    </div>
    <p>
      Seu currículo organiza o feed de vagas e pode ser pesquisado por
      recrutadores autorizados.
    </p>
    <label>Título profissional
      <input
        value={headline}
        onChange={event => setHeadline(event.target.value)}
        placeholder='Ex.: Motorista, Desenvolvedor, Auxiliar Administrativo'
        required
      />
    </label>
    <label>Resumo profissional
      <textarea
        value={summary}
        onChange={event => setSummary(event.target.value)}
        placeholder='Experiência, habilidades e objetivos'
        required
      />
    </label>
    <div className='field-pair'>
      <label>Cidade
        <input value={city} onChange={event => setCity(event.target.value)} required />
      </label>
      <label>Estado
        <input
          value={state}
          onChange={event => setState(event.target.value.toUpperCase())}
          maxLength={2}
          required
        />
      </label>
    </div>
    <label>Cargos de interesse
      <input
        value={desiredTitles}
        onChange={event => setDesiredTitles(event.target.value)}
        placeholder='Separe por vírgulas'
      />
    </label>
    <label>Regiões de interesse
      <input
        value={desiredRegions}
        onChange={event => setDesiredRegions(event.target.value)}
        placeholder='Separe por vírgulas'
      />
    </label>
    <fieldset className='choice-field'>
      <legend>Tipos de trabalho</legend>
      <div className='choice-grid'>
        {employmentOptions.map(option => <label
          key={option}
          className='checkbox-row'
        >
          <input
            type='checkbox'
            checked={desiredTypes.includes(option)}
            onChange={event => setDesiredTypes(current => (
              event.target.checked
                ? [...current, option]
                : current.filter(item => item !== option)
            ))}
          />
          {option}
        </label>)}
      </div>
    </fieldset>
    <label>Remuneração mínima desejada
      <input
        inputMode='decimal'
        value={minimumSalary}
        onChange={event => setMinimumSalary(event.target.value)}
        placeholder='R$'
      />
    </label>
    <div className='ctps-import'>
      <label>Importar PDF da Carteira de Trabalho Digital
        <input
          type='file'
          accept='application/pdf,.pdf'
          onChange={event => setCtpsFile(event.target.files?.[0] ?? null)}
        />
      </label>
      <small>
        O PDF fica protegido e não é entregue aos recrutadores. Somente
        informações de procedência autorizadas são exibidas.
      </small>
    </div>
    <button className='primary' type='submit' disabled={savingResume}>
      {savingResume
        ? 'Salvando...'
        : currentResume
          ? 'Salvar currículo'
          : 'Cadastrar currículo'}
    </button>
  </form>;

  return <section className='jobs-screen'>
    <SectionHeader
      title={
        mode === 'seek'
          ? 'Buscar emprego'
          : mode === 'offer'
            ? 'Oferecer trabalho'
            : 'Contratar para uma vaga'
      }
      subtitle={
        mode === 'seek'
          ? 'Currículo, filtros de interesse e feed de oportunidades.'
          : mode === 'offer'
            ? 'Cadastre-se como prestador especializado em uma área.'
            : 'Publique uma oportunidade e acompanhe candidatos.'
      }
      actionLabel='Atualizar'
      onAction={load}
    />

    <div className='segmented intent-segmented'>
      <button
        type='button'
        className={mode === 'seek' ? 'active' : ''}
        onClick={() => setMode('seek')}
      >Buscar emprego</button>
      <button
        type='button'
        className={mode === 'offer' ? 'active' : ''}
        onClick={() => setMode('offer')}
      >Oferecer trabalho</button>
      <button
        type='button'
        className={mode === 'recruit' ? 'active' : ''}
        onClick={() => setMode('recruit')}
      >Contratar</button>
    </div>

    {loading && <StateCard text='Sincronizando currículo e oportunidades...' />}

    {!loading && mode === 'seek' && !currentResume && renderResumeForm()}

    {!loading && mode === 'seek' && currentResume && <>
      <div className='jobs-toolbar'>
        <div>
          <strong>{headline || 'Meu currículo'}</strong>
          <span>{city}{city && state ? ', ' : ''}{state}</span>
        </div>
        <button
          className='secondary edit-resume-button'
          type='button'
          onClick={() => setEditingResume(true)}
        >Editar currículo</button>
      </div>

      {editingResume && renderResumeForm()}

      <div className='jobs-layout'>
        <aside className={`job-filter-rail ${preferencesPinned ? 'pinned' : ''}`}>
          <button
            type='button'
            className='pin-filter'
            aria-pressed={preferencesPinned}
            onClick={() => { void togglePinnedPreferences(); }}
          >
            <PinIcon />
            {preferencesPinned ? 'Interesses fixados' : 'Fixar interesses'}
          </button>
          <label>Título da vaga
            <input
              type='search'
              value={preferences.query}
              onChange={event => setPreferences(current => ({
                ...current,
                query: event.target.value,
              }))}
              placeholder='Cargo ou palavra-chave'
            />
          </label>
          <label>Região
            <input
              value={preferences.region}
              onChange={event => setPreferences(current => ({
                ...current,
                region: event.target.value,
              }))}
              placeholder='Cidade, estado ou remoto'
            />
          </label>
          <label>Remuneração mínima
            <input
              inputMode='decimal'
              value={preferences.minSalary}
              onChange={event => setPreferences(current => ({
                ...current,
                minSalary: event.target.value,
              }))}
              placeholder='R$'
            />
          </label>
          <label>Tipo de vaga
            <select
              value={preferences.employmentType}
              onChange={event => setPreferences(current => ({
                ...current,
                employmentType: event.target.value,
              }))}
            >
              <option value=''>Todos</option>
              {employmentOptions.map(option => <option key={option} value={option}>
                {option}
              </option>)}
            </select>
          </label>
          <button
            className='text-button'
            type='button'
            onClick={() => setPreferences(emptyPreferences)}
          >Limpar filtros</button>
        </aside>

        <div className='job-feed'>
          <div className='feed-heading'>
            <h2>Vagas para você</h2>
            <span>{filteredVacancies.length} oportunidade(s)</span>
          </div>
          {!filteredVacancies.length && (
            <StateCard text='Nenhuma vaga encontrada com estes filtros.' />
          )}
          {filteredVacancies.map(vacancy => {
            const payload = vacancy.payload ?? {};
            const salaryValue = (
              payload.salary_amount ?? payload.salary_brl ?? payload.remuneration
            );
            const salary = salaryValue == null
              ? 'Remuneração a combinar'
              : formatMoney(String(salaryValue));
            const applying = applicationVacancyId === vacancy.id;
            return <article className='job-card' key={vacancy.id}>
              <div className='job-card-main'>
                <span className='eyebrow'>
                  {asText(payload.employment_type ?? payload.contract_type ?? 'Vaga')}
                </span>
                <h3>{itemTitle(vacancy)}</h3>
                <p>{itemSubtitle(vacancy)}</p>
                <div className='job-meta'>
                  <span>{asText(
                    payload.company_name ?? payload.company ?? 'Empresa verificada',
                  )}</span>
                  <span>{asText(
                    payload.region ?? payload.location ?? 'Região não informada',
                  )}</span>
                  <strong>{salary}</strong>
                </div>
              </div>
              {!applying
                ? <button
                    className='primary'
                    type='button'
                    onClick={() => setApplicationVacancyId(vacancy.id)}
                  >Candidatar-se</button>
                : <div className='application-composer'>
                    <label>Mensagem opcional
                      <textarea
                        value={applicationNote}
                        onChange={event => setApplicationNote(event.target.value)}
                      />
                    </label>
                    <div className='button-row'>
                      <button
                        className='secondary'
                        type='button'
                        onClick={() => setApplicationVacancyId('')}
                      >Cancelar</button>
                      <button
                        className='primary'
                        type='button'
                        onClick={() => { void apply(vacancy); }}
                      >Enviar candidatura</button>
                    </div>
                  </div>}
            </article>;
          })}
        </div>
      </div>

      {applications.length > 0 && <div className='resource-section'>
        <h2>Minhas candidaturas</h2>
        <div className='card-list compact'>
          {applications.map(application => <article
            className='data-card'
            key={application.id}
          >
            <div>
              <span className='eyebrow'>{application.status ?? 'enviada'}</span>
              <h3>{itemTitle(application)}</h3>
              <p>{itemSubtitle(application)}</p>
            </div>
          </article>)}
        </div>
      </div>}
    </>}

    {!loading && mode === 'offer' && <form className='form-card' onSubmit={offerWork}>
      <h2>Ofereça seu trabalho</h2>
      <label>Área ou especialidade
        <input
          value={specialty}
          onChange={event => setSpecialty(event.target.value)}
          placeholder='Ex.: eletricista, cuidador, designer'
          required
        />
      </label>
      <label>Experiência e serviços oferecidos
        <textarea
          value={serviceDescription}
          onChange={event => setServiceDescription(event.target.value)}
          required
        />
      </label>
      <label>Região de atendimento
        <input
          value={serviceRegion}
          onChange={event => setServiceRegion(event.target.value)}
          required
        />
      </label>
      <button className='primary' type='submit'>Cadastrar como prestador</button>
    </form>}

    {!loading && mode === 'recruit' && <form className='form-card' onSubmit={recruit}>
      <h2>Publicar oportunidade</h2>
      <label>Título da vaga
        <input
          value={jobTitle}
          onChange={event => setJobTitle(event.target.value)}
          required
        />
      </label>
      <label>Descrição
        <textarea
          value={jobDescription}
          onChange={event => setJobDescription(event.target.value)}
          required
        />
      </label>
      <div className='field-pair'>
        <label>Região
          <input
            value={jobRegion}
            onChange={event => setJobRegion(event.target.value)}
            required
          />
        </label>
        <label>Tipo de vaga
          <select value={jobType} onChange={event => setJobType(event.target.value)}>
            {employmentOptions.map(option => <option key={option} value={option}>
              {option}
            </option>)}
          </select>
        </label>
      </div>
      <label>Remuneração
        <input
          inputMode='decimal'
          value={jobSalary}
          onChange={event => setJobSalary(event.target.value)}
          placeholder='R$ ou deixe em branco para combinar'
        />
      </label>
      <button className='primary' type='submit'>Cadastrar vaga</button>
    </form>}
  </section>;
}
