import { type ChangeEvent, useEffect, useState } from 'react';
import { readValleyProfileBrand, saveValleyProfileBrand, ValleyProfileMark, type ValleyProfileMode } from '../brand';
import { errorMessage, request, type ViewProps } from '../lib/api';

const MAX_SOURCE_BYTES = 5 * 1024 * 1024;
const MAX_SAVED_BYTES = 650 * 1024;

export function ProfileBrandSettings({ session, setNotice }: ViewProps) {
  const [mode, setMode] = useState<ValleyProfileMode>('official');
  const [photoDataUrl, setPhotoDataUrl] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const current = readValleyProfileBrand();
    setMode(current.mode);
    setPhotoDataUrl(current.photoDataUrl);
  }, []);

  const choosePhoto = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setNotice('Escolha uma foto JPG, PNG ou WEBP.');
      return;
    }
    if (file.size > MAX_SOURCE_BYTES) {
      setNotice('A foto original deve ter no máximo 5 MB.');
      return;
    }
    try {
      const compressed = await compressProfilePhoto(file);
      setPhotoDataUrl(compressed);
      setMode('personalized');
      setNotice('Foto preparada. Salve para aplicar ao perfil.');
    } catch (error) {
      setNotice(errorMessage(error));
    }
  };

  const save = async () => {
    setSaving(true);
    try {
      const effectiveMode: ValleyProfileMode = mode === 'personalized' && photoDataUrl ? 'personalized' : 'official';
      saveValleyProfileBrand({ mode: effectiveMode, photoDataUrl: effectiveMode === 'personalized' ? photoDataUrl : '' });
      await request(`/identity/resources/users/${session.userId}`, 'PATCH', {
        payload: {
          valley_profile_brand_mode: effectiveMode,
          valley_profile_brand_scope: 'profile_only',
          valley_launcher_icon_policy: 'official_immutable',
        },
      }, session.accessToken);
      setMode(effectiveMode);
      setNotice(effectiveMode === 'personalized' ? 'Identidade personalizada aplicada somente ao seu perfil.' : 'Identidade oficial VALLEY restaurada no perfil.');
    } catch (error) {
      setNotice(errorMessage(error));
    } finally {
      setSaving(false);
    }
  };

  const restoreOfficial = () => {
    setMode('official');
    setPhotoDataUrl('');
  };

  return <section className='profile-brand-card'>
    <div className='profile-brand-preview'>
      <ValleyProfileMark mode={mode} photoDataUrl={photoDataUrl} className='profile-brand-large' />
    </div>
    <div className='profile-brand-copy'>
      <h2>Identidade visual do perfil</h2>
      <p>A marca oficial VALLEY continua no aplicativo e no ícone instalado. Aqui você pode, opcionalmente, usar sua foto dentro do aro com “VALLEY” abaixo.</p>
      <div className='profile-brand-options' role='radiogroup' aria-label='Identidade visual do perfil'>
        <label><input type='radio' name='profile-brand-mode' checked={mode === 'official'} onChange={() => setMode('official')} />Usar a marca oficial</label>
        <label><input type='radio' name='profile-brand-mode' checked={mode === 'personalized'} disabled={!photoDataUrl} onChange={() => setMode('personalized')} />Usar minha foto no aro</label>
      </div>
      <div className='button-row'>
        <label className='secondary file-button'>Escolher foto<input type='file' accept='image/jpeg,image/png,image/webp' onChange={choosePhoto} /></label>
        <button className='secondary' type='button' onClick={restoreOfficial}>Restaurar oficial</button>
        <button className='primary' type='button' onClick={save} disabled={saving}>{saving ? 'Salvando...' : 'Salvar no perfil'}</button>
      </div>
      <small className='profile-brand-note'>Esta personalização não altera o ícone do APK, a tela de abertura, a marca institucional nem a identidade de outros usuários.</small>
    </div>
  </section>;
}

async function compressProfilePhoto(file: File): Promise<string> {
  const source = await readFileAsDataUrl(file);
  const image = await loadImage(source);
  const dimension = Math.min(512, Math.max(image.naturalWidth, image.naturalHeight));
  const canvas = document.createElement('canvas');
  canvas.width = dimension;
  canvas.height = dimension;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('Não foi possível preparar a foto.');
  const side = Math.min(image.naturalWidth, image.naturalHeight);
  const sourceX = (image.naturalWidth - side) / 2;
  const sourceY = (image.naturalHeight - side) / 2;
  context.drawImage(image, sourceX, sourceY, side, side, 0, 0, dimension, dimension);
  let quality = 0.86;
  let result = canvas.toDataURL('image/jpeg', quality);
  while (estimatedDataUrlBytes(result) > MAX_SAVED_BYTES && quality > 0.46) {
    quality -= 0.08;
    result = canvas.toDataURL('image/jpeg', quality);
  }
  if (estimatedDataUrlBytes(result) > MAX_SAVED_BYTES) throw new Error('A foto não pôde ser reduzida para o limite seguro.');
  return result;
}

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result ?? ''));
    reader.onerror = () => reject(new Error('Não foi possível ler a foto.'));
    reader.readAsDataURL(file);
  });
}

function loadImage(source: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error('A imagem selecionada é inválida.'));
    image.src = source;
  });
}

function estimatedDataUrlBytes(value: string) {
  const payload = value.split(',', 2)[1] ?? '';
  return Math.ceil(payload.length * 0.75);
}
