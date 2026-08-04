import { type ChangeEvent } from 'react';

const MAX_AVATAR_BYTES = 2 * 1024 * 1024;
const ALLOWED_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp']);

export function avatarStorageKey(userId: string) {
  return `valley.profile.avatar.${userId}`;
}

export function loadProfileAvatar(userId: string) {
  return window.localStorage.getItem(avatarStorageKey(userId)) ?? '';
}

export function saveProfileAvatar(userId: string, dataUrl: string) {
  if (dataUrl) window.localStorage.setItem(avatarStorageKey(userId), dataUrl);
  else window.localStorage.removeItem(avatarStorageKey(userId));
  window.dispatchEvent(new CustomEvent('valley-profile-avatar-changed', { detail: { userId, dataUrl } }));
}

export async function readProfileAvatar(file: File) {
  if (!ALLOWED_TYPES.has(file.type)) throw new Error('Use uma imagem JPG, PNG ou WebP.');
  if (file.size > MAX_AVATAR_BYTES) throw new Error('A foto deve ter no máximo 2 MB.');
  return await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('Não foi possível ler a imagem.'));
    reader.onload = () => resolve(String(reader.result ?? ''));
    reader.readAsDataURL(file);
  });
}

export function ValleyProfileAvatar({ src, size = 'medium', label = 'Foto de perfil Valley' }: { src?: string; size?: 'small' | 'medium' | 'large'; label?: string }) {
  return <div className={`valley-profile-avatar ${size}`} role='img' aria-label={label}>
    <div className='profile-photo-disc'>{src ? <img className='profile-photo' src={src} alt='' /> : <span className='profile-photo-placeholder' aria-hidden='true'>V</span>}</div>
    <img className='valley-avatar-frame' src='/assets/brand/valley-logo-official.png' alt='' aria-hidden='true' />
    <span className='valley-avatar-wordmark'>VALLEY</span>
  </div>;
}

export function ValleyAvatarPicker({ value, onChange, onError }: { value: string; onChange: (value: string) => void; onError: (message: string) => void }) {
  const select = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      onChange(await readProfileAvatar(file));
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Não foi possível usar esta foto.');
    } finally {
      event.target.value = '';
    }
  };

  return <div className='avatar-picker'>
    <ValleyProfileAvatar src={value} size='large' />
    <div className='avatar-picker-actions'>
      <label className='secondary file-button'>Escolher foto<input type='file' accept='image/jpeg,image/png,image/webp' onChange={select} /></label>
      {value && <button className='text-button' type='button' onClick={() => onChange('')}>Usar avatar padrão</button>}
    </div>
    <small>A foto é opcional e fica dentro da moldura do perfil. A logomarca oficial e o ícone do aplicativo não são alterados.</small>
  </div>;
}
