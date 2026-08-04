import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { errorMessage, itemSubtitle, itemTitle, request, uploadPdf, type ApiItem, type JourneyHint, type ViewProps } from '../lib/api';
import { ResourceSummary, SectionHeader, StateCard } from '../ui';

type Mode = 'seek' | 'offer' | 'recruit';
type JobFilters = { title: string; region: string; minPay: string; maxPay: string; contractType: string; pinned: boolean };
const EMPTY_FILTERS: JobFilters = { title:'', region:'', minPay:'', maxPay:'', contractType:'', pinned:false };

export function JobsExperience({ session, setNotice, hint }: ViewProps & { hint?: JourneyHint }) {
  const [mode, setMode] = useState<Mode>(hint?.mode === 'offer' ? 'offer' : hint?.mode === 'recruit' ? 'recruit' : 'seek');
  const [resumes, setResumes] = useState<ApiItem[]>([]);
  const [vacancies, setVacancies] = useState<ApiItem[]>([]);
  const [applications, setApplications] = useState<ApiItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingResume, setEditingResume] = useState(false);
  const [resumeTitle, setResumeTitle] = useState('');
  const [resumeSummary, setResumeSummary] = useState('');
  const [resumeRegion, setResumeRegion] = useState('');
  const [ctpsPdf, setCtpsPdf] = useState<File | null>(null);
  const [filters, setFilters] = useState<JobFilters>(EMPTY_FILTERS);
  const [applicationNote, setApplicationNote] = useState('');
  const [selectedVacancy, setSelectedVacancy] = useState<ApiItem | null>(null);
  const [professionalArea, setProfessionalArea] = useState('');
  const [professionalDescription, setProfessionalDescription] = useState('');
  const [professionalRegion, setProfessionalRegion] = useState('');
  const [vacancyTitle, setVacancyTitle] = useState('');
  const [vacancyDescription, setVacancyDescription] = useState('');
  const [vacancyRegion, setVacancyRegion] = useState('');
  const [vacancyContract, setVacancyContract] = useState('CLT');
  const [vacancyPay, setVacancyPay] = useState('');

  const resume = resumes[0] ?? null;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [resumeData, vacancyData, applicationData] = await Promise.all([
        request<ApiItem[]>('/jobs/resources/resumes', 'GET', undefined, session.accessToken),
        request<ApiItem[]>('/jobs/vacancies', 'GET', undefined, session.accessToken),
        request<ApiItem[]>('/jobs/resources/applications', 'GET', undefined, session.accessToken),
      ]);
      setResumes(resumeData ?? []); setVacancies(vacancyData ?? []); setApplications(applicationData ?? []);
      const current = resumeData?.[0]?.payload;
      if (current) {
        setResumeTitle(String(current.title ?? current.professional_title ?? ''));
        setResumeSummary(String(current.summary ?? current.objective ?? ''));
        setResumeRegion(String(current.region ?? ''));
        const saved = current.valley_job_filters as Record<string, unknown> | undefined;
        if (saved) setFilters({ title:String(saved.title ?? ''), region:String(saved.region ?? ''), minPay:String(saved.minPay ?? ''), maxPay:String(saved.maxPay ?? ''), contractType:String(saved.contractType ?? ''), pinned:Boolean(saved.pinned) });
      }
    } catch (error) { setNotice(errorMessage(error)); }
    finally { setLoading(false); }
  }, [session.accessToken, setNotice]);

  useEffect(() => { void load(); }, [load]);
  useEffect(() => { setMode(hint?.mode === 'offer' ? 'offer' : hint?.mode === 'recruit' ? 'recruit' : 'seek'); }, [hint?.mode]);

  const filteredVacancies = useMemo(() => vacancies.filter(vacancy => {
    const payload = vacancy.payload ?? {};
    const haystack = `${itemTitle(vacancy)} ${itemSubtitle(vacancy)} ${JSON.stringify(payload)}`.toLocaleLowerCase('pt-BR');
    if (filters.title && !haystack.includes(filters.title.toLocaleLowerCase('pt-BR'))) return false;
    if (filters.region && !String(payload.region ?? payload.location ?? '').toLocaleLowerCase('pt-BR').includes(filters.region.toLocaleLowerCase('pt-BR'))) return false;
    if (filters.contractType && String(payload.contract_type ?? payload.employment_type ?? '').toLocaleLowerCase('pt-BR') !== filters.contractType.toLocaleLowerCase('pt-BR')) return false;
    const pay = Number(payload.remuneration_brl ?? payload.salary_brl ?? payload.max_salary_brl ?? 0);
    if (filters.minPay && pay && pay < Number(filters.minPay)) return false;
    if (filters.maxPay && pay && pay > Number(filters.maxPay)) return false;
    return true;
  }), [filters, vacancies]);

  const saveResume = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const payload = { title:resumeTitle, summary:resumeSummary, region:resumeRegion, visibility:'business_recruiters', valley_job_filters:filters };
      let current = resume;
      if (current) await request(`/jobs/resources/resumes/${current.id}`, 'PATCH', { payload }, session.accessToken);
      else current = await request<ApiItem>('/jobs/resources/resumes', 'POST', { user_id:session.userId, status:'active', payload }, session.accessToken);
      if (ctpsPdf && current?.id) await uploadPdf(`/jobs/resumes/${current.id}/imports/ctps-digital`, ctpsPdf, session.accessToken);
      setCtpsPdf(null); setEditingResume(false); setNotice(resume ? 'Currículo atualizado.' : 'Currículo cadastrado.'); await load();
    } catch (error) { setNotice(errorMessage(error)); }
  };

  const savePinnedFilters = async () => {
    if (!resume) return;
    const next = { ...filters, pinned:!filters.pinned };
    setFilters(next);
    try {
      await request(`/jobs/resources/resumes/${resume.id}`, 'PATCH', { payload:{ ...resume.payload, valley_job_filters:next } }, session.accessToken);
      setNotice(next.pinned ? 'Filtro de vagas fixado no seu currículo.' : 'Filtro automático removido.');
    } catch (error) { setFilters(filters); setNotice(errorMessage(error)); }
  };

  const apply = async () => {
    if (!selectedVacancy) return;
    try {
      await request('/jobs/resources/applications', 'POST', { user_id:session.userId, status:'submitted', payload:{ vacancy_id:selectedVacancy.id, resume_id:resume?.id, note:applicationNote } }, session.accessToken);
      setSelectedVacancy(null); setApplicationNote(''); setNotice('Candidatura enviada.'); await load();
    } catch (error) { setNotice(errorMessage(error)); }
  };

  const offerWork = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/services/resources/providers', 'POST', { user_id:session.userId, status:'REQUESTED', payload:{ professional_area:professionalArea, description:professionalDescription, service_region:professionalRegion, source:'valley_offer_work' } }, session.accessToken);
      setProfessionalArea(''); setProfessionalDescription(''); setProfessionalRegion(''); setNotice('Seu cadastro profissional foi enviado para análise.');
    } catch (error) { setNotice(errorMessage(error)); }
  };

  const recruit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await request('/jobs/resources/job_postings', 'POST', { user_id:session.userId, status:'draft', payload:{ title:vacancyTitle, description:vacancyDescription, region:vacancyRegion, contract_type:vacancyContract, remuneration_brl:vacancyPay || null } }, session.accessToken);
      setVacancyTitle(''); setVacancyDescription(''); setVacancyRegion(''); setVacancyPay(''); setNotice('Oportunidade cadastrada para revisão.'); await load();
    } catch (error) { setNotice(errorMessage(error)); }
  };

  if (loading) return <StateCard text='Preparando sua área de trabalho...' />;

  return <section className='jobs-experience'>
    <SectionHeader title='Trabalhar' subtitle='Busque emprego, ofereça seu trabalho ou contrate uma pessoa.' actionLabel='Atualizar' onAction={load} />
    <div className='segmented intent-segmented'><button type='button' className={mode==='seek'?'active':''} onClick={() => setMode('seek')}>Buscar emprego</button><button type='button' className={mode==='offer'?'active':''} onClick={() => setMode('offer')}>Oferecer trabalho</button><button type='button' className={mode==='recruit'?'active':''} onClick={() => setMode('recruit')}>Contratar</button></div>
    {mode === 'seek' && (!resume || editingResume) && <ResumeForm resumeExists={Boolean(resume)} title={resumeTitle} setTitle={setResumeTitle} summary={resumeSummary} setSummary={setResumeSummary} region={resumeRegion} setRegion={setResumeRegion} file={ctpsPdf} setFile={setCtpsPdf} onSubmit={saveResume} onCancel={resume ? () => setEditingResume(false) : undefined} />}
    {mode === 'seek' && resume && !editingResume && <div className='jobs-layout'>
      <aside className='job-filters'><div className='job-filter-heading'><h2>Filtrar vagas</h2><button type='button' className={filters.pinned?'pin-button active':'pin-button'} onClick={savePinnedFilters} aria-label='Fixar filtros de interesse'>⌖</button></div><label>Título da vaga<input type='search' value={filters.title} onChange={event => setFilters(current => ({...current,title:event.target.value}))} /></label><label>Região<input value={filters.region} onChange={event => setFilters(current => ({...current,region:event.target.value}))} /></label><div className='salary-filter'><label>Remuneração mínima<input type='number' value={filters.minPay} onChange={event => setFilters(current => ({...current,minPay:event.target.value}))} /></label><label>Máxima<input type='number' value={filters.maxPay} onChange={event => setFilters(current => ({...current,maxPay:event.target.value}))} /></label></div><label>Tipo de vaga<select value={filters.contractType} onChange={event => setFilters(current => ({...current,contractType:event.target.value}))}><option value=''>Todos</option><option>CLT</option><option>Temporário</option><option>Autônomo</option><option>Comissionado</option><option>Estágio</option><option>Aprendiz</option></select></label></aside>
      <div className='job-feed'><div className='job-feed-toolbar'><div><strong>{filteredVacancies.length}</strong><span> vagas encontradas</span></div><button className='secondary' type='button' onClick={() => setEditingResume(true)}>Editar currículo</button></div>{!filteredVacancies.length && <StateCard text='Nenhuma vaga encontrada com estes filtros.' />}{filteredVacancies.map(vacancy => <article className='job-card' key={vacancy.id}><span className='eyebrow'>{String(vacancy.payload?.contract_type ?? vacancy.payload?.employment_type ?? 'Oportunidade')}</span><h2>{itemTitle(vacancy)}</h2><p>{itemSubtitle(vacancy)}</p><small>{String(vacancy.payload?.region ?? vacancy.payload?.location ?? 'Região não informada')}</small><strong>{formatPay(vacancy.payload)}</strong><button className='primary' type='button' onClick={() => setSelectedVacancy(vacancy)}>Candidatar-se</button></article>)}</div>
    </div>}
    {mode === 'offer' && <form className='form-card' onSubmit={offerWork}><h2>Oferecer trabalho</h2><p>Cadastre-se como profissional ou prestador especializado.</p><label>Área de atuação<input value={professionalArea} onChange={event => setProfessionalArea(event.target.value)} required /></label><label>Experiência e serviços<textarea value={professionalDescription} onChange={event => setProfessionalDescription(event.target.value)} required /></label><label>Região de atendimento<input value={professionalRegion} onChange={event => setProfessionalRegion(event.target.value)} required /></label><button className='primary' type='submit'>Enviar cadastro profissional</button></form>}
    {mode === 'recruit' && <form className='form-card' onSubmit={recruit}><h2>Cadastrar oportunidade</h2><label>Título da vaga<input value={vacancyTitle} onChange={event => setVacancyTitle(event.target.value)} required /></label><label>Descrição<textarea value={vacancyDescription} onChange={event => setVacancyDescription(event.target.value)} required /></label><label>Região<input value={vacancyRegion} onChange={event => setVacancyRegion(event.target.value)} required /></label><label>Tipo de contratação<select value={vacancyContract} onChange={event => setVacancyContract(event.target.value)}><option>CLT</option><option>Temporário</option><option>Autônomo</option><option>Comissionado</option><option>Estágio</option><option>Aprendiz</option></select></label><label>Remuneração<input type='number' value={vacancyPay} onChange={event => setVacancyPay(event.target.value)} /></label><button className='primary' type='submit'>Cadastrar oportunidade</button></form>}
    {mode === 'seek' && <ResourceSummary title='Minhas candidaturas' items={applications} />}
    {selectedVacancy && <div className='modal-backdrop'><section className='modal' role='dialog' aria-modal='true'><header><h2>{itemTitle(selectedVacancy)}</h2><button type='button' onClick={() => setSelectedVacancy(null)}>×</button></header><p>{itemSubtitle(selectedVacancy)}</p><label>Mensagem para a empresa<textarea value={applicationNote} onChange={event => setApplicationNote(event.target.value)} /></label><button className='primary' type='button' onClick={apply}>Enviar candidatura</button></section></div>}
  </section>;
}

