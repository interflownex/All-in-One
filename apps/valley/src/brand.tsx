export const VALLEY_OFFICIAL_LOGO = '/assets/brand/valley-logo-official.png';
export const VALLEY_PROFILE_MODE_KEY = 'valley.profile.brand.mode.v1';
export const VALLEY_PROFILE_PHOTO_KEY = 'valley.profile.brand.photo.v1';
export const VALLEY_PROFILE_EVENT = 'valley-profile-brand-updated';

export type ValleyProfileMode = 'official' | 'personalized';

export type ValleyProfileBrand = {
  mode: ValleyProfileMode;
  photoDataUrl: string;
};

export function readValleyProfileBrand(): ValleyProfileBrand {
  const mode = window.localStorage.getItem(VALLEY_PROFILE_MODE_KEY) === 'personalized' ? 'personalized' : 'official';
  const photoDataUrl = window.localStorage.getItem(VALLEY_PROFILE_PHOTO_KEY) ?? '';
  return { mode: mode === 'personalized' && photoDataUrl ? 'personalized' : 'official', photoDataUrl };
}

export function saveValleyProfileBrand(next: ValleyProfileBrand) {
  window.localStorage.setItem(VALLEY_PROFILE_MODE_KEY, next.mode);
  if (next.photoDataUrl) window.localStorage.setItem(VALLEY_PROFILE_PHOTO_KEY, next.photoDataUrl);
  else window.localStorage.removeItem(VALLEY_PROFILE_PHOTO_KEY);
  window.dispatchEvent(new CustomEvent(VALLEY_PROFILE_EVENT));
}

export function ValleyOfficialLogo({ className = '' }: { className?: string }) {
  return <img className={className} src={VALLEY_OFFICIAL_LOGO} alt='VALLEY' draggable={false} />;
}

export function ValleyProfileMark({ mode, photoDataUrl, className = '' }: ValleyProfileBrand & { className?: string }) {
  if (mode !== 'personalized' || !photoDataUrl) return <ValleyOfficialLogo className={className} />;
  return <span className={`valley-profile-mark ${className}`.trim()} aria-label='Identidade visual personalizada do perfil VALLEY'>
    <span className='valley-profile-ring'><img src={photoDataUrl} alt='Foto do perfil' /></span>
    <strong>VALLEY</strong>
  </span>;
}