function ResumeForm({ resumeExists, title, setTitle, summary, setSummary, region, setRegion, file, setFile, onSubmit, onCancel }: { resumeExists:boolean; title:string; setTitle:(value:string)=>void; summary:string; setSummary:(value:string)=>void; region:string; setRegion:(value:string)=>void; file:File|null; setFile:(value:File|null)=>void; onSubmit:(event:FormEvent)=>void; onCancel?:()=>void }) {
  return <form className='form-card resume-first' onSubmit={onSubmit}><h2>{resumeExists?'Editar currículo':'Cadastre seu currículo'}</h2><p>{resumeExists?'Atualize seus dados e preferências.':'Seu currículo vem antes do feed de vagas. Você também pode importar o PDF da Carteira de Trabalho Digital.'}</p><label>Título profissional<input value={title} onChange={event => setTitle(event.target.value)} placeholder='Ex.: motorista, desenvolvedor, atendente' required /></label><label>Resumo profissional<textarea value={summary} onChange={event => setSummary(event.target.value)} required /></label><label>Região<input value={region} onChange={event => setRegion(event.target.value)} required /></label><label>Importar Carteira de Trabalho Digital em PDF<input type='file' accept='application/pdf' onChange={event => setFile(event.target.files?.[0] ?? null)} /></label>{file && <small>Arquivo selecionado: {file.name}</small>}<div className='button-row'>{onCancel && <button className='secondary' type='button' onClick={onCancel}>Cancelar</button>}<button className='primary' type='submit'>{resumeExists?'Salvar currículo':'Cadastrar currículo'}</button></div></form>;
}

function formatPay(payload?: Record<string, unknown>) {
  const value = Number(payload?.remuneration_brl ?? payload?.salary_brl ?? 0);
  return value ? value.toLocaleString('pt-BR',{style:'currency',currency:'BRL'}) : 'Remuneração a combinar';
}
